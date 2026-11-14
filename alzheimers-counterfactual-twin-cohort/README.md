# Alzheimer's Counterfactual Twin Cohort — free sample

> **This folder contains the technical documentation, the validation code and a free evaluation sample (500 of 10,000 people) — not the full dataset.**
> **Full dataset (10,000 people, 27 scenarios, 12 linked tables):** **[sentineldata.com.ua/dataset/alzheimers-counterfactual-twin-cohort](https://sentineldata.com.ua/dataset/alzheimers-counterfactual-twin-cohort)**

Ten thousand synthetic people, aged 50 to 75 at entry, followed for up to 25 years through the course of Alzheimer's disease. Every person is lived **27 times**: once untreated, and 26 more times under different medical strategies, with the same body and the same random numbers every time. The effect of any strategy on one person is therefore a subtraction of two of that person's own trajectories, which real studies can never provide. The hidden truth (amyloid, tau, inflammation, clearance, damage, every quarter) is stored next to the noisy clinical record, so you train on what a clinic would see and score against what actually happened.

**DOI (Zenodo):** [10.5281/zenodo.24227228](https://doi.org/10.5281/zenodo.24227228)
**Also archived:** [OSF](https://doi.org/10.17605/OSF.IO/EPK8Q) · [Kaggle (free sample)](https://www.kaggle.com/datasets/corot7b/alzheimers-counterfactual-twin-cohort)

**Status: MODEL-GENERATED / HYPOTHETICAL.** Fully synthetic data from a mechanistic disease model. No real individual stands behind any row. It supports benchmarking, method development and trial or screening design prototyping; it is not clinical evidence and does not replace real cohort data.

## What the data are good for

- **Benchmarking causal-effect estimators.** The true individual effect of every strategy is known, so you can measure the error of a CATE or uplift model instead of guessing it.
- **Trial and screening design.** Six labelled worlds (natural course, clearance therapy, TNF inhibitor, p-tau217 screening with lecanemab, lecanemab after symptoms only, subtype-matched therapy) share one detection path, so a difference between worlds is a difference between theories and nothing else. Sample-size and power questions can be answered by drawing arms from the cohort.
- **Dementia forecasting from an entry visit.** Annual MMSE, CDR-SB, plasma p-tau217 and amyloid PET with realistic measurement error.
- **Teaching.** A cohort whose answers can be opened and checked.

## Sample contents

A true row-level subset of the full dataset: 500 people selected by `subject_id`, same seed (`20261108`), same generation pass, all 27 scenarios for each of those people. Not a separate generation run.

| Path | Rows | Content |
|---|---:|---|
| `sample/cohort.parquet` | 500 | Age at entry, sex, APOE e4 allele count |
| `sample/scenarios.parquet` / `.csv` | 27 | World, strategy, requested and applied effect shares, heterogeneity mode, admissibility flags |
| `sample/visits/scenario_id=S00 … S26/` | 245,973 | Annual MMSE, CDR-SB, plasma p-tau217 with zone, clinical stage; one partition per scenario |
| `sample/pet_scans.parquet` | 43,030 | Amyloid PET in centiloid, with measurement error |
| `sample/detection_events.parquet` | 4,678 | Who was found, at what age, by screening or by clinical route |
| `sample/treatments.parquet` | 4,678 | Therapy, start, stop, stop reason, assignment |
| `sample/adverse_events.parquet` | 148 | ARIA-E during a lecanemab course (risk depends on APOE e4 count) |
| `sample/subtype_assays.parquet` | 1,128 | Measured molecular subtype, world W4 only |
| `sample/outcomes.parquet` | 13,500 | MCI, dementia, moderate dementia, death (flag plus age), dementia-free years, last CDR-SB |
| `sample/truth/subject_truth.parquet` | 500 | True subtype, amyloid onset age, damage rate, cognitive reserve, tau rate multiplier |
| `sample/truth/theta_by_subject.parquet` | 13,500 | Per-person effect shares for every scenario |
| `sample/truth/truth_quarterly/scenario_id=S00 … S26/` | 957,431 | True amyloid, tau, inflammation, clearance, damage, noise-free CDR-SB every quarter |
| `sample/data_dictionary.csv`, `schema.json`, `manifest.csv` | — | Every column documented, schema, SHA-256 per file |
| `sample/ALZ-PATHWAY-TWIN_Sample_Passport_EN.pdf` | — | Sample data passport |
| `sample/parquet_howto.txt` | — | How to open Parquet files (pandas, R arrow, DuckDB) |

The full dataset carries 10,000 people: 4.77 M visit rows, 826,990 PET scans, 270,000 outcome rows and 18.5 M quarterly truth rows, plus the audit constants, the literature registry and the validation tables. See the dataset page for the complete list.

## Validation / benchmark

`validation/benchmark_script.py` is the exact script that produced the published numbers on the full 10,000-person dataset, reproduced here unmodified. It runs two benchmark tasks (a third, trial-power task is part of the published `benchmark_results.parquet`):

- **Task 1: five-year dementia forecast from the entry visit** (natural course, scenario S00). Logistic regression and XGBoost on age, sex, APOE e4, MMSE, CDR-SB and log p-tau217, 5-fold stratified CV.
- **Task 2: individual treatment effect of early therapy.** A randomised split between S00 and S15 is simulated, a T-learner is fitted on what the trial would observe, and the estimate is scored against the true individual effect (PEHE, ATE bias, rank correlation).

**Published results, full dataset (seed 20261108):**

| Task | Model | Result |
|---|---|---|
| Task 1 (n = 8,577, 183 events) | Logistic regression, all features | ROC AUC **0.901**, Brier 0.0123 |
| Task 1 | XGBoost, all features | ROC AUC 0.895, Brier 0.0125 |
| Task 1 | Logistic regression, p-tau217 only | ROC AUC 0.829 |
| Task 1 | Logistic regression, p-tau217 + MMSE + APOE e4 | ROC AUC 0.882 |
| Task 2 (n = 7,617 alive at year 10 in both worlds) | T-learner, ridge | ATE bias +0.006, PEHE 0.659, rank correlation 0.310 |
| Task 2 | T-learner, XGBoost | ATE bias +0.001, PEHE 0.837, rank correlation 0.120 |
| Task 2 reference | Predict the true mean effect for everyone | PEHE 0.673 |

Read the second block honestly: both T-learners recover the **average** effect almost exactly (bias near zero), but the ridge model only just beats the constant-effect reference on individual error (0.659 vs 0.673) and XGBoost is worse than the reference (0.837). Individual effects are hard to recover from noisy covariates, and the dataset shows that instead of hiding it. That is the point of keeping the truth next to the observations.

`validation/validation_report_EN.pdf` is the full validation report. `validation/trial_replications.csv` lists the four calibration targets (lecanemab amyloid PET and CDR-SB, the XPro1595 trial), all met. `validation/prediction_results.csv` lists six predictions written down and sealed before the full run: **none matched within tolerance, one was withdrawn before the run, one was compared without a threshold.** Misses are published next to hits on purpose.

### Re-running the benchmark on the sample

`notebook/validate_sample.ipynb` runs the same script, unmodified, against the 500-person sample (executed output is stored in the notebook). It is a reproducibility smoke test only. **The numbers it produces are not statistically meaningful and must not be quoted:** after the five-year filter the sample leaves 441 people for Task 1 with just **6 dementia events**, so each CV fold sees one or two events and the AUC swings widely with the seed. Only the published n = 10,000 numbers above are the real benchmark.

To run it yourself:

```bash
pip install -r validation/requirements.txt
python validation/benchmark_script.py --data sample --out benchmark_results_sample.parquet
```

## Known limitations

- Cohort entry is age 50; there are no reference data on amyloid prevalence below that age, so the cohort says nothing about younger-onset disease.
- Amyloid share of damage at symptomatic stage (0.60) was fitted to the lecanemab trial and the inflammation share (0.38) to a soluble-TNF trial; the clearance share has no clinical anchor and its grid (0, 0.5 and 1 times the amyloid share) is a design choice.
- Scenarios S25 and S26 asked for shares that would push some person's total effect above 1; an admissibility rule reduces them, so they equal S23 and S24 (flagged in the `scenarios` table).
- The subtype-matched world (W4) is an experimental condition that no trial has tested.
- None of the six sealed predictions matched within tolerance (see `validation/prediction_results.csv`).
- Full list: the [dataset page](https://sentineldata.com.ua/dataset/alzheimers-counterfactual-twin-cohort), section on limitations, and the validation report.

## Licensing

This free sample (data, script and notebook) is released under **CC BY-NC 4.0**: non-commercial use permitted with attribution. The full 10,000-person dataset is sold under a commercial research license; see the [dataset page](https://sentineldata.com.ua/dataset/alzheimers-counterfactual-twin-cohort) and the [licence terms](https://sentineldata.com.ua/dataset-license).

## Citation

> Code Sentinel Data, Chekerskyi, M. (2026). *Alzheimer's Counterfactual Twin Cohort*. Zenodo. https://doi.org/10.5281/zenodo.24227228

## Links

- Full dataset and passport: https://sentineldata.com.ua/dataset/alzheimers-counterfactual-twin-cohort
- Zenodo record (DOI): https://doi.org/10.5281/zenodo.24227228
- OSF: https://doi.org/10.17605/OSF.IO/EPK8Q
- Kaggle (free sample): https://www.kaggle.com/datasets/corot7b/alzheimers-counterfactual-twin-cohort
