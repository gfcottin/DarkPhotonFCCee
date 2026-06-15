# Repository for HNL Studies at FCC-ee in the U1BL Model 

This repository contains the work developed by **gfcottin** for Heavy Neutral Lepton (HNL) studies at FCC-ee within the $$U(1)_{B-L}$$ model framework.

Main contributions include:

* Proposal and idea of this project
* Identification of unexplored regions in the low-m_Z' model parameter space
* Selection of relevant benchmarks for the DELPHES study
* Proposal of the strategy for displaced vertex searches
* Computation of all relevant theoretical observables:

  * Production cross-sections
  * Decay widths and branching ratios
  * Kinematic distributions for displaced HNL events
  * Theoretical decay probabilities inside the IDEA detector geometry

---

# Repository Structure

## `gen_scripts/`

Contains scripts for event generation in **MadGraph5 (MG5)**:

* Coupled mass scans with and without ISR effects
* Individual benchmark generation for fixed $m_{Z'}$ values

The fixed benchmark generation was performed in two major production campaigns:

1. Initial scan to identify the parameter space with ISR sensitivity
2. Refined scan for smooth contour extraction

runs with

```bash
python3 generate_HNL_grid_XXX.py
```

Note the ```MG5_gen_U1BL_mu_FCCee``` folder as well as all output folders for lhe events and cross-sections must be created beforehand.

---

## `MG5_cards/`

Contains all MadGraph and model-related cards:

* UFO model implementation developed in:
  https://arxiv.org/abs/1908.09838
* Parameter card with automatic decay handling
* MadSpin cards for event generation and decays

---

## `pythiaCode/`

Contains the **Pythia 8** code used to extract kinematic information for displaced HNL events.

Includes:

* Benchmark-specific run scripts
* `get_BM_values.py` scripts to extract exact benchmark values from stored LHE files
* Kinematic extraction tools for displaced vertex observables

runs with

```bash
make
source run_XXX.sh
```

---

## `master_csv/`

Contains scripts that extract and combine relevant information from:

* MG5 LHE banner files
* Pythia 8 outputs

All python files run with

```bash
python3 get_XXX.py
```
---

### `get_Master_cross_section_decay_fixed_mZp.py`

Extracts directly from LHE banner files :

* Pair production cross-section:

 $$ e^+ e^- \to Z' \to NN $$ 
 
* Full signal cross-section including MadSpin decays: 
 
 $$ e^+ e^- \to Z' \to NN \to \mu\mu jjjj $$

* Total decay width of Z'

* Total decay width of HNL

* BR of Z' to two HNLs

Outputs CSV files:

```bash
Master_cross_section_decay_mZpXX.csv
```

All cross-sections include ISR effects.

---

### `get_Master_cross_section_coupled_isr.py`

Extracts cross-sections for the coupled mass scenario from the "short" MG5 command that outputs cross-sections to .txt files:

* With ISR
* Without ISR

Outputs:

```bash
Master_cross_section_coupled_isr.csv
```

---

### `get_Master_decay_coupled_isr.py`

Extracts from MG5 banner files for the coupled mass scenario:

* HNL total decay width
* $Z'$ total decay width
* Branching ratio:

  $Z' \to NN$

Outputs:

```bash
decay_data_coupled_isr2.csv
```

---

### `get_Master_kinematics.py`

Extracts all relevant kinematic quantities from Pythia outputs required to compute decay probabilities for the fixed Z' scenarios.

Also combines information from:

```bash
Master_cross_section_decay_XXX.csv
```

Outputs large datasets:

```bash
MasterData_kinematics_XXX.csv
```

These files are not included in the repository due to size limitations.

Stored quantities include:

* Energy
* Boost factors
* Angular variables
* Decay lengths
* Total decay width
* ctau


for each benchmark combination of HNL mass and mixing.

---

### `get_decay_probability_fixed_mZp.py`

Computes the average HNL decay probability inside the IDEA detector geometry for the three fixed scenarios using:

* Pythia kinematic outputs
* MG5 total decay widths

It also extracts 

* Cross-section information

to compute the number of expected signal events.

Produces the final datasets (merging all runs):

```
MasterData_XXX.csv
```

for each benchmark point $(m_N, V_{\ell N}^2)$.

---

# Final Dataset Variables

The final ``` MasterData_XXX.csv``` tables contain:

```bash
HNLmass,
Vlnu2,
GammaN,
HNLctau,
average_decayLenght_mm,
average_decayLength_mm_z,
decay_Probability_IDEA,
decay_Probability_IDEA_z,
crossNN,
crossALL,
N_DecayIDEALumi1,
N_DecayIDEALumi1_z
```

---

## Variable Definitions

### `HNLmass`

Heavy Neutral Lepton mass in GeV.

---

### `Vlnu2`

Active-sterile mixing squared in the muon sector.

---

### `GammaN`

Total HNL decay width (Γ_N) in GeV, extracted from MG5's `DECAY` block.

---

### `HNLctau`

Proper decay length in mm:

cτ = (3×10¹¹ × 6.581×10⁻²⁵) / Γ_N
---

### `average_decayLenght_mm`

The decay length in mm computed from Pythia displaced vertex information:

$$\sqrt{trux^2 + truy^2 + truz^2} $$

where:

* `trux`
* `truy`
* `truz`

are the LLP decay vertex coordinates extracted from Pythia. The mean is saved.

---

### `average_decayLength_mm_z`

Projected decay length along the (z)-direction:

$$ \beta_z \gamma c\tau $$

where:

- $\beta_z$

- $\gamma$

are extracted from Pythia four-vectors. The mean is saved.

---

### `decay_Probability_IDEA`

Average probability for HNL decay inside IDEA using the full decay length.

---

### `decay_Probability_IDEA_z`

Average probability for HNL decay inside IDEA using the projected (z)-direction  decay length.

---

### `crossNN`

Cross-section:

$$ \sigma(e^+e^- \to Z' \to NN) $$

computed at:

- $\sqrt{s} = 91.2$ GeV 

- $g' = 10^{-4}$

including ISR effects.

Units: pb.

---

### `crossALL`

Cross-section:

$$ \sigma(e^+e^- \to Z' \to NN \to \mu\mu jjjj) $$ 

computed at: 

- $\sqrt{s} = 91.2$ GeV

- $g' = 10^{-4}$

including ISR effects.

Units: pb.

---

### `N_DecayIDEALumi1`

Expected number of displaced signal events:


N = σ_ALL × ⟨decay_Probability_IDEA⟩ × 10^6 × 150

where:

- $10^6$ converts pb to ab 

- $150$ corresponds to the integrated luminosity in ab^-1
---

### `N_DecayIDEALumi1_z`


Same computation as above but using the projected (z)-direction decay probability (decay_Probability_IDEA_z). This is the one we show.

---

## `plot_scripts/`

Contains scripts used to visualize and study the physics behavior of the model:

* Cross-sections with and without ISR
* Branching ratios
* Proper decay lengths ($$c\tau$$)
* Average decay probabilities
* Expected number of signal events
* Benchmark grids in the mass-mixing plane

The final publication-quality figures are generated using:

```bash
plots_paper.py
```
