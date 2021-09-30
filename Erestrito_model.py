from gurobipy import*
from tabulate import tabulate
#import paralelgraph
import Paralelgraph2
import tresdgraph
import timeit

def solve(tempo,rem,MA,F,JM,DE,TE,KC,GR,carga,Pmin,Pmax,numateriais,mina,dj,\
                 materiais,massa,atv,ciclo,tciclo,teores,t,part, \
                 teores2,lsup,lmeta,mindes,maxdes,granulometrias1,\
                 linfg,lsupg,mindesg,maxdesg,granulometrias2, gran,\
                 descarga,Prod,britador,mlc,tamanho,caminhao,frota,cm,ce,comp_mina,peso,to,disp):

    
    poolSol = []
    poolEval = []
    result_ob = []
    m = Model("Produção")
    x = m.addVars(F,MA,JM,vtype = GRB.BINARY,name = "x")
    xf = m.addVars(F,JM,vtype = GRB.BINARY,name = "x")
    p = m.addVars(F,MA,DE,name = "p")
    w = m.addVars(DE,F,MA,KC,vtype = GRB.INTEGER,name = "w")
    #w = m.addVars(DE,F,MA,KC,name = "w")
    eprodi = m.addVars(DE,name = "eprodi")
    eprodn = m.addVars(DE,name = "eprodn")
    de_max_gran = m.addVars(DE,GR,name = "de_max_gran")
    de_min_gran = m.addVars(DE,GR,name = "de_min_gran")
    de_max_teor = m.addVars(DE,TE,name = "de_max_teor")
    de_min_teor = m.addVars(DE,TE,name = "de_min_teor")
    erem = m.addVar(name = "erem")
    FK = m.addVars(DE,F,MA,KC, name = "FK")
    tempototal = m.addVar(name = "tempototal")


    m.setObjectiveN(0.0001*sum(de_min_teor.sum(d,t) + de_max_teor.sum(d,t) for d in DE if britador[d] == 1 for t in TE),0,priority = 4,weight = peso[0])
    
    m.setObjectiveN(0.01*sum(de_min_gran.sum(d,g) + de_max_gran.sum(d,g)  for d in DE if britador[d] == 1 for g in GR),1,priority = 3, weight = peso[1])
    
    #m.setObjectiveN(erem[0]/(rem*(Prod[1]+Prod[2])*tempo),2,priority = 2, weight = peso[2])
    m.setObjectiveN(erem,2,priority = 2, weight = peso[2])
    m.setObjectiveN(w.sum(),3,priority = 1, weight = peso[3])
    #m.setObjectiveN(sum(w[d,f,i,k]/cm[k] for d in DE for f in F for i in MA for k in KC),3,priority = 1, weight = peso[3])

    m.NumObj = 4
    #m.set(MipGap,0.01)
    #m.Params.timeLimit = 3600
    #m.Params.Mipgap = 0.0019
    m.Params.Cuts = 0
    #m.Params.timeLimit = 3600
    #m.Params.PoolSearchMode = 0
    ##m.Params.PoolSolutions = 1
    ##m.Params.SolutionNumber = 1
    #Restrições de Alocação:
    #m.Params.Heuristics = 0.2
    
    #2resaloc1 = m.addConstrs((xf.sum(f,"*") <= 1 for f in F),"resaloc1")
    #2resaloc2 = m.addConstrs((xf.sum("*",j) <= 1*disp[j-1] for j in JM),"resaloc2")
    resaloc1 = m.addConstrs((x.sum("*","*",j)<= 4*disp[j-1] for j in JM),"resaloc1")
    #2resaloc2 = m.addConstrs((x[f,i,j] - xf[f,j] == 0 for f in F for i in MA for j in JM),"resaloc2")
    resaloc2 = m.addConstrs((x.sum(f,i,"*")<= 1 for f in F for i in MA),"resaloc2")
    resaloc3 = m.addConstrs((x[f,i,j] - x[f,t,j] == 0 for f in F for i in MA for t in MA for j in JM),"resaloc3")
    resaloc4 = m.addConstrs((x[f,i,j] == 0 for f in F for i in MA for i in MA for j in JM if comp_mina[j] != mina[f] and comp_mina[j] !=0),"resaloc3")

    #Restrições de Massa por Usina

    resmass1 = m.addConstrs((p.sum(f,i,"*") <= massa[f,i]*x.sum(f,i,"*") for f in F for i in MA if (f,i) in materiais),"resmass1")
    resmass2 = m.addConstrs((sum(p[f,i,d]*atv[f,i] for f in F for i in MA if (f,i) in materiais ) >= (0.99*Prod[d]*tempo) for d in DE if (britador[d] == 1)),"resmass2")
    resmass3 = m.addConstrs((sum(p[f,i,d]*atv[f,i] for f in F for i in MA if (f,i) in materiais) <= (1.01*Prod[d]*tempo) for d in DE if (britador[d] == 1)),"resmass3")
    resmass4 = m.addConstrs((p[f,i,d] == sum((atv[f,i]*cm[k] + (1-atv[f,i])*ce[k])*w[d,f,i,k] for k in KC) for f in F for i in MA for d in DE if (f,i) in materiais),"resmass4")
    resmass5 = m.addConstrs((p.sum(f,"*","*") <=sum(x[f,i,j]*Pmax[j]*tempo/numateriais[f] for j in JM for i in MA) for f in F),"resmass5")

    

    #Restrições do número de viagens
    #resnumv3 = m.addConstr((FK.sum("*","*","*",1) <= frota[1]),"resnumv3")
    #resnumv3 = m.addConstr((FK.sum("*","*","*",2) <= frota[2]),"resnumv3")
    #resnumv1 = m.addConstrs((w[d,f,i,k] <= sum(60*x[f,i,j] for j in JM)for d in DE for k in KC for f in F for i in MA),"resnumv1")
    resnumv1 = m.addConstrs((w[d,f,i,k]  <= ((60/tciclo[d,f,i,k])*FK[d,f,i,k]*tempo) for k in KC for f in F for i in MA for d in DE if (d,f,i,k) in ciclo),"resnumv1")
    resnumv1 = m.addConstrs((w[d,f,i,k]  <= 0 for k in KC for f in F for i in MA for d in DE if (d,f,i,k) not in ciclo),"resnumv1")
    resnumv3 = m.addConstrs((FK.sum("*","*","*",k) <= frota[k] for k in KC),"resnumv3")
    resnumv4 = m.addConstrs((w.sum(d,f,i,"*") == 0 for d in DE for f in F for i in MA if britador[d] == 1 and atv[f,i] == 0),"resnum4")


    #Restrições de granulometria
  
    '''
    resgran2 = m.addConstrs((sum(gran[f,i,g]*atv[f,i]*p[f,i,d] for f in F for i in MA if (f,i,g) in granulometrias2 ) - de_max_gran[d,g] + de_min_gran[d,g] ==
                            linfg[d,g]*sum(atv[f,i]*p[f,i,d] for f in F for i in MA if (f,i) in materiais) for d in DE \
                             if britador[d] == 1 for g in GR if linfg[d,g] > 0),"resgran2")
    '''

    resgran2 = m.addConstrs((sum(gran[f,i,g]*atv[f,i]*p[f,i,d] for f in F for i in MA if (f,i,g) in granulometrias2 if britador[d] == 1) - de_max_gran[d,g] + de_min_gran[d,g] ==
                            linfg[d,g]*sum(atv[f,i]*p[f,i,d] for f in F for i in MA if (f,i) in materiais if britador[d] == 1) for d in DE if britador[d] == 1 for g in GR\
                             ),"resgran2")


                                        
            

    

    #Restrições de teores

    #resteor1 = m.addConstrs((sum(t[f,i,j]*atv[f,i]*p[f,i,d]*part[f,i,j] for f in F for i in MA if (f,i) in materiais) - de_max_teor[d,j] + de_min_teor[d,j] == \
     #        linf[d,j]*sum(atv[f,i]*p[f,i,d]*part[f,i,j] for f in F for i in MA if (f,i) in materiais) for d in DE if britador[d] == 1 for j in TE),"resteor1")

    resteor2 = m.addConstrs((sum(t[f,i,j]*atv[f,i]*p[f,i,d]*part[f,i,j] for f in F for i in MA if (f,i,j) in teores) - de_max_teor[d,j] <=
                             (1+to)*lmeta[d,j]*sum(atv[f,i]*p[f,i,d]*part[f,i,j] for f in F for i in MA if (f,i,j) in teores) for d in DE if britador[d] == 1 for j in TE if lmeta[d,j] > 0),"resteor2")

    resteor3= m.addConstrs((sum(t[f,i,j]*atv[f,i]*p[f,i,d]*part[f,i,j] for f in F for i in MA if (f,i,j) in teores) + de_min_teor[d,j] >=
                             (1-to)*lmeta[d,j]*sum(atv[f,i]*p[f,i,d]*part[f,i,j] for f in F for i in MA if (f,i,j) in teores) for d in DE if britador[d] == 1 for j in TE if lmeta[d,j] > 0),"resteor1")

    #Restrição de rem

    resrem = m.addConstr(sum((1-atv[f,i])*p[f,i,d] for f in F for i in MA for d in DE if (f,i) in materiais) + erem >=
                         rem*sum(atv[f,i]*p[f,i,d] for f in F for i in MA for d in DE if (f,i) in materiais), "restrem")

    #resrep = m.addConstr((tempototal == sum(w[d,f,i,k]*tciclo[d,f,i,k] for d in DE for f in F for i in MA for k in KC\
    #                                        if (d,f,i,k) in ciclo)),"tempototall")


    env0 = m.getMultiobjEnv(0)
    env1 = m.getMultiobjEnv(1)
    env2 = m.getMultiobjEnv(2)
    env3 = m.getMultiobjEnv(3)
    env0.setParam('TimeLimit',3600)
    env1.setParam('TimeLimit',3600)
    env2.setParam('TimeLimit',3600)
    env3.setParam('TimeLimit',3600)
    '''
    Disponibilidade = 4:
    if to == 0:
     #   env0.setParam('Mipgap',0.0001)
     #   env1.setParam('Mipgap',0.0001)
        env2.setParam('Mipgap',0.0073)
     #   env3.setParam('Mipgap',0.0009)
    #elif to == 0.01:
    #    env0.setParam('Mipgap',0.0001)
    #    env1.setParam('Mipgap',0.0001)
    #    env2.setParam('Mipgap',0.0001)
    #    env3.setParam('Mipgap',0.0001)

    if to == 0.02:
    #    env0.setParam('Mipgap',0.0001)
    #    env1.setParam('Mipgap',0.0001)
        env2.setParam('Mipgap',0.057)
        env3.setParam('Mipgap',0.078)
    '''
    
    '''
        if to == 0:
         #   env0.setParam('Mipgap',0.0001)
         #   env1.setParam('Mipgap',0.0001)
            env2.setParam('Mipgap',0.0073)
         #   env3.setParam('Mipgap',0.0009)
        #elif to == 0.01:
        #    env0.setParam('Mipgap',0.0001)
        #    env1.setParam('Mipgap',0.0001)
        #    env2.setParam('Mipgap',0.0001)
        #    env3.setParam('Mipgap',0.0001)
        elif to == 0.02:
        #    env0.setParam('Mipgap',0.0001)
        #    env1.setParam('Mipgap',0.0001)
            env2.setParam('Mipgap',0.057)
            env3.setParam('Mipgap',0.078)

    
    #if to == 0:
     #   env0.setParam('Mipgap',0.0001)
     #   env1.setParam('Mipgap',0.0001)
     #  env2.setParam('Mipgap',0.0073)
     #   env3.setParam('Mipgap',0.0009)

    #if to == 0.02:
    #    env0.setParam('Mipgap',0.0019)
    #    env1.setParam('Mipgap',0.0019)
    #    env2.setParam('Mipgap',0.014)
    #    env3.setParam('Mipgap',0.14)
        #env3.setParam('Cuts',0)
    if to == 0.03:
        #env0.setParam('Mipgap',0.0019)
        env1.setParam('Mipgap',0.0019)
        #env2.setParam('Mipgap',0.0018)
        #env3.setParam('Mipgap',0.128)
    '''

            
    

    m.optimize()

    x = m.getVars()
    nSolutions = m.SolCount
    nObjectives = m.NumObj
    solutions = []
    obj = m.getObjective(3)
    print("Número de soluções igual a: ",nSolutions)
    print("Número de variáveis: ",m.NumVars)
    print("Número de variáveis binárias: ",m.NumBinVars)
    print("Número de variáveis inteiras: ",m.NumIntVars)
    print("Número de resitrções: ", m.NumConstrs)
    print("Funçao objetivo 4: ", obj.getValue())
    m.discardMultiobjEnvs()

        

            
            
        
        

    
    
    for s in range(nSolutions):
        # Set qual solução será informada:
        m.params.SolutionNumber = s
        #Imprime o valor da solução para cada função objetivo:
        print("SOLUÇÃO ", s, ":", end = ' ')
        print("Tolerancia: ",to)
        poolEval.append([])
        poolSol.append([])
        for o in range(nObjectives):
            #Configura qual objetivo será informado:
            m.params.ObjNumber = o
            poolEval[len(poolEval)-1].append(m.ObjNVal)
            #Imprime o respectivo valor da função objetivo:
        #    print(" ", m.ObjNVal,end = " ")

        #Imprime as primeiras 3 variáveis de decisão:
        n = len(x)
        for j in range(n):
            poolSol[len(poolSol)-1].append((x[j].VarName,x[j].Xn))
    del(m)
    #print("PoolSol =",poolSol)
    '''
    for v in m.getVars():
        if (abs(v.x)>1e-6):
            print(v.varName,v.x)
        resultados.update({v.varName:v.x})
    '''
    # Para cada solução, imprime o valor das 3 primeiras variáveis e
    # o valor de cada função objetivo

    
    
    return(poolEval,poolSol,nObjectives)
    
