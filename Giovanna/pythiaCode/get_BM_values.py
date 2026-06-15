import os
import re
import numpy as np

# Path containing all MG5 folders
#path = "/data1/hep-shared/HNLsFCCee/UBL/lhe/mZp70_isr"
#path = "/data1/hep-shared/HNLsFCCee/UBL/lhe/mZp50_isr"
#path = "/data1/hep-shared/HNLsFCCee/UBL/lhe/mZp70_isr"

#path = "/data1/hep-shared/HNLsFCCee/UBL/lhe/mZp30_isr2"
#path = "/data1/hep-shared/HNLsFCCee/UBL/lhe/mZp50_isr2"
#path = "/data1/hep-shared/HNLsFCCee/UBL/lhe/mZp70_isr2"

path = "/data1/hep-shared/HNLsFCCee/UBL/lhe/coupled_isr2"


folders = os.listdir(path)

print(folders)
# Use sets to keep only unique values
masses = set()
mixings = set()

# Keep the exact string representation from the folder name
#pattern = r"MG5_GRID_U1BL_mu-(\d+)-([0-9.eE+-]+)"
pattern = r"MG5_GRID_U1BL_mu-([\d.]+)-([0-9.eE+-]+)" #second run of LHE has decimal masses

for folder in folders:

    match = re.match(pattern, folder)

    if match:

        # mass as integer/float
        #mass = int(match.group(1))
        mass = float(match.group(1))
        # mixing EXACTLY as written in folder name
        mixing = match.group(2)

        masses.add(mass)
        mixings.add(mixing)

# Convert to sorted numpy arrays
mN = np.array(sorted(masses))
mixing = np.array(
    sorted(mixings, key=lambda x: float(x))
)

# Print arrays
print("mN = {" + ",".join(map(str, mN)) + "}")
print("mixing = {" + ",".join(mixing) + "}")

# Save to txt file
### APADT TO FILE
#with open("mass_mixing_isr30_2.txt", "w") as f:
#with open("mass_mixing_isr50_2.txt", "w") as f:
#with open("mass_mixing_isr70_2.txt", "w") as f:
#with open("mass_mixing_isr30.txt", "w") as f:
#with open("mass_mixing_isr50.txt", "w") as f:
#with open("mass_mixing_isr70.txt", "w") as f:

with open("mass_mixing_coupled_isr2.txt", "w") as f:
    f.write("# Unique masses\n")
    f.write("mN = {" + ",".join(map(str, mN)) + "}\n\n")
    f.write("# Unique mixings\n")
    f.write("mixing = {" + ",".join(mixing) + "}\n")

#print("Saved unique values to mass_mixing_isr70.txt")
#print("Saved unique values to mass_mixing_isr50.txt")
#print("Saved unique values to mass_mixing_isr70.txt")

#print("Saved unique values to mass_mixing_isr30_2.txt")
#print("Saved unique values to mass_mixing_isr50_2.txt")
print("Saved unique values to mass_mixing_isr70_2.txt")