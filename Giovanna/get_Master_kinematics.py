################################
# Extracting HNL kinematics
# gfcottin@uc.cl
################################

import os
import pandas as pd
import numpy as np

path = "/data1/hep-shared/HNLsFCCee/UBL"

# =========================================================
# COLUMNS OF PYTHIA OUTPUT FILES
# =========================================================

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
    "HNLphi"
]

# =========================================================
# LOOP OVER ALL Z' MASSES
# =========================================================

for mzp in [30, 50, 70]:

    print("\n" + "=" * 70)
    print(f"Processing mZp = {mzp}")
    print("=" * 70)

    # -----------------------------------------------------
    # PYTHIA DIRECTORIES
    # -----------------------------------------------------

    dir1 = f"{path}/pythiaOutput/mZp{mzp}_isr"
    dir2 = f"{path}/pythiaOutput/mZp{mzp}_isr2"

    files1 = os.listdir(dir1)
    files2 = os.listdir(dir2)

    df_decay = []

    # -----------------------------------------------------
    # READ ISR
    # -----------------------------------------------------

    for f in files1:

        fullfile = os.path.join(dir1, f)

        try:
            ff = pd.read_csv(
                fullfile,
                header=None,
                delim_whitespace=True
            )

            ff.columns = decay_columns
            df_decay.append(ff)

        except Exception as e:
            print(f"[FAILED ISR ] {f}")
            print(e)

    # -----------------------------------------------------
    # READ ISR2
    # -----------------------------------------------------

    for f in files2:

        fullfile = os.path.join(dir2, f)

        try:
            ff = pd.read_csv(
                fullfile,
                header=None,
                delim_whitespace=True
            )

            ff.columns = decay_columns
            df_decay.append(ff)

        except Exception as e:
            print(f"[FAILED ISR2] {f}")
            print(e)

    # -----------------------------------------------------
    # CONCATENATE ALL EVENTS
    # -----------------------------------------------------

    if len(df_decay) == 0:
        print(f"No files found for mZp={mzp}")
        continue

    df_decay = pd.concat(df_decay, ignore_index=True)

    print(f"Total events loaded: {len(df_decay):,}")

    # -----------------------------------------------------
    # LOAD CROSS SECTION / DECAY INFO
    # -----------------------------------------------------

    decayinfo_file = (
        f"/home/gfcottin/MyGit/UBL_FCCee/master_csv/csv/"
        f"Master_cross_section_decay_mZp{mzp}.csv"
    )

    df_decayinfo = pd.read_csv(decayinfo_file)

    # rename to match event dataframe

    df_decayinfo = df_decayinfo.rename(columns={
        "mass [GeV]": "HNLmass",
        "VlN2": "Vlnu2"
    })

    print(f"Grid points in decay table: {len(df_decayinfo)}")

    # -----------------------------------------------------
    # MERGE
    # -----------------------------------------------------

    df = pd.merge(
        df_decay,
        df_decayinfo,
        on=["HNLmass", "Vlnu2"],
        how="left"
    )

    print(f"Rows after merge: {len(df)}")

    # -----------------------------------------------------
    # COMPUTE ctau
    # -----------------------------------------------------

    # GammaN [GeV]
    # ctau [mm]

    df["HNLctau"] = (
        3.0e11 * 6.581e-25
    ) / df["GammaN"]

    # beta_z * gamma * ctau

    df["decayLength_mm_z"] = (
        df["HNLbeta_z"]
        * df["HNLgamma"]
        * df["HNLctau"]
    )

    # -----------------------------------------------------
    # CHECK MISSING VALUES
    # -----------------------------------------------------

    missing_gamma = df["GammaN"].isna().sum()

    if missing_gamma > 0:
        print(
            f"WARNING: {missing_gamma} events have "
            f"missing GammaN after merge"
        )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    output_file = (
        f"/home/gfcottin/MyGit/UBL_FCCee/master_csv/"
        f"csv_large/MasterData_kinematics_mZp{mzp}.csv"
    )

    df.to_csv(output_file, index=False)

    print(f"Saved:")
    print(output_file)

    print(df.columns)
    print(df.head())

print("\nFinished all mZp points.")