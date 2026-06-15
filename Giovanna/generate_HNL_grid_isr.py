# Written by Giovanna Cottin (gfcottin@gmail.com)
# import pandas as pd
import shutil, subprocess
import pathlib
import numpy as np
#import stat 

#mN    = np.arange(5, 46, 1)
#Vlnu2 = np.logspace(-4, -20, num=41) 
#spaced grid of 41*41=1681 points
#Vlnu2 = np.logspace(-2, -20, num=41) #enalrging in mixing to catch 1mm

#new grid isr3 for contour
mN    =  np.arange(20, 35, 0.5)
Vlnu2 = np.logspace(-4, -14, 61)
#spaced grid  points 61*30=1830

#Mixing in muon sector
for mass in mN:
    mZp=mass/0.3
    for mix2 in Vlnu2:
        sqmix2 = np.sqrt(mix2) 
        with open(f"/home/gfcottin/MyGit/UBL_FCCee/MG5_gen_U1BL_mu_FCCee/coupled_isr3/MG5_gen_U1BL_mu_FCCee-{mass}-{mix2}",'w') as f:
            f.write("import model B-L-Gen_UFO\n")
            f.write("define j = g u c d s u~ c~ d~ s~\n")
            f.write("define w= w+ w-\n")
            f.write("generate e+ e- > zp > n2 n2\n") 
            f.write("output /data1/hep-shared/HNLsFCCee/UBL/lhe/coupled_isr3/MG5_GRID_U1BL_mu-"+str(mass)+"-"+str(mix2)+"\n")
            f.write("launch -i /data1/hep-shared/HNLsFCCee/UBL/lhe/coupled_isr3/MG5_GRID_U1BL_mu-"+str(mass)+"-"+str(mix2)+"\n")
            f.write("generate_events\n")
            f.write("madspin=ON\n")
            f.write("/home/gfcottin/MyGit/UBL_FCCee/MG5_cards/param_card_autoDecays.dat\n") 
            f.write("/home/gfcottin/MyGit/UBL_FCCee/MG5_cards/madSpin_card_BLmu.dat\n") 
            f.write("set nevents 10000\n")
            f.write("set lpp1 -3\n") #include ISR effects for electrons/positrons slide 46 https://ics.sgk.iwate-u.ac.jp/wp-content/uploads/2024/03/2024_T_mg5amc_lo.pdf
            f.write("set lpp2 3\n")
            f.write("set pdlabel isronlyll\n") # enable isr effects before hard scatter
            f.write("set numixing 2 2 "+str(sqmix2)+ "\n") #mixing in muon sector
            f.write("set MASS 9900032 "+str(mZp)+"\n")
            f.write("set MASS 9910014 "+str(mass)+"\n")
            f.write("set ebeam1 45.6\n")
            f.write("set ebeam2 45.6\n")
            f.write("set BLINPUTS 1 1e-04\n") # fixed U1BL coupling to 1e-4
            f.write("set time_of_flight 1e-25\n")
            f.write(f"print_results --path=/data1/hep-shared/HNLsFCCee/UBL/cross_section_results/coupled_isr3/cross_section_{mass}_{mix2}.txt --format=short")  
            f.close()

        p=subprocess.Popen(
            ["python3","bin/mg5_aMC",f"/home/gfcottin/MyGit/UBL_FCCee/MG5_gen_U1BL_mu_FCCee/coupled_isr3/MG5_gen_U1BL_mu_FCCee-{mass}-{mix2}"],
            stdout=subprocess.PIPE,
            text=True,
            cwd="/home/gfcottin/HNL_test/MG5_aMC_v3_5_5/") # aqui cambiar a tu madgraph
        p.wait()
        while (line := p.stdout.readline()) != "":
            print(line.rstrip())