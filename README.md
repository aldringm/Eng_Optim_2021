# Eng_Optim_2021

Orientations:

To run the model, download the file Data.py and Model.py
The scenarios described in the paper can be reproduced by setting the variable to and the variable disp inside the Data.py file
For example, to run the scenario with 2 excavators and tolerance equal to 0, assign disp = availability [0] and to = tolerance[0].

Below are the corresponding labels between the manuscript and the template file. 

Sets, parameters and variables no modelo:

Sets:
Trucks:              manuscript = mathcal(T), model file = KC;
Excavators:          manuscript = mathcal(E), model file = JM;
Discharges:          manuscript = mathcal(D), model file = DE;
Fronts:              manuscript = mathcal(F), model file = F;
Elements:            manuscript = mathcal(G), model file = TE;
Particle size range: manuscript = mathcal(S), model file = GR;
Materials:           manuscritp = mathcal(M), model file = MA;


Parameters:

Type of each discharge:            manuscript = DT, model file = DT;
Mass of material in each front:    manuscript = MM, model_file = MM;
Extraction rate of excavators:     manuscript = ER, model_file = ER;
Shift Duration:                    manuscript = SD, model_file = SD;
Material type:                     manuscript = MT, model_file = MT;
Trucks capacities                  manuscript = TC, model_file = TC;
Cycle times:                       manuscript = CT, model_file = CT;
Number of available trucks:        manuscript = N,  model_file = N;
Production rate of ore discharges: manuscript = DR, model_file = DR;
Grade targets:                     manuscript = GT, model_file = GT;
Materials grades in fronts:        manuscript = GM, model_file = GM;
Percentage of particle size range: manuscript = SP, model_file = SP;
Allowable tolerance:               manuscript = epsilon, model_file = to;
Target for the proportion of ore in the particle size range: manuscript = ST, model_file = ST;
Target for the stripping ratio:    manuscritp = WT, model_file = WT;
Number of materials per front:     manuscript = NM, model_file = 4;

Decision variables:

manuscript = x,    model_file = x;
manuscript = w,    model_file = w;
manuscript = gd^+, model_file = de_max_teor;
manuscript = gd^-, model_file = de_min_teor;
manuscript = sd^+, model_file = de_max_gra;
manuscript = sd^-, model_file = de_min_gra;
manuscript = sd^-, model_file = de_min_gra;
manuscript = srd,  model_file = erem;
manuscript = un,   model_file = FK;
