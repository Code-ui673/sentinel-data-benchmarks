# Hospital Antibiotic Resistance Counterfactual Cohort — free sample

> **This folder contains the technical documentation, the validation code and a free evaluation sample (500 of 10,000 patients, scenarios S10/S13/S16, all six policy worlds) — not the full dataset.**
> **Full dataset (10,000 patients, 26 scenarios, 10 linked tables):** **[sentineldata.com.ua/dataset/hospital-antibiotic-resistance-counterfactual-cohort](https://sentineldata.com.ua/dataset/hospital-antibiotic-resistance-counterfactual-cohort)**

Ten thousand synthetic adult patients are admitted to a hospital ward and treated with piperacillin-tazobactam for a resistant gram-negative organism. Each patient is then lived **six times**: once under standard practice, and five more times under different stewardship and dosing policies, with the same body and the same random numbers every time. The share of each patient's resistance acquisition that any given policy actually prevents is a number no real ward can ever measure, because one patient only ever lives one policy. This dataset gives you that number directly, by giving you the same patient twice. The hidden truth (true acquisition day, 24-hour drug exposure, strain burdens, true kidney clearance) is stored next to the noisy observed clinical record, so you train on what a ward's infection-control team would actually have and score against what really happened.

**DOI (Zenodo):** [10.5281/zenodo.24248664](https://doi.org/10.5281/zenodo.24248664)
**Also archived:** [OSF](https://doi.org/10.17605/OSF.IO/59FXM) · [Kaggle (free sample)](https://www.kaggle.com/datasets/corot7b/antibiotic-resistance-counterfactual-cohort)

**Status: MODEL-GENERATED / HYPOTHETICAL.** Fully synthetic data from a mechanistic disease, pharmacokinetic and detection model. No real patient stands behind any row. It supports benchmarking, method development and stewardship/surveillance-design prototyping; it is not clinical evidence and does not replace a real ward trial.

## What the data are good for

- **Causal-effect estimation with a known answer.** Every patient lives all six policy worlds with the same random numbers, so the true individual and average treatment effect of any policy is a simple subtraction, not an estimate.
- **Surveillance-schedule design.** The truth layer holds the true day of organism acquisition; the observed layer holds the day a scheduled culture actually detects it. The gap between the two is the exact error of a given culture schedule, and it can be measured directly.
- **Stewardship and dosing-policy evaluation across mechanisms.** Six real policies (standard therapy, short course with rapid testing, gut decolonisation, containment dosing, true-clearance dosing, vaccination) are tested against 26 scenarios spanning a grid of how much of resistance acquisition is attributable to antibiotic exposure, ward transmission, or under-dosing — a method has to work across the whole plausible range, not one assumed mechanism.
- **Early-warning carriage forecasting.** Admission data alone, plus however many surveillance cultures have resulted, forecasting a new resistant culture by day 14.
- **Teaching**, with every patient-world-scenario triple carrying its own truth row.

## Sample contents

A true row-level subset of the full dataset: 500 patients selected by `subject_id`, same seed (`20261110`), same generation pass, all six policy worlds in three of the 26 scenarios (S10, S13, S16) — not a separate generation run and not the same scenario (S12) used for the published full-dataset benchmark.

| Path | Rows | Content |
|---|---:|---|
| `sample/data/observed/admissions/scenario_id=.../part-0.parquet` | 9,000 | Age, sex, serum creatinine, estimated clearance, dose tier, course length, four binary admission risk indicators |
| `sample/data/observed/cultures/...` | 72,000 | Eight scheduled surveillance cultures per patient-world-scenario: resistant phenotype, reported MIC, day the result reaches the clinician |
| `sample/data/observed/dosing/...` | 115,500 | Daily piperacillin dose, fraction of the day the drug ran, skipped days |
| `sample/data/observed/labs/...` | 54,000 | Serum creatinine, the only kidney measurement a clinician sees |
| `sample/data/observed/outcomes/...` | 9,000 | New carriage by day 14, in-hospital and 90-day death, days of antibiotic actually given |
| `sample/data/observed/ward_census/...` | 558 | Daily cohort-level census: cohort size, observed carrier share, total antibiotic given |
| `sample/data/truth/subject_truth/subject_truth.parquet` | 500 | True clearance, true admission colonisation, true acquisition-hazard multiplier, unobserved frailty, common random numbers |
| `sample/data/truth/events_truth/...` | 9,000 | True day of acquisition, 24-hour drug exposure, day-30 strain burdens, mortality probability used to draw the outcome |
| `sample/data/truth/trajectory_truth/...` | 1,080,000 | Drug concentration and both strain burdens at quarter-day resolution across the full 30-day course |
| `sample/data/truth/theta_by_scenario/...` | 18 | Attribution shares and residual policy fractions, 3 scenarios x 6 worlds |
| `sample/data/sample_subject_ids.csv` | 500 | The sampled `subject_id` values |
| `sample/data_dictionary.csv`, `schema.json`, `manifest.csv` | — | Every column documented, schema, SHA-256 per file |
| `sample/ward-amr-counterfactual_sample_passport_EN.pdf` | — | Sample data passport |
| `sample/parquet_howto.txt` | — | How to open the partitioned Parquet files (pandas, R arrow, DuckDB) |

The full dataset carries 10,000 patients across 26 scenarios: 1,560,000 rows in most patient-world-scenario tables, 20,020,000 dosing rows, and 187,200,000 quarter-day truth-trajectory rows, plus the full constants audit (61 constants, 53 literature sources) and the complete validation log. See the dataset page for the full list.

## Validation / benchmark

`validation/benchmark_script.py` is the exact script that produced the published numbers on the full 10,000-patient dataset, reproduced here unmodified. It trains logistic regression and XGBoost with five-fold, patient-grouped cross-validation on the control world (W0) of one scenario, and reports five benchmark tasks plus four landmark variants:

- **T1 — new resistant culture by day 14, admission data only.**
- **T2 — same, restricted to patients negative on the admission culture.**
- **T3 — resistant culture on day 14, cultures resulted by day 9**, with landmark variants at days 2, 4 and 12 (more cultures resulted = more signal).
- **T4 — T3 restricted to admission-negative patients**, with the same landmarks.
- **T5 — death by day 90, cultures resulted by day 9** (included to show that mortality is, by design, not learnable from patient properties here).
- **U1 — the true acquisition-hazard multiplier** (truth layer only, the ceiling no real-world buyer can reach).

**Published results, full dataset (n = 10,000, seed 20261110):**

| Task | Model | AUC (95% interval) |
|---|---|---|
| T1 — admission data only | Logistic regression | **0.697** (0.685–0.707) |
| T1 — admission data only | XGBoost | 0.690 (0.679–0.700) |
| T2 — admission-negative patients | Logistic regression | 0.748 (0.737–0.758) |
| T3 — cultures resulted by day 9 | Logistic regression | **0.847** (0.838–0.854) |
| T3 — landmark, cultures resulted by day 12 | Logistic regression | **0.871** (0.863–0.877) |
| T4 — T3, admission-negative | Logistic regression | 0.840 (0.830–0.848) |
| T5 — death by day 90 | Logistic regression | **0.564** (0.550–0.580) |
| U1 — true hazard multiplier (ceiling) | — | 0.795 |

Read these with care, not at face value. The 0.847–0.871 forecast AUCs are driven largely by **persistent carriage in this model**: a colonised patient never clears the organism, so an early positive culture almost guarantees a later one. This is stated plainly rather than let a high score speak for itself — it is a property of the dataset's disease model, and a method benchmarked here should not expect the same number on data where carriage clears. The 0.564 mortality AUC is intentional: the 90-day death model in this generator depends only on true acquisition and planned course length, nothing else about the patient, precisely so the dataset cannot be mistaken for a mortality-prediction benchmark.

`validation/validation_report_EN.pdf` is the full validation report (34 automatic checks, all passing). `validation/sensitivity.csv` shows the benchmark under two alternative design choices (unobserved-frailty spread, invasive-device odds ratio) that the passport documents as genuine source conflicts rather than averaging them away. Twelve predictions were written down and hashed before the full run: **nine passed, two failed, one was not applicable** — the two misses (a 0.003 shortfall on the T3 day-9 AUC threshold, and an under-dosing pattern that did not show near a dose-tier boundary) are reported with their numbers in the passport, not adjusted after the fact.

### Re-running the benchmark on the sample

`notebook/validate_sample.ipynb` runs the same script, unmodified, against the 500-patient sample (scenario S13; executed output is stored in the notebook). It is a reproducibility smoke test only: with roughly 500 patients per task instead of 10,000, the AUCs it produces are noisy and must not be quoted. Only the published n = 10,000 numbers above are the real benchmark.

To run it yourself:

```bash
pip install -r validation/requirements.txt
python validation/benchmark_script.py sample/data benchmark_results_sample.parquet S13
```

## Known limitations

- **One pathogen, one drug.** A single resistant Enterobacterales strain pair and piperacillin-tazobactam only; other agents, organisms and combination therapies are not modelled.
- **Kidney function is static.** Serum creatinine stays at its admission value, so acute kidney injury and the dosing changes it would trigger are absent.
- **Mortality is intentionally unlearnable from patient properties** — see above. Do not use this dataset to train or benchmark a mortality predictor.
- **The forecast benchmark leans on persistent carriage** in this disease model; the headline AUCs would likely be lower if carriage could clear, as it sometimes does on a real ward.
- **Three source conflicts, resolved and documented rather than averaged:** the direction of the clearance-estimate bias, the strength of the invasive-device odds ratio, and in-hospital versus 90-day mortality all had conflicting published values. Each choice, and its effect on the benchmark, is in the passport with a sensitivity table.
- **Admission risk-factor prevalences (prior antibiotic course, invasive device, transfer, surgery) are design choices**, not measured for a general ward; their *effects* (odds ratios) are published, their *prevalence* is not.
- Full list and rationale: the [dataset page](https://sentineldata.com.ua/dataset/hospital-antibiotic-resistance-counterfactual-cohort) and the validation report.

## Licensing

This free sample (data, script and notebook) is released under **CC BY-NC 4.0**: non-commercial use permitted with attribution. The full 10,000-patient dataset is sold under a commercial research license; see the [dataset page](https://sentineldata.com.ua/dataset/hospital-antibiotic-resistance-counterfactual-cohort) and the [licence terms](https://sentineldata.com.ua/dataset-license).

## Citation

> Code Sentinel Data, Chekerskyi, M. (2026). *Hospital Antibiotic Resistance Counterfactual Cohort*. Zenodo. https://doi.org/10.5281/zenodo.24248664

## Links

- Full dataset and passport: https://sentineldata.com.ua/dataset/hospital-antibiotic-resistance-counterfactual-cohort
- Zenodo record (DOI): https://doi.org/10.5281/zenodo.24248664
- OSF: https://doi.org/10.17605/OSF.IO/59FXM
- Kaggle (free sample): https://www.kaggle.com/datasets/corot7b/antibiotic-resistance-counterfactual-cohort
