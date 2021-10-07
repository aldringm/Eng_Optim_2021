from gurobipy import*
import Data

#IMPORT OF PARAMETERS DATA
SD,WT,MA,F,JM,DE,TE,KC,GR,carga,ER,numateriais,mina,dj,\
                 materiais,MM,MT,ciclo,CT,teores,GM,SP, \
                 teores2,GT,mindes,maxdes,granulometrias1,\
                 ST,mindesg,maxdesg,granulometrias2, gran,\
                 descarga,DR,DT,mlc,tamanho,caminhao,N,TC,ce,comp_mina,to,disp = Data.data()


#DECISION VARIABLE DECLARATION
m = Model("Produção")
x = m.addVars(F,MA,JM,vtype = GRB.BINARY,name = "x")
w = m.addVars(DE,F,MA,KC,vtype = GRB.INTEGER,name = "w")
eprodi = m.addVars(DE,name = "eprodi")
eprodn = m.addVars(DE,name = "eprodn")
de_max_gran = m.addVars(DE,GR,name = "de_max_gran")
de_min_gran = m.addVars(DE,GR,name = "de_min_gran")
de_max_teor = m.addVars(DE,TE,name = "de_max_teor")
de_min_teor = m.addVars(DE,TE,name = "de_min_teor")
erem = m.addVar(name = "erem")
FK = m.addVars(DE,F,MA,KC, name = "FK")
NM=4

#OBJETIVE FUNCTIONS
m.NumObj = 4
m.setObjectiveN(sum(de_min_teor.sum(d,t) + de_max_teor.sum(d,t) for d in DE if DT[d] == 1 for t in TE),0,priority = 4)
m.setObjectiveN(sum(de_min_gran.sum(d,g) + de_max_gran.sum(d,g)  for d in DE if DT[d] == 1 for g in GR),1,priority = 3)
m.setObjectiveN(erem,2,priority = 2)
m.setObjectiveN(w.sum(),3,priority = 1)

# MILP SET PARAMETERS
m.Params.timeLimit = 3600

# ESCAVATORS ASSIGNMENT CONSTRAINTS:
Equation5= m.addConstrs((x.sum(f,i,"*")<= 1 for f in F for i in MA),"resaloc1")
Equation6 = m.addConstrs((x.sum("*","*",j)<= 4*disp[j-1] for j in JM),"resaloc2")
Equation7 = m.addConstrs((x[f,i,j] - x[f,t,j] == 0 for f in F for i in MA for t in MA for j in JM),"resaloc3")

#MASS EXTRACTION CONSTRAINTS:

Equation8 = m.addConstrs((sum(TC[k]*w[d,f,i,k] for k in KC for d in DE) <= MM[f,i]*x.sum(f,i,"*") for f in F for i in MA if (f,i) in materiais),"resmass1")
Equation9 = m.addConstrs((NM*sum(TC[k]*w[d,f,i,k] for k in KC for i in MA for d in DE if (f,i) in materiais) <= sum(x[f, i, j] * ER[j] * SD  for j in JM for i in MA) for f in F), "resmass2")

# NUMBER OF TRIPS BETWEEN FRONTS AND DISCHARGES CONSTRAINTS:

Equation10 = m.addConstrs((w[d,f,i,k]  <= ((60/CT[d,f,i,k])*FK[d,f,i,k]*SD) for k in KC for f in F for i in MA for d in DE if (d,f,i,k) in ciclo),"resnumv1")
Equation11 = m.addConstrs((FK.sum("*","*","*",k) <= N[k] for k in KC),"resnumv3")

#PLANTS CAPACTITIES CONSTRAINTS:

Equation12 = m.addConstrs((sum(TC[k]*w[d,f,i,k]*MT[f,i] for k in KC for f in F for i in MA if (f,i) in materiais ) >= (0.99*DR[d]*SD) for d in DE if (DT[d] == 1)),"resmass2")
Equation13 = m.addConstrs((sum(TC[k]*w[d,f,i,k]*MT[f,i] for k in KC for f in F for i in MA if (f,i) in materiais ) <= (1.01*DR[d]*SD) for d in DE if (DT[d] == 1)),"resmass3")

#GRADES CONSTRAINTS:

Equation14 = m.addConstrs((sum(GM[f,i,j]*MT[f,i]*sum(TC[k]*w[d,f,i,k]for k in KC)*SP[f,i,j] for f in F for i in MA if (f,i,j) in teores) - de_max_teor[d,j] <=
                             (1+to)*GT[d,j]*sum(MT[f,i]*sum(TC[k]*w[d,f,i,k]for k in KC)*SP[f,i,j] for f in F for i in MA if (f,i,j) in teores) for d in DE if DT[d] == 1 for j in TE if GT[d,j] > 0),"resteor2")

Equation15= m.addConstrs((sum(GM[f,i,j]*MT[f,i]*sum(TC[k]*w[d,f,i,k]for k in KC)*SP[f,i,j] for f in F for i in MA if (f,i,j) in teores) + de_min_teor[d,j] >=
                             (1-to)*GT[d,j]*sum(MT[f,i]*sum(TC[k]*w[d,f,i,k]for k in KC)*SP[f,i,j] for f in F for i in MA if (f,i,j) in teores) for d in DE if DT[d] == 1 for j in TE if GT[d,j] > 0),"resteor1")

#PARTICLE SIZE RANGE CONSTRAINTS:

Equation16 = m.addConstrs((sum(gran[f,i,g]*MT[f,i]*sum(TC[k]*w[d,f,i,k]for k in KC) for f in F for i in MA if (f,i,g) in granulometrias2 if DT[d] == 1) - de_max_gran[d,g] + de_min_gran[d,g] ==
                            ST[d,g]*sum(MT[f,i]*sum(TC[k]*w[d,f,i,k]for k in KC) for f in F for i in MA if (f,i) in materiais if DT[d] == 1) for d in DE if DT[d] == 1 for g in GR\
                             ),"resgran2")

#STRIPPING RATIO CONSTRAINT:

Equation17= m.addConstr(sum((1-MT[f,i])*sum(TC[k]*w[d,f,i,k]for k in KC) for f in F for i in MA for d in DE if (f,i) in materiais) + erem >= WT*sum(MT[f,i]*sum(TC[k]*w[d,f,i,k]for k in KC) for f in F for i in MA for d in DE if (f,i) in materiais), "restrem")

m.optimize()      
