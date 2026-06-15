import os
import re
import pandas as pd

# =========================================================
# PARSE folder name: MG5_GRID_U1BL_mu-17-3.98e-19
# =========================================================
def parse_folder_name(folder_name):
    try:
        tail = folder_name.split("mu-")[1]
        mass_str, mixing_str = tail.split("-", 1)
        return float(mass_str), float(mixing_str)
    except Exception:
        return None, None


# =========================================================
# PARSE BANNER (ROBUST MG5 VERSION)
# =========================================================
def parse_banner(filepath):

    sigma_prod = None
    sigma_decay = None
    GammaZp = None
    BRZpNN = None
    GammaN = None

    inside_init = False
    init_lines = []

    inside_Zp_block = False

    with open(filepath, "r") as f:
        lines = f.readlines()

    for line in lines:

        parts = line.strip().split()

        # -------------------------------------------------
        # DECAY BLOCK
        # -------------------------------------------------
        if len(parts) >= 3 and parts[0] == "DECAY":

            if parts[1] == "9900032":
                GammaZp = float(parts[2])
                inside_Zp_block = True
            else:
                inside_Zp_block = False

            if parts[1] == "9910014":
                GammaN = float(parts[2])

        # BR(Z' -> NN)
        if inside_Zp_block and len(parts) >= 4:
            if parts[2] == "9910014" and parts[3] == "9910014":
                BRZpNN = float(parts[0])

        # -------------------------------------------------
        # sigma_prod (Integrated weight)
        # -------------------------------------------------
        if "Integrated weight" in line:
            m = re.search(r":\s*([0-9.eE+-]+)", line)
            if m:
                sigma_prod = float(m.group(1))

        # -------------------------------------------------
        # sigma_decay (<init> block)
        # -------------------------------------------------
        if "<init>" in line:
            inside_init = True
            continue

        if "</init>" in line:
            inside_init = False
            continue

        if inside_init:
            parts_f = []
            for p in parts:
                try:
                    parts_f.append(float(p))
                except:
                    continue

            # THIS IS THE CORRECT MG5 LOGIC:
            # first physical line in init block has small positive weight
            if len(parts_f) >= 3:
                if parts_f[0] > 0 and parts_f[0] < 1e-3:
                    sigma_decay = parts_f[0]
                    inside_init = False  # stop after first valid line


    # =========================================================
    # FIX: kinematically closed channel
    # =========================================================
    if BRZpNN is None:
        BRZpNN = 0.0

    return sigma_prod, sigma_decay, GammaZp, BRZpNN, GammaN


# =========================================================
# INPUT FOLDERS
# =========================================================
base_dirs = [
    "/data1/hep-shared/HNLsFCCee/UBL/lhe/coupled_isr2/"
    #,"/data1/hep-shared/HNLsFCCee/UBL/lhe/coupled_isr2/",
]

data = []

# =========================================================
# LOOP OVER ALL FOLDERS
# =========================================================
for base_dir in base_dirs:

    if not os.path.exists(base_dir):
        print(f"[WARNING] Missing: {base_dir}")
        continue

    for folder in os.listdir(base_dir):

        if not folder.startswith("MG5_GRID_U1BL_mu-"):
            continue

        full_path = os.path.join(base_dir, folder)

        if not os.path.isdir(full_path):
            continue

        mass, mixing = parse_folder_name(folder)

        if mass is None:
            continue

        banner_path = os.path.join(
            full_path,
            "Events/run_01_decayed_1/run_01_decayed_1_tag_1_banner.txt"
        )

        if not os.path.exists(banner_path):
            continue

        sigma_prod, sigma_decay, GammaZp, BRZpNN, GammaN = parse_banner(banner_path)

        # =====================================================
        # STORE EVERYTHING (NO DROPPING)
        # =====================================================
        data.append({
            "mass [GeV]": mass,
            "VlN2": mixing,
            "sigma(ee->Z'->NN) [pb]": sigma_prod,
            "sigma(ee->Z'->NN->mumujjjj) [pb]": sigma_decay,
            "GammaZp": GammaZp,
            "BRZpNN": BRZpNN,
            "GammaN": GammaN,
        })


# =========================================================
# DATAFRAME + SAVE
# =========================================================
df = pd.DataFrame(data)
df = df.sort_values(by=["mass [GeV]", "VlN2"])

output = "/home/gfcottin/MyGit/UBL_FCCee/master_csv/csv/Master_cross_section_decay_coupled_isr2.csv"
df.to_csv(output, index=False)

print(f"Saved to: {output}")
print("Total entries:", len(df))