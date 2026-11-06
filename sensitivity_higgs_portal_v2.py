import os
import re
import time
import ast
import numpy as np
import pandas as pd


def decay_probability_array(theta_arr, beta_arr, gamma_arr, ctau_arr, RI, RO, LD):
    probs = np.zeros_like(theta_arr)
    for i in range(len(theta_arr)):
        theta_abs = np.abs(theta_arr[i])
        tan_theta = np.tan(theta_abs)
        if np.isclose(tan_theta, 0.0):
            continue

        L1 = min(LD, np.abs(RI / tan_theta))
        L2 = min(LD, np.abs(RO / tan_theta)) - L1

        if L2 <= 0:
            continue

        beta_z = beta_arr[i] * np.cos(theta_arr[i])
        beta_z_abs = np.abs(beta_z)
        if beta_z_abs <= 0.0 or gamma_arr[i] <= 0.0 or ctau_arr[i] <= 0.0:
            continue

        lambda_z = beta_z_abs * gamma_arr[i] * ctau_arr[i]
        probs[i] = np.exp(-L1 / lambda_z) * (1.0 - np.exp(-L2 / lambda_z))
    return probs


# IDEA dimensions as far as the silicon wrapper
R_I   = 13.7
R_O   = 2080.0
L_D   = 2400.0
ETA_MAX = 2.5


# Fixed parameters
sqrts = 240
mv_list = [0.1]
L_int = 240    # ab^-1
AB_TO_PB_FACTOR = 1e6
hbarc_GeV_mm    = 1.973269804e-13

pythia_cols = ["mphi", "tau0", "decay_length_mm", "gamma", "energy", "p",
               "beta", "beta_z", "eta", "theta", "phi", "iEvent", "iPhi"]

OUT_DIR = "/home/jlucero/files_to_run/sensitivity_plots_data/"
os.makedirs(OUT_DIR, exist_ok=True)

_F = r"[0-9]+\.?[0-9]*(?:[eE][-+]?[0-9]+)?"
FNAME_RE = re.compile(rf"^decayKinematics_GRID-({_F})-({_F})-({_F})\.dat$")

L_int_ab = L_int
for mv_val in mv_list:

    pythia_files_path = f"/data1/jlucero/DP_ALP_research/higgs_portal/phi_decay/pythia_phi_data/mv_{mv_val}_sqrts_{sqrts}"
    csv_file = f"/data1/jlucero/DP_ALP_research/higgs_portal/mphi_run/complete_data/cs_data_mv{mv_val}_sqrts{sqrts}_data.csv"

    if not os.path.isdir(pythia_files_path) or not os.path.exists(csv_file):
        continue

    csdf = pd.read_csv(csv_file, sep=";")
    csdf = csdf[np.isclose(csdf["sqrts"], sqrts)].copy()

    csdf["width_list"] = csdf["width_list"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    csdf["br_list"]    = csdf["br_list"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    csdf["width_total"] = csdf["width_list"].apply(
        lambda x: np.sum(np.asarray(x, dtype=float)[np.isfinite(np.asarray(x, dtype=float))]) or np.nan
    )
    csdf["br_visible"] = csdf["br_list"].apply(
        lambda x: np.sum(np.asarray(x, dtype=float)[-2:][np.isfinite(np.asarray(x, dtype=float)[-2:])]) or np.nan
    )
    csdf["ctau_mm"] = csdf["width_total"].apply(
        lambda g: hbarc_GeV_mm / g if (g > 0 and np.isfinite(g)) else np.inf
    )

    outpath = os.path.join(OUT_DIR, f"results_higgs_portal_mv{mv_val}_sqrts{sqrts}.csv")
    if os.path.exists(outpath):
        os.remove(outpath)
    header_written = False
    n_rows_written = 0

    files = sorted(f for f in os.listdir(pythia_files_path)
                   if f.endswith(".dat") and os.path.getsize(os.path.join(pythia_files_path, f)) > 0)
    n_files = len(files)
    t_start = time.time()
    failed_files = []
    
    #Note: I read ctau, decay widths, and cross-section from a csv file I created before using only madgraph.

    for i_file, fname in enumerate(files, start=1):
        fpath = os.path.join(pythia_files_path, fname)

        try:
            m = FNAME_RE.match(fname)
            if m is None:
                print(f"[{i_file}/{n_files}] WARNING: cannot parse filename {fname}, skipping", flush=True)
                failed_files.append(fname)
                continue
            mphi_name, Lambda_name, lamHS_name = (float(x) for x in m.groups())

            df = pd.read_csv(fpath, sep=r"\s+", header=None, names=pythia_cols)
            mphi_val  = float(df["mphi"].iloc[0])
            lamHS_val = lamHS_name
            Lambda_file = Lambda_name

            elapsed = time.time() - t_start
            eta_min = (elapsed / (i_file - 1)) * (n_files - i_file + 1) / 60 if i_file > 1 else float("nan")
            print(f"[{i_file}/{n_files}] computing for mphi={mphi_val:.6g}, "
                  f"Lambda={Lambda_file:.6g}, lamHS={lamHS_val:g} "
                  f"| elapsed {elapsed/60:.1f} min, ETA {eta_min:.1f} min", flush=True)

            sub = csdf[np.isclose(csdf["mphi"],   mphi_val,    rtol=1e-3) &
                       np.isclose(csdf["lamHS"],  lamHS_val,   rtol=1e-3) &
                       np.isclose(csdf["Lambda"], Lambda_file, rtol=1e-6)]
            if sub.empty:
                print("    WARNING: no CSV row matches this file, skipping", flush=True)
                continue
            if len(sub) > 1:
                print(f"    WARNING: {len(sub)} CSV rows match, using the first", flush=True)
                sub = sub.iloc[[0]]

            theta = df["theta"].values
            beta  = df["beta"].values
            gamma = df["gamma"].values
            eta   = df["eta"].values

            full_mask = np.isclose(np.tan(theta), 0.0) | (np.abs(eta) >= ETA_MAX)

            row_csv = sub.iloc[0]
            Lambdaval = float(row_csv["Lambda"])
            sigmapb   = float(row_csv["cross"])
            br_raw    = float(row_csv["br_visible"])
            ctau_mm   = float(row_csv["ctau_mm"])


            no_decay = (not np.isfinite(ctau_mm)) or ctau_mm <= 0 \
                       or (not np.isfinite(br_raw)) or br_raw <= 0
            br_val = br_raw if np.isfinite(br_raw) else 0.0

            if no_decay:
                print(f"NOTE: no visible decay (ctau={ctau_mm}, BR={br_raw}) -> writing zeros", flush=True)
            else:
                ctau_arr = np.full(len(df), ctau_mm, dtype=float)
                probs = decay_probability_array(theta, beta, gamma, ctau_arr, R_I, R_O, L_D)
                probs[full_mask] = 0.0
                df["P"] = probs

                d0 = df[df["iPhi"] == 0].set_index("iEvent")
                d1 = df[df["iPhi"] == 1].set_index("iEvent")
                common = d0.index.intersection(d1.index)
                P1 = d0.loc[common, "P"].values
                P2 = d1.loc[common, "P"].values

                p1 = br_val * P1
                p2 = br_val * P2

                P_two      = p1 * p2
                P_atleast1 = p1 + p2 - p1 * p2

                P_two_m  = P_two.mean()
                P_atl1   = P_atleast1.mean()

            norm = sigmapb * L_int_ab * AB_TO_PB_FACTOR

            row = {
                "mphi": mphi_val,
                "Lambda": Lambdaval,
                "lamHS": lamHS_val,
                "Pavg_two": P_two_m,
                "Pavg_atleast1": P_atl1,
                "cross_pb": sigmapb,
                "BR_visible": br_val,
                "ctau_mm_csv": ctau_mm,
                "N_two": norm * P_two_m,
                "N_atleast1": norm * P_atl1,
            }

            pd.DataFrame([row]).to_csv(outpath, mode="a", header=not header_written, index=False)
            header_written = True
            n_rows_written += 1
        except Exception as e:
            print(f"    ERROR in {fname}: {type(e).__name__}: {e}", flush=True)
            failed_files.append(fname)
            continue

    print(f"\nmv={mv_val}: done in {(time.time()-t_start)/60:.1f} min, "
          f"{n_rows_written} rows written (of {n_files} files) to {outpath}", flush=True)
    if failed_files:
        print(f"{len(failed_files)} files failed:", *failed_files, sep="\n  ")