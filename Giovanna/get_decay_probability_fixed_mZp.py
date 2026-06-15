################################
# Extracting HNL kinematics
# Computing decay probabilities
# Computing expected event yields
# gfcottin@uc.cl
################################

import os
import numpy as np
import pandas as pd

# ==========================================================
# INPUTS
# ==========================================================

path = "/data1/hep-shared/HNLsFCCee/UBL"

#input_dirs = [
#    f"{path}/pythiaOutput/mZp70_isr",
#    f"{path}/pythiaOutput/mZp70_isr2",
#]

input_dirs = [
    f"{path}/pythiaOutput/coupled_isr2",
]

#cross_section_file = (
#    "/home/gfcottin/MyGit/UBL_FCCee/master_csv/csv/"
#    "Master_cross_section_decay_mZp70.csv"
#)

cross_section_file = (
    "/home/gfcottin/MyGit/UBL_FCCee/master_csv/csv/"
    "Master_cross_section_decay_coupled_isr2.csv"
)

output_file = (
    "/home/gfcottin/MyGit/UBL_FCCee/master_csv/csv/"
    "MasterData_coupled_isr2.csv"
)

# ==========================================================
# PYTHIA OUTPUT COLUMNS
# ==========================================================

decay_columns = [
    "HNLmass",
    "HNLmass2",
    "Vlnu2",
    "HNLdecayLength",
    "HNLgamma",
    "HNLbeta_z",
    "HNLe",
    "HNLp",
    "HNLbeta",
    "HNLeta",
    "HNLtheta",
    "HNLphi",
]

# ==========================================================
# READ ALL PYTHIA FILES
# ==========================================================

dfs = []

for directory in input_dirs:

    print(f"Reading directory: {directory}")

    for filename in os.listdir(directory):

        filepath = os.path.join(directory, filename)

        try:

            tmp = pd.read_csv(
                filepath,
                header=None,
                sep=r"\s+"
            )

            tmp.columns = decay_columns

            dfs.append(tmp)

        except Exception as e:

            print(f"Failed: {filepath}")
            print(e)

if len(dfs) == 0:
    raise RuntimeError("No Pythia files were successfully read.")

df = pd.concat(dfs, ignore_index=True)

print("Total HNL entries:", len(df))

# ==========================================================
# READ CROSS SECTION / DECAY TABLE
# ==========================================================

df_cs = pd.read_csv(cross_section_file)

df_cs = df_cs.rename(columns={
    "mass [GeV]": "HNLmass",
    "VlN2": "Vlnu2",
    "sigma(ee->Z'->NN) [pb]": "crossNN",
    "sigma(ee->Z'->NN->mumujjjj) [pb]": "crossALL"
})

# ==========================================================
# MERGE
# ==========================================================

df = pd.merge(
    df,
    df_cs,
    on=["HNLmass", "Vlnu2"],
    how="left"
)

print("\nColumns after merge:\n")
print(df.columns)

print("\nMissing values after merge:\n")
print(
    df[[
        "crossNN",
        "crossALL",
        "GammaZp",
        "BRZpNN",
        "GammaN"
    ]].isna().sum()
)

# ==========================================================
# CTAU
# ==========================================================

# GammaN = 3e11 * 6.581e-25 / ctau(mm)

df["HNLctau"] = (3e11 * 6.581e-25) / df["GammaN"]

# beta_z * gamma * ctau

df["decayLength_mm_z"] = (df["HNLbeta_z"]*df["HNLgamma"]*df["HNLctau"])

# ==========================================================
# IDEA DECAY PROBABILITY
# ==========================================================

R_I = 17.0      # mm
R_O = 340.0     # mm
L_D = 1050.0    # mm

tan_theta = np.tan(df["HNLtheta"])

L1 = (R_I / tan_theta).abs()
L1[L1 > L_D] = 0

L2 = (R_O / tan_theta).abs()
L2[L2 > L_D] = L_D
L2 = L2 - L1

df["decay_Probability_IDEA"] = (
    np.exp(-L1 / df["HNLdecayLength"])
    * (1.0 - np.exp(-L2 / df["HNLdecayLength"]))
)

df["decay_Probability_IDEA_z"] = (
    np.exp(-L1 / df["decayLength_mm_z"])
    * (1.0 - np.exp(-L2 / df["decayLength_mm_z"]))
)

# ==========================================================
# PROTECTION AGAINST BAD EVENTS
# ==========================================================

mask_theta = (tan_theta == 0)
mask_eta = (np.abs(df["HNLeta"]) >= 2.5)

df.loc[mask_theta, "decay_Probability_IDEA"] = 0
df.loc[mask_eta, "decay_Probability_IDEA"] = 0

df.loc[mask_theta, "decay_Probability_IDEA_z"] = 0
df.loc[mask_eta, "decay_Probability_IDEA_z"] = 0

# ==========================================================
# GROUP BY MASS AND MIXING
# ==========================================================

gb = df.groupby(["HNLmass", "Vlnu2"])

gdf = gb.first()

gdf["decay_Probability_IDEA"] = (
    gb["decay_Probability_IDEA"].mean()
)

gdf["average_decayLenght_mm"] = (
    gb["HNLdecayLength"].mean()
)

gdf["decay_Probability_IDEA_z"] = (
    gb["decay_Probability_IDEA_z"].mean()
)

gdf["average_decayLength_mm_z"] = (
    gb["decayLength_mm_z"].mean()
)

gdf.reset_index(inplace=True)

# ==========================================================
# KEEP ONLY USEFUL COLUMNS
# ==========================================================

gdf = gdf[[
    "HNLmass",
    "Vlnu2",
    "GammaZp",
    "BRZpNN",
    "GammaN",
    "HNLctau",
    "crossNN",
    "crossALL",
    "average_decayLenght_mm",
    "average_decayLength_mm_z",
    "decay_Probability_IDEA",
    "decay_Probability_IDEA_z"
]]

# ==========================================================
# EXPECTED EVENTS
# ==========================================================

FCCeeLumi1 = 150.0   # ab^-1

# 1 pb = 1e6 ab

gdf["N_DecayIDEALumi1"] = (
    gdf["crossALL"]
    * gdf["decay_Probability_IDEA"]
    * 1e6
    * FCCeeLumi1
)

gdf["N_DecayIDEALumi1_z"] = (
    gdf["crossALL"]
    * gdf["decay_Probability_IDEA_z"]
    * 1e6
    * FCCeeLumi1
)

# ==========================================================
# SORT
# ==========================================================

gdf = gdf.sort_values(
    by=["HNLmass", "Vlnu2"]
)

# ==========================================================
# SAVE
# ==========================================================

gdf.to_csv(output_file, index=False)

print("\nSaved:")
print(output_file)

print("\nRows:", len(gdf))

print("\nPreview:")
print(gdf.head())