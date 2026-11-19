# Beta-Lactam ICU Dosing Cohort — free sample

> **This folder contains the technical documentation, the validation code and a free evaluation sample (400 of 20,000 patients, all five dosing regimens) — not the full dataset.**
> **Full dataset (20,000 patients, 100,000 patient-regimens, 10 linked tables):** **[sentineldata.com.ua/dataset/betalactam-icu-dosing-cohort](https://sentineldata.com.ua/dataset/betalactam-icu-dosing-cohort)**

**DOI (Zenodo):** [10.5281/zenodo.24376814](https://doi.org/10.5281/zenodo.24376814)
**Also archived:** [Kaggle (free sample)](https://www.kaggle.com/datasets/corot7b/betalactam-icu-dosing-cohort) · [Hugging Face](https://huggingface.co/datasets/codesentineldata/betalactam-icu-dosing-cohort)

**Status: MODEL-GENERATED / HYPOTHETICAL.** Fully synthetic data from published population pharmacokinetic models. No real patient stands behind any row. It supports benchmarking and method development for beta-lactam dosing and drug monitoring; it is not clinical evidence.

Twenty thousand synthetic adults in intensive care are treated with meropenem or piperacillin-tazobactam (10,000 each) and each of them is dosed **five times**, under five different regimens, with the same body and the same random numbers every time. Because one real patient only ever receives one regimen, the difference between regimens for the same person can never be measured in a real ICU. Here it is stored. Next to the noisy record a bedside clinician would have (two blood samples, creatinine-based clearance estimates, the isolate and its MIC) the dataset keeps the hidden truth behind it: the patient's true clearance and volumes, and the true concentration curve, total and unbound, every 10 minutes for 72 hours under every regimen. You train on what the bedside has and score against what really happened.

### Cohort and regimens

- **Patients:** adults, 10,000 on meropenem and 10,000 on piperacillin-tazobactam, with age, sex, weight, height, albumin, Cockcroft-Gault and CKD-EPI clearance estimates, and flags for renal replacement therapy (CRRT), ECMO, burns (with burned surface area) and surgery in the previous 24 hours.
- **Microbiology:** one pathogen per patient (*Klebsiella pneumoniae*, *Escherichia coli*, *Pseudomonas aeruginosa* or *Acinetobacter baumannii*) and a measured MIC drawn from the EUCAST MIC distribution of that species and drug. The distributions are in the `pathogen_mic` table.
- **Five regimens per patient (100,000 patient-regimens):**
  - **A**, label bolus dosing over 30 minutes: meropenem 1 g every 8 h, piperacillin-tazobactam 4.5 g every 6 h. This is the regimen whose failure the benchmark predicts.
  - **B**, a loading dose followed by 3-hour extended infusions.
  - **C**, a loading dose followed by continuous infusion.
  - **D**, continuous infusion adjusted after the 24-hour and 48-hour blood levels (drug monitoring), aiming at a free concentration of four times the MIC. The adjustments and the clinician's predictions are stored.
  - **E**, a loading dose and a continuous infusion set from the patient's true clearance. It is an oracle that no bedside has, and it marks the upper bound.
- **Hidden truth:** true clearance, central and peripheral volumes, inter-compartment clearance, unbound fraction, the individual random effects, and the true urinary creatinine clearance. The gap between the creatinine-based estimate and the true clearance is what makes bedside dosing miss in patients with augmented renal clearance.

### Pharmacokinetic models

Each patient is generated from one of eight published population models, four per drug. Every parameter is traced in the constants register (`docs/constants_register.csv`) with its source, and the sources are in `docs/references.csv`.

| Model | Drug | Structure | Population in the source |
|---|---|---|---|
| M1 | meropenem | 2-compartment, linear | critically ill, preserved or increased renal function (doi:10.2147/IDR.S343264) |
| M2 | meropenem | 2-compartment, linear | burn and non-burn patients, with and without CVVH (doi:10.1111/bcp.15138) |
| M3 | meropenem | 2-compartment, linear | critically ill adults including ECMO (doi:10.3390/pharmaceutics13111861) |
| M4 | meropenem | 2-compartment, linear | critically ill adults, day 1 and steady state (doi:10.1038/s41598-025-20630-5) |
| P1 | piperacillin | 2-compartment, linear | ICU, continuous infusion (doi:10.3390/antibiotics12030531) |
| P2 | piperacillin | 1-compartment, linear | ICU hospital-acquired pneumonia, continuous infusion, CRRT (doi:10.1128/aac.01760-25) |
| P3 | piperacillin | 2-compartment, linear | ECMO patients (doi:10.1128/Spectrum.00633-21) |
| P4 | piperacillin | 2-compartment, linear plus Michaelis-Menten | critically ill adults, continuous and intermittent (doi:10.1016/j.ijantimicag.2019.08.024) |

The cohort mixes the four models on purpose, so the nominal model is wrong for most patients, as it would be at the bedside of an unknown patient. Concentrations are produced by solving the model for each patient and regimen; the observed layer adds measurement error to the two blood samples.

### Sample contents

This folder holds the **free sample**: 400 patients (200 meropenem, 200 piperacillin-tazobactam), a true subset of the 20,000 (a fixed random draw, 1 in 50). Every row keeps the values it has in the full data and nothing was simulated again. Tables, columns, types and keys are identical, so code written on the sample runs on the full cohort unchanged.

| Table | Rows in the sample | Content |
|---|---:|---|
| `patients_observed` | 400 | What the bedside sees: demographics, size, albumin, clearance estimates, CRRT/ECMO/burn/surgery flags, pathogen and MIC |
| `patients_truth` | 400 | Hidden truth: model id, true urinary creatinine clearance, true clearance and volumes, unbound fraction, random effects |
| `regimens` | 2,000 | Dosing schedule of each patient-regimen as segments (start, duration, rate), day-1 and 72-hour dose, whether the dose ceiling was applied |
| `regimen_metrics` | 2,000 | fT>MIC (50% and 100%), 4×MIC target, steady-state concentrations, neuro- and nephrotoxicity flags, meropenem 8 to 16 mg/L window flags |
| `pk_profiles` | 866,000 | True total and unbound concentration every 10 minutes for 72 hours (433 points per patient-regimen) |
| `tdm_samples` | 800 | The two noisy blood samples of regimen D, at 24 h and 48 h |
| `tdm_predictions` | 1,200 | The clinician's predicted levels: prior model only, and after the first sample |
| `tdm_adjustments` | 400 | Initial infusion rate, the rates after each sample and the clearance estimates behind them |
| `model_registry` | 8 | The eight source models with covariate forms and DOIs |
| `pathogen_mic` | 133 | MIC distributions by drug and species |

The full cohort has 20,000 patients, 100,000 patient-regimens, 43.3 million profile points and about 290 MB in ten Parquet tables. The sample is about 7 MB. In the sample the label bolus regimen fails to hold the free concentration above the MIC for the whole of hours 48 to 72 in 16.0% of meropenem patients and 34.5% of piperacillin-tazobactam patients; with 200 patients per drug these shares move by several points from one draw to another.

### Validation and benchmark

The validation report (a PDF on the dataset page and in the GitHub repository) was run on the full 20,000 patients. The task is to predict, at the 24-hour decision point, which patients will not keep the free drug concentration above the MIC throughout hours 48 to 72 under regimen A (prevalence 24.8%). Three input sets are scored with logistic regression and XGBoost (600 trees, depth 3, learning rate 0.03) in five-fold stratified cross-validation, 16,000 patients to train and 4,000 to test in each fold, seed 20261119. No hidden-truth column is an input.

| Inputs | Model | AUROC (SD) | AUPRC | Brier |
|---|---|---|---|---|
| characteristics + first level | XGBoost | 0.809 (0.005) | 0.639 | 0.136 |
| characteristics + first level | logistic regression | 0.809 (0.004) | 0.640 | 0.136 |
| characteristics + microbiology | XGBoost | 0.893 (0.007) | 0.777 | 0.105 |
| characteristics + microbiology | logistic regression | 0.854 (0.007) | 0.710 | 0.123 |
| characteristics + first level + microbiology | XGBoost | **0.970 (0.003)** | 0.927 | 0.059 |
| characteristics + first level + microbiology | logistic regression | 0.956 (0.002) | 0.897 | 0.069 |

Without microbiology the task has a difficulty similar to the one reported by Wieringa and colleagues for real ICU patients (AUROC 0.75 to 0.80, doi:10.3390/antibiotics12121674). That is a statement about difficulty only: their data were noisy and their target was defined differently, while here the label comes from a model that the features partly describe.

The report also compares the data with seven published observations on real patients (target non-attainment on bolus and on extended or continuous infusion, urinary clearance against the Cockcroft-Gault estimate, meropenem after level-guided adjustment, target attainment with model-informed dosing, and the prediction error of the piperacillin models). Six match or sit in line with the published values, one is close, none differs. Nothing was tuned to bring these numbers closer to the literature. The ten internal checks all pass.

### Honest limitations

- **Seventy-two hours, constant kidneys.** Renal function does not change inside the horizon. Acute kidney injury and recovery need a different product.
- **No clinical outcomes.** Cure and death are not simulated. Toxicity appears only as threshold flags on the lowest concentration.
- **Piperacillin means piperacillin.** Tazobactam is not modelled, so every metric is computed for piperacillin alone.
- **Adults only.** Resistance stands still: MIC distributions are fixed and do not evolve during the 72 hours.
- **Scenario shares are design choices.** Ten percent renal replacement therapy, eight percent ECMO and a burn share inside one meropenem model were set so that benchmarks get enough cases. They are not prevalences.
- **Saturable piperacillin elimination rests on one model (P4).** The published model gives no random effects, so they are borrowed from a sister model of the same drug, and its linear clearance follows creatinine clearance through the labelled renal excretion of 68% of the dose. Both choices are marked in the constants register.
- **The nominal piperacillin model runs high in two worlds.** After one measured level its median error stays at 52.1% for the ECMO world and 62.7% for the saturable world; both are inside the range of the 24 published models.
- **Regimen D aims at the threshold.** Its target is four times the MIC, so close to half of the patients sit just under it.
- **Circularity.** The label and the features come from the same generating model, so a score here is a score to beat in a controlled setting, not a prediction of bedside performance. MIC is a drawn covariate, not the result of susceptibility testing.
- **A 400-patient slice is thin in rare strata** (CRRT, ECMO and burns: 41, 35 and 17 patients here; about fifty patients per true model). Judge methods on the full cohort.

### What you can build

- A **failure predictor** for label dosing from bedside data, with the 24-hour level and the isolate as inputs, scored against the true concentration curve.
- A **Bayesian dosing or drug-monitoring method**, tested head-to-head against the stored clinician predictions and regimen-D adjustments.
- A **comparison of dosing policies** with a known answer: the same patient under five regimens, so the true benefit of an extended or continuous infusion is a subtraction.
- **Model-misspecification studies**: each patient's true model is stored next to the nominal model the clinician would assume.
- **Teaching**, with every patient carrying its own truth row.

---

### Folder layout

| Path | Content |
|---|---|
| `sample/*.parquet`, `sample/*.csv` | The ten tables above, plus the constants register (216 constants with sources) and the references (28) |
| `sample/schema.json`, `sample/manifest.json`, `sample/README_parquet.txt` | Column-level schema; file list with SHA-256; how to open the Parquet files |
| `sample/BETALACTAM-ICU-DOSING-COHORT_Sample_Passport_v1.1.pdf` | Sample passport |
| `validation/benchmark_script.py` | The exact script that produced the published numbers on the full 20,000 patients, unmodified |
| `validation/benchmark_results.parquet` | Its per-fold results on the full cohort |
| `validation/validation_report_EN.pdf` | The validation report |
| `validation/requirements.txt` | Package versions the script was run with |
| `notebook/validate_sample.ipynb` | Runs the same script on the 400-patient sample (executed, output included) |

Run it yourself:

```bash
pip install -r validation/requirements.txt
python validation/benchmark_script.py sample/ results.parquet
```

On 400 patients the numbers are noisy and differ from the published ones; the notebook shows by how much.

### Permitted use

This free sample (data, passport and documentation) is released for any lawful use, with attribution, under **CC BY-NC 4.0, non-commercial use only**. The full 20,000-patient dataset is sold separately under a commercial research license; see the dataset page. Fully synthetic: no real patient is used or reproduced. **Model-generated and hypothetical; not for clinical decisions.**

### Citation

> Code Sentinel Data, Chekerskyi, M. (2026). *Beta-Lactam ICU Dosing Cohort* — Free Sample. Zenodo. https://doi.org/10.5281/zenodo.24376814
