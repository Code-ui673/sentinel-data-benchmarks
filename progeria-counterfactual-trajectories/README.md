# Progeria Counterfactual Trajectories: free sample

> **This folder contains the technical documentation, the validation code and a free evaluation sample (200 of the 10,000 children, every table of the full dataset). It is not the full dataset.**
> **Full dataset (10,000 children, 6 treatment worlds, 8 Parquet tables):** **[sentineldata.com.ua/dataset/progeria-counterfactual-trajectories](https://sentineldata.com.ua/dataset/progeria-counterfactual-trajectories)**

Progeria makes children age far too fast, and only a few dozen are alive at any moment, so nobody can run a trial with many arms or watch the same child once with a drug and once without. This dataset builds that missing view. It holds 10,000 invented children with Hutchinson-Gilford progeria, and each one lives six times: untreated, with lonafarnib from the usual age, with lonafarnib from diagnosis, with lonafarnib plus everolimus, and with a progerin-lowering treatment started at diagnosis or at twelve years. The body and the random numbers are the same in all six lives, so the difference between two lives is the treatment and nothing else.

Next to the clinic record (weight, height, artery stiffness, skin biopsies, a yearly blood panel, outcomes) sits a hidden truth layer: the true disease state every half-year in every world and the age at death in all six worlds. You build your estimate on the observed tables, then check it against the truth tables.

**DOI (Zenodo):** [10.5281/zenodo.24352098](https://doi.org/10.5281/zenodo.24352098)
**Also available:** [Kaggle (free sample)](https://www.kaggle.com/datasets/corot7b/progeria-counterfactual-trajectories)

**Status: MODEL-GENERATED / HYPOTHETICAL.** All children are synthetic. No real patient stands behind any row. The data supports benchmarking and method development. It is not clinical evidence and shows nothing about whether any treatment works in a real child.

The sample passport in `sample/` explains every table. The full dataset passport (on the dataset page and on Zenodo) holds much more: the log of all 30 checks, the twelve registered predictions, all 89 parameters with their sources and a worked example.

## What the data are good for

- **Causal-effect estimation with a known answer.** Every child lives all six worlds, so the true effect of a treatment is a subtraction in the truth tables. Observed arms recover 0.60 months of extra survival over five years in the full dataset, the truth says 1.20, and that gap is what a method has to explain.
- **Biomarker pipelines.** Farnesylated progerin in a skin biopsy separates treated from untreated children (AUC 0.976). Carotid-femoral pulse wave velocity hardly does (AUC 0.560). A method can be tested on which of the two it trusts.
- **Two stiffness markers that disagree.** Carotid-femoral PWV is about twice the control while local carotid stiffness stays close to healthy children (ratios 2.26 and 1.02), as in the source papers.
- **Planning studies on very few patients** and **teaching survival analysis** with an answer key.

It is not a mortality benchmark. Death follows from a random tolerance each child carries, so even the hidden damage index reaches an AUC of only 0.58 for death within 24 months.

## Sample contents

A true row-level subset of the full dataset: 100 girls and 100 boys, all tables, all six worlds, nothing recomputed.

| Path | Rows | Content |
|---|---:|---|
| `sample/observed/patients.parquet` | 200 | Sex, age at diagnosis, index age, treatment received and its start age |
| `sample/observed/outcomes.parquet` | 200 | Follow-up, death flag, age at death |
| `sample/observed/visits.parquet` | 4,595 | Weight, height, PWV, local carotid beta, ankle-brachial index, diastolic dysfunction flag, drug flags |
| `sample/observed/skin_biopsies.parquet` | 219 | Farnesylated progerin, lamin A, six fibroblast transcript modules |
| `sample/observed/plasma_panel.parquet` | 2,351 | Five plasma protein module scores, once a year |
| `sample/truth/patients.parquet` | 200 | Factual world, progerin production multiplier, death tolerance, treatment efficiency |
| `sample/truth/world_outcomes.parquet` | 1,200 | Age at death in each of the six worlds |
| `sample/truth/latent_states.parquet` | 27,930 | Hidden state per child, world and half-year |
| `sample/data_dictionary.csv`, `manifest.csv` | | Every column documented, SHA-256 per file |
| `sample/progeria-counterfactual-trajectories_sample_passport_EN.pdf` | | Sample data passport |
| `sample/parquet_howto.txt` | | How to read the Parquet files |

Join every table on `patient_id`. The truth tables add the keys `world` (W0 to W5) and `age_months`. The full dataset has 220,970 visits and 1,336,920 hidden-state rows for 10,000 children.

## Validation / benchmark

`validation/benchmark_script.py` is the exact script that produced the published numbers on the full dataset, reproduced here unmodified. It reads features from `observed/`, labels and counterfactual references from `truth/`, and prints every row with a bootstrap interval. The preregistration SHA-256 is in the script header.

**Published results, full dataset (10,000 children, master seed 20261109):**

| Task | Value | n | 95% interval |
|---|---:|---:|---|
| A. Restricted mean survival, 60 months from the index age, treated minus untreated, observed arms (months) | 0.600 | 3,919 | |
| A. Same quantity from the counterfactual truth (months) | 1.204 | 3,919 | |
| B. Progerin in the skin biopsy, AUC for lonafarnib at the index age | 0.976 | 3,410 | 0.971 to 0.980 |
| B. Carotid-femoral PWV, same task, AUC | 0.560 | 5,769 | 0.546 to 0.573 |
| C. Death within 24 months, age only, AUC | 0.551 | 112,975 | 0.546 to 0.555 |
| C. Age and PWV, AUC | 0.563 | 112,975 | 0.558 to 0.568 |
| C. Age, PWV, weight and treatment flag, AUC | 0.566 | 112,975 | 0.561 to 0.571 |
| C. Hidden damage index, the upper reference, AUC | 0.582 | 112,975 | 0.577 to 0.587 |

The same table is in `validation/benchmark_results_readable.csv`, the raw output in `validation/benchmark_results.parquet`. `validation/validation_report_EN.pdf` is the full validation report: 30 automatic checks, all passing. Twelve predictions were written down before the first full run. **Eight passed and four failed.** The four failures concern how much lonafarnib lowers death and how much progerin lowering adds, and they are reported with their numbers in the passport, not adjusted afterwards.

### Re-running the benchmark on the sample

`notebook/validate_sample.ipynb` runs the same script, unmodified, against the 200-child sample (executed output is stored in the notebook). It is a reproducibility smoke test only. With 200 children some groups hold 70 to 115 rows and the observed-arm survival estimate can even change sign, so these numbers are noisy and must not be quoted. Only the published numbers above are the real benchmark.

```bash
pip install -r validation/requirements.txt
python validation/benchmark_script.py sample benchmark_results_sample.parquet
```

## Known limitations

- **Lonafarnib lowers death less than the two clinical papers report.** The treated death share in the 5.3-year emulation is 0.325 against 11.6% published. The published risk reduction and the published 1.6-year gain cannot both be reached by one mechanistic model, so the gain was calibrated and the death shares were held out.
- **Progerin lowering from diagnosis adds about 13% of life.** Mouse studies report +84.5% and +137%.
- **Everolimus and progerin lowering are hypotheses.** Their sizes were chosen by design and are marked that way.
- **Progerin dynamics in living children are not published.** Hidden trajectories are model quantities marked DESIGN.
- **Classic mutation only.** Non-classic forms and progeroid laminopathies are not modelled.
- **Randomised in silico.** The factual world is independent of every hidden variable, so there is no confounding here. Real non-randomised comparisons are biased more strongly.
- **Horizon and censoring.** Observation stops at 20 years and truth at 40.
- Full list and rationale: the [dataset page](https://sentineldata.com.ua/dataset/progeria-counterfactual-trajectories) and the validation report.

## Licensing

This free sample (data, script and notebook) is released under **CC BY-NC 4.0**: non-commercial use permitted with attribution. The full 10,000-child dataset is sold under a commercial research license; see the [dataset page](https://sentineldata.com.ua/dataset/progeria-counterfactual-trajectories) and the [licence terms](https://sentineldata.com.ua/dataset-license).

## Citation

> Code Sentinel Data, Chekerskyi, M. (2026). *Progeria Counterfactual Trajectories*. Zenodo. https://doi.org/10.5281/zenodo.24352098

## Links

- Full dataset and passport: https://sentineldata.com.ua/dataset/progeria-counterfactual-trajectories
- Zenodo record (DOI): https://doi.org/10.5281/zenodo.24352098
- Kaggle (free sample): https://www.kaggle.com/datasets/corot7b/progeria-counterfactual-trajectories
