import Data
import pandas as pd
import Erestrito_model
from gurobipy import*
from tabulate import tabulate
#import paralelgraph
import Paralelgraph2
import tresdgraph
import respostas
import os
import time
def main():
    disponibilidade = [[1,1,0,0,0,0,0],[1,1,1,0,0,0,0],[1,1,1,1,0,0,0],[1,1,1,1,1,0,0]]
    disponibilidade = [disponibilidade[3]]
    for disp in disponibilidade:
        dado = "Data"
        tempo,rem,MA,F,JM,DE,TE,KC,GR,carga,Pmin,Pmax,numateriais,mina,dj,\
                         materiais,massa,atv,ciclo,tciclo,teores,t,part, \
                         teores2,lsup,lmeta,mindes,maxdes,granulometrias1,\
                         linfg,lsupg,mindesg,maxdesg,granulometrias2, gran,\
                         descarga,Prod,britador,mlc,tamanho,caminhao,frota,cm,ce,comp_mina = eval(dado).data()
        resultados = {}
        result_teor = []
        result_gran = []
        peso = [1,1,1,1]

        eixox = []
        eixoy = []
        eixoz = []
        eixow1= []
        eixow2= []
        #tolerancia=[0.0,0.01,0.0245,0.0335,0.041,0.05]
        #tolerancia=[0.0,0.01,0.02,0.03,0.04,0.05]
        #tolerancia = [0.0,0.01,0.02]
        tolerancia=[0.05]

        peso = [1,1,1,1]
        XeSol = []
        XeEval = []

        for tol in tolerancia:

            start = time.perf_counter()
            print("&&&&&&&&&&&&&&&&&&&&&&")
            print("ESCAVADEIRAS = ", sum(disp))
            print("&&&&&&&&&&&&&&&&&&&&&&")
            print("TOLERANCIA = ",tol)
            print("&&&&&&&&&&&&&&&&&&&&&&")
            
            poolEval,poolSol,nObjectives = Erestrito_model.solve(tempo,rem,MA,F,JM,DE,TE,KC,GR,carga,Pmin,Pmax,numateriais,mina,dj,\
            materiais,massa,atv,ciclo,tciclo,teores,t,part, \
            teores2,lsup,lmeta,mindes,maxdes,granulometrias1,\
            linfg,lsupg,mindesg,maxdesg,granulometrias2, gran,\
            descarga,Prod,britador,mlc,tamanho,caminhao,frota,cm,ce,comp_mina,peso,tol,disp)
            XeSol.append(poolSol[0])
            XeEval.append(poolEval[0])
            end = time.perf_counter() - start
            print("Tempoo = ",end,", tolerancia = ",tol)
            
        for i in XeSol:
            somaw1 = 0
            somaw2 = 0
            somadesg = 0
            somadest = 0
            somaerem = 0
            for j in i:
                #somaw = 0
                if j[0].startswith("w"):
                    #print("Viagemmm: ",j[0])
                    if j[0].find("1]") != -1:
                        somaw1+=int(j[1])
                    if j[0].find("2]") != -1:
                        somaw2+=int(j[1])
                    
                if j[0].startswith("de_min_teor") or j[0].startswith("de_max_teor"): 
                    somadest+=0.0001*float(j[1])
                if j[0].startswith("de_min_gran") or j[0].startswith("de_max_gran"): 
                    somadesg+=0.01*float(j[1])
                if j[0].startswith("erem"):
                    somaerem+=float(j[1])
                if j[0].startswith("x"):
                    if int(j[1]) == 1:
                        print(j[0]," = ", j[1] )
                if j[0].startswith("w"):
                    if int(j[1]) >= 1:
                        print(j[0]," = ", j[1] )
                    

            eixox.append(round(somadest,3))
            eixoy.append(round(somadesg,3))
            eixoz.append(round(somaerem,1))
            eixow1.append(round(somaw1,0))
            eixow2.append(round(somaw2,0))
        def gera_arquivos_paral(eixox,eixoy,eixoz,eixow1,eixow2,dado):
            arquivos = ["Erestrito_desvios"]
            for i in arquivos:
                if os.path.exists(i+dado+str(sum(disp))+"e"+".csv"):
                    os.remove(i+dado+str(sum(disp))+"e"+".csv")
            dicionariodesvios = {"eixox":[],"eixoy":[],"eixoz":[],"eixow1":[],"eixow2":[]}
            for i in range(len(eixox)):
                dicionariodesvios["eixox"].append(eixox[i])
                dicionariodesvios["eixoy"].append(eixoy[i])
                dicionariodesvios["eixoz"].append(eixoz[i])
                dicionariodesvios["eixow1"].append(eixow1[i])
                dicionariodesvios["eixow2"].append(eixow2[i])
            fonteeixo = pd.DataFrame.from_dict(dicionariodesvios)
            fonteeixo.to_csv("Erestrito_desvios"+dado+str(sum(disp))+"e"+".csv",index=True)

        gera_arquivos_paral(eixox,eixoy,eixoz,eixow1,eixow2,dado)


        res_teor = {}
        res_gran = {}


        res_teor,res_gran,REM,Viagens1,Viagens2 = respostas.resultados(XeSol,tempo,rem,MA,F,JM,DE,TE,KC,GR,carga,Pmin,Pmax,numateriais,mina,dj,\
                         materiais,massa,atv,ciclo,tciclo,teores,t,part, \
                         teores2,lsup,lmeta,mindes,maxdes,granulometrias1,\
                         linfg,lsupg,mindesg,maxdesg,granulometrias2, gran,\
                         descarga,Prod,britador,mlc,tamanho,caminhao,frota,cm,ce,comp_mina)
        def gera_arquivos(res_teor,res_gran,REM,Viagens1,Viagens2):
            arquivos = ["_fontegran.csv","_fonteteor.csv","_fonterem.csv","_fonteviagens1.csv","_fonteviagens2.csv"]
            for i in arquivos:
                if os.path.exists("Erestrito"+dado+str(sum(disp))+"e"+i):
                    os.remove("Erestrito"+dado+str(sum(disp))+"e"+i)
            fonteteor = pd.DataFrame.from_dict(res_teor)
            fontegran = pd.DataFrame.from_dict(res_gran)
            fonterem = pd.DataFrame.from_dict(REM)
            fonteviagens1 = pd.DataFrame.from_dict(Viagens1)
            fonteviagens2 = pd.DataFrame.from_dict(Viagens2)
            fonteteor.to_csv("Erestrito"+dado+str(sum(disp))+"e"+"_fonteteor.csv",index=True)
            fontegran.to_csv("Erestrito"+dado+str(sum(disp))+"e"+"_fontegran.csv",index=True)
            fonterem.to_csv("Erestrito"+dado+str(sum(disp))+"e"+"_fonterem.csv",index=True)
            fonteviagens1.to_csv("Erestrito"+dado+str(sum(disp))+"e"+"_fonteviagens1.csv",index=True)
            fonteviagens2.to_csv("Erestrito"+dado+str(sum(disp))+"e"+"_fonteviagens2.csv",index=True)

        gera_arquivos(res_teor,res_gran,REM,Viagens1,Viagens2)
    



if __name__ == "__main__":
    main()
