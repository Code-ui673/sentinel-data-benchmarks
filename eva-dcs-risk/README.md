# EVA Decompression Sickness Risk Dataset — free sample

> **This repository folder contains the technical documentation, validation code and a free evaluation sample (40 of 10,000 subjects (120 subject-branch rows)) — not the full dataset.**
> **Full dataset:** **[sentineldata.com.ua/dataset/eva-dcs-risk](https://sentineldata.com.ua/dataset/eva-dcs-risk)**

10,000 synthetic EVA crew members each evaluated under all three exposure branches of the Conkin 2017 calibration study — with a true within-subject counterfactual on every subject. Includes minute-by-minute tissue nitrogen kinetics, VGE grade outcomes, and DCS diagnoses generated from a calibrated Haldane nitrogen-washout model.

**DOI (Zenodo):** [10.5281/zenodo.23840239](https://doi.org/10.5281/zenodo.23840239)  
**Also archived:** [OSF](https://doi.org/10.17605/OSF.IO/TB458)

**Status: MODEL-GENERATED / SYNTHETIC.** This is fully synthetic data from a calibrated nitrogen-washout simulation, not records of real astronauts. It supports benchmarking, algorithm development and research prototyping; it is not clinical or flight-surgeon evidence.

## Sample contents

| File | Rows × Cols | Content |
|---|---:|---|
| `sample/crew.parquet` / `.csv` | 40 × 10 | One row per subject: demographics (age, sex, weight, body-fat %), fitness score, PFO status, prior DCS history, hydration state, factual branch assignment |
| `sample/observations.parquet` / `.csv` | 120 × 7 | One row per subject per branch: Doppler-check minute, VGE grade (0–4), symptom report, symptom onset minute, joint pain location |
| `sample/outcomes.parquet` / `.csv` | 120 × 9 | The core counterfactual table — factual + both counterfactual outcomes per subject: high_vge flag, DCS pain-only, DCS neurological, recompression treatment, counterfactual_set_id |
| `sample/profile.parquet` / `.csv` | 1,053 × 7 | Branch-level exposure profile, full table (not subset, because it is keyed by branch, not by subject) |
| `sample/truth.parquet` / `.csv` | 1,053 × 8 | Branch-level ground-truth tissue-nitrogen kinetics, full table |
| `sample/sample_manifest.json` | — | Manifest: tables, row counts and checksums |
| `sample/sample_passport_EN.pdf` | — | Sample data passport |
| `sample/working_with_parquet.txt` | — | How to open the Parquet files (pandas / R arrow / DuckDB) |

## About the dataset

The text below is the dataset's description from the product page, converted to Markdown.

Every year, astronauts preparing for Extravehicular Activity (spacewalks) go through a carefully timed pre-breathe protocol to purge dissolved nitrogen from their tissue before dropping to the 4.3 psi suit environment. Get the timing wrong, and supersaturated nitrogen can nucleate into venous gas emboli (VGE) — the bubbles that drive decompression sickness. This dataset lets you study that process in exhaustive counterfactual detail.

Ten thousand virtual EVA crew members are each evaluated under **all three** exposure branches of the Conkin 2017 calibration source — control (no mechanical loading), loading before the pressure drop, and loading during the supersaturated phase — using the *same underlying random draw per subject* across all three branches. No real clinical study can ever do this; one person is only ever in one arm. The result is a genuine within-subject comparison of loading-timing effects, free of between-subject noise.

### Three branches, one cohort

| Branch                        | Protocol                                            | Factual share | High-VGE rate |
|-------------------------------|-----------------------------------------------------|---------------|---------------|
| control                       | No mechanical loading (standard pre-breathe only)   | ~42.2%        | 17%           |
| group2_pre_only               | Ambulation before the pressure drop                 | ~38.3%        | 15%           |
| group1_during_supersaturation | Loading after the ramp, during peak supersaturation | ~19.5%        | 57%           |

Moving a subject from the control branch to loading-during-supersaturation flips **roughly 4 in 10 subjects** from low to high VGE grade — a within-subject effect size that no between-group study design can report directly.

### Dataset contents (11 tables in the full delivery)

| Table                                   | Rows   | Cols | Contents                                                                                                                                                                           |
|-----------------------------------------|--------|------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `crew.parquet`                          | 10,000 | 10   | One row per subject: demographics (age, sex, weight, body-fat %), fitness score, PFO status, prior DCS history, hydration state, factual branch assignment                         |
| `observations.parquet`                  | 30,000 | 7    | One row per subject per branch: Doppler-check minute, VGE grade (0–4), symptom report, symptom onset minute, joint pain location                                                   |
| `outcomes.parquet`                      | 30,000 | 9    | The core counterfactual table — factual + both counterfactual outcomes per subject: high_vge flag, DCS pain-only, DCS neurological, recompression treatment, counterfactual_set_id |
| `profile.parquet`                       | 1,053  | 7    | Minute-by-minute exposure protocol per branch: ambient pressure (psia), inspired FO₂, activity level, ambulation flag, exercise pre-breathe flag                                   |
| `truth.parquet`                         | 1,053  | 8    | Ground-truth tissue nitrogen kinetics per branch: tissue N₂ tension (mmHg), Tissue Ratio (TR), TR cumulative peak, controlling compartment, bubble load, minute of first bubble    |
| `group_frequency_reproduction.parquet`  | 6      | 7    | The six published incidence rates from the source study vs. what this dataset reproduces — deviation \<0.0023                                                                      |
| `counterfactual_effect_summary.parquet` | 6      | 10   | For every branch pair, the percentage of subjects who flip high-VGE status when moved between branches                                                                             |
| `validation_checks.parquet`             | 9      | 6    | Every structural and physical invariant check — machine-readable PASS/FAIL with detail                                                                                             |
| `audit_constants.csv/.parquet`          | 59     | 14   | Every physiological constant used in generation: source citation, tier (VERIFIED / DERIVED_CALIBRATED / ASSUMPTION_STRUCTURAL), verification date                                  |
| `literature_registry.csv`               | 12     | 11   | All 12 source references with what each was used for                                                                                                                               |
| `benchmark_results.parquet`             | 11     | 7    | 5-fold cross-validation results for both benchmark tasks, including the theoretical Bayes-ceiling reference row                                                                    |

### How the data was generated

The generative core is a **single-compartment, perfusion-limited Haldane nitrogen-washout model**. It computes Tissue Ratio (TR) — the ratio of dissolved tissue N₂ tension to ambient pressure — minute by minute across the full oxygen pre-breathe, staged intermediate-pressure phase, decompression ramp, and EVA at suit pressure. TR_peak, the maximum TR reached at the end of the ramp, is the single calibrated physiological driver of bubble-formation risk.

Two logistic regression stages sit on top of the physics: the first converts TR_peak into a VGE-grade probability (grades III–IV = "high VGE"); the second converts high VGE into a DCS incidence probability. Both stages are fitted to reproduce the Conkin 2017 published rates *exactly by construction* — not by curve-fitting to observed noise, but by solving for the logistic coefficients that yield those exact published numbers. A Patent Foramen Ovale (PFO, present in ~24.4% of subjects) enters as a relative-risk multiplier (RR≈2.65) on the DCS odds, calibrated to the Germonpré 2021 prospective carotid-Doppler study.

Every one of the 59 audited physiological constants is traceable to a published source and tagged by tier: 38 are VERIFIED (confirmed in peer-reviewed or institutional sources), 11 are DERIVED_CALIBRATED (fitted to reproduce published targets), and the remaining are ESTIMATE_SOURCED or ASSUMPTION_STRUCTURAL — all disclosed, none quietly invented.

### Benchmark results

| Task                                    | Model                 | Mean accuracy | AUC / kappa          | Note                                                                                                                                                                                                                                     |
|-----------------------------------------|-----------------------|---------------|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| A — binary high-VGE from branch + PFO   | Logistic regression   | 73.9%         | AUC 0.752            | Matches the Bayes-optimal ceiling to 4 decimal places — the model recovered the generating function exactly. The gap to 100% is irreducible sampling noise.                                                                              |
| A — theoretical ceiling                 | True cell probability | 73.9%         | AUC 0.752            | Maximum any classifier using only these two inputs could ever reach                                                                                                                                                                      |
| B — 5-level VGE grade from branch + PFO | Gradient boosting     | 41.8%         | Weighted kappa 0.344 | Ceiling is deliberately well below 100% — the fine grade split (0 vs I vs II vs III vs IV) is a structural random draw within the high/low binary cut. Resolving the fine grade requires a real Doppler signal, not exposure covariates. |

### Key variables

| Column                  | Table                         | Description                                                                                                                                                              |
|-------------------------|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `subject_id`            | crew, obs, outcomes           | Integer 1–10,000. The join key across all subject-level tables.                                                                                                          |
| `branch_group`          | obs, outcomes, profile, truth | One of: control / group2_pre_only / group1_during_supersaturation                                                                                                        |
| `pfo_present`           | crew                          | Boolean. PFO prevalence 24.4% (Koutroulou et al. 2020 autopsy-series rate)                                                                                               |
| `high_vge`              | outcomes                      | Boolean. VGE grade III–IV. The primary binary outcome; the generating model is calibrated to this variable directly.                                                     |
| `vge_grade`             | observations                  | Integer 0–4. Spencer/Kissman Doppler scale. Grades III–IV are high_vge=True.                                                                                             |
| `dcs_pain_only`         | outcomes                      | Boolean. Type I DCS (joint/musculoskeletal pain). Rates: 0% / 5% / 20% by branch.                                                                                        |
| `dcs_neurological`      | outcomes                      | Boolean. Type II DCS. Always False in this dataset — two independent sources (Conkin 2017 + NASA OCHMO-TB-037) confirm zero neurological events for this protocol class. |
| `tissue_ratio`          | truth                         | Minute-by-minute Haldane TR. The key physiological intermediate linking the protocol to VGE outcomes.                                                                    |
| `counterfactual_set_id` | outcomes                      | Groups the three rows (one per branch) that share the same underlying random draw for one subject — the join key for within-subject counterfactual analysis.             |

### Validation

**ALL_PASS = true.** All 9 structural, physical, and calibration-reproduction checks passed against the actual delivered files — not against a target typed to match. This includes tissue-tension bounds, degenerate-limit tests, step-size independence (TR_peak stable to 6 significant figures across dt ∈ {0.2, 0.1, 0.05, 0.02}), null-pattern checks, shape and range checks, coherence (DCS implies high VGE; neurological DCS always False; exactly one factual row per subject), and truth/observation separation (no true-physiology column leaks into observations or outcomes). The machine-readable results are in `validation_checks.parquet`.

### Known limitations — disclosed, not buried

- **profile and truth are branch-keyed, not subject-keyed.** The validated physics model has no sourced mechanism for individual variation in tissue nitrogen kinetics. Every subject on the same branch follows the identical protocol and compartment half-time. All subject-level variation lives in the Bernoulli outcome draw (outcomes/observations).
- **The fine VGE-grade split is a structural convenience.** The 5-level Spencer scale is reproduced in `vge_grade`, but only the binary high/not-high cut is covariate-determined. Grades within each side of that cut are a random draw by design — the fine split carries no calibration weight and cannot be predicted from exposure covariates alone.
- **body_fat_pct and BMI carry no causal weight.** A published negative result (Schellart et al. 2012) found no significant correlation with bubble grade; these fields are included as descriptive demography only.
- **prior_dcs_history and hydration_state are descriptive only.** No sourced mechanism linking either to this model's outcome was found in the literature search for this release.
- **12 literature references.** The dataset falls short of a 40-source depth bar — disclosed directly rather than rounded past.

### Intended use cases

- Causal-inference method development — the only dataset that provides a true within-subject counterfactual on the same random draw for a physiological outcome
- DCS / VGE risk-model benchmarking with a known, reproducible generating function
- Aerospace medicine education and protocol comparison
- ML model development for tabular physiological outcomes
- Testing uplift / heterogeneous-treatment-effect estimators in a ground-truth setting

*This dataset is a synthetic simulation product generated from a calibrated decompression-sickness model. It does not contain real astronaut, diver, or patient data. It is built for ML/CV development, benchmarking, and education — not for clinical, operational, or flight-readiness decisions.*

## Reproducing the validation on the sample

`validation/benchmark_script.py` is the script used for the published benchmark, reproduced here **unmodified** from the dataset's validation package. It runs two tasks: Task A predicts the binary high-VGE label with logistic regression, Task B predicts the five-class VGE grade with gradient boosting, both with 5-fold cross-validation.

**Published result, full dataset:**

- Validation checks passed: 9/9
- Calibration reproduction deviation: <0.0023
- Benchmark Task A (binary high_vge, logistic regression, 5-fold CV, seed 20261027): accuracy 73.87%, AUC 0.7516
- Benchmark Task B (5-class vge_grade, gradient boosting, 5-fold CV): accuracy 41.8%, weighted kappa 0.344

**Note on the published result.** Task A (binary high_vge prediction from branch_group + pfo_present): AUC 0.7516 matches the Bayes ceiling to 4 decimal places. This is an artifact of construction — these two covariates fully determine the generating Bernoulli probability for high_vge in the calibrated model. The gap to 1.0 is irreducible sampling noise, not a modeling shortfall.

Task B (5-class vge_grade from the same two covariates, gradient boosting): accuracy 41.8%, weighted kappa 0.344. The fine grade split within each binary side is an undisclosed random draw by design — resolving it requires an actual Doppler bubble-detection signal, not exposure covariates alone. Task B's ceiling is itself the honest result.

**What `notebook/validate_sample.ipynb` does.** The notebook loads the script as a module, points its `DATASET` and `OUT` settings at the sample and a temporary directory, and calls `main()`. The notebook is executed, with its outputs saved in the file, and writes nothing into the repository.

**What it produced on the sample.** On 120 rows the folds are 24 rows each. Task A reaches a mean AUC of 0.646 against a ceiling of 0.673 for these rows; Task B reaches a mean accuracy of 0.358. The published full-dataset values are AUC 0.7516 and accuracy 41.8% with weighted kappa 0.344.

Figures computed on the sample are **not** a benchmark of the dataset and should not be quoted; the numbers to cite are the published full-dataset ones above. `validation/requirements.txt` pins the package versions the notebook was executed with.

## Licensing

This free sample (data, script and notebook) is released under **CC BY-NC 4.0**: non-commercial use is permitted with attribution. The full dataset is sold under a commercial research license; see the [dataset page](https://sentineldata.com.ua/dataset/eva-dcs-risk) and the [licence terms](https://sentineldata.com.ua/dataset-license).

## Citation

> Code Sentinel Data, Chekerskyi, M. (2026). *EVA Decompression Sickness Risk Dataset*. Zenodo. https://doi.org/10.5281/zenodo.23840239

## Links

- Full dataset and passport: https://sentineldata.com.ua/dataset/eva-dcs-risk
- Zenodo record (DOI): https://doi.org/10.5281/zenodo.23840239
- OSF: https://doi.org/10.17605/OSF.IO/TB458