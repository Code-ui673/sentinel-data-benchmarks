# Combat Amputation and Prosthetic Rehabilitation Dataset (CAPR) — free sample

> **This folder contains the validation code, the published benchmark results and a free evaluation sample (500 of 15,000 patients) — not the full dataset.**
> **Full dataset (15,000 patients, 10 linked tables, OMOP CDM export):** **[sentineldata.com.ua/dataset/capr-combat-amputation-prosthetic-rehabilitation](https://sentineldata.com.ua/dataset/capr-combat-amputation-prosthetic-rehabilitation)**

**DOI (Zenodo):** [10.5281/zenodo.24403459](https://doi.org/10.5281/zenodo.24403459)
**Also archived:** [Kaggle (free sample)](https://www.kaggle.com/datasets/corot7b/capr-combat-amputation-prosthetic-rehabilitation) · [Hugging Face (DOI 10.57967/hf/11732)](https://doi.org/10.57967/hf/11732)

**Status: MODEL-GENERATED / HYPOTHETICAL.** Fully synthetic data. No real service member stands behind any row. The dataset supports method development and benchmarking for amputation care, prosthetic prescription and rehabilitation analytics; it is not clinical evidence.

## What is in this folder

| Path | Content |
|---|---|
| `sample/` | 500 patients as Parquet and CSV: wide patient table, limbs, prostheses, longitudinal rehabilitation panel, and six OMOP tables, plus the sample passport PDF |
| `validation/benchmark_script.py` | The benchmark script exactly as shipped with the full dataset (unmodified) |
| `validation/benchmark_results.parquet` | Results of that script on the full 15,000-patient cohort |
| `validation/validation_report_EN.pdf` | Validation report |
| `validation/requirements.txt` | Package versions used to run the notebook |
| `notebook/validate_sample.ipynb` | Executed notebook: runs the script on the sample and compares the output with the published full-cohort numbers |

## Published benchmark results (full cohort)

| Task | Accuracy | Balanced accuracy | ROC AUC |
|---|---|---|---|
| A1: K-level, 4 classes | 0.822 | 0.763 | n/a |
| A2: K2 vs K3 | 0.966 | 0.848 | 0.977 |
| B: return to duty from intake data | 0.917 | 0.725 | 0.899 |
| C: chronic pain from early data | 0.778 | 0.621 | 0.704 |

Task A2 is close to circular by construction: the K-level and the functional tests come from one generated continuum. Read it as a pipeline check. The report discusses this in detail.

## Running the sample yourself

1. Install the packages: `pip install -r validation/requirements.txt`
2. Open `notebook/validate_sample.ipynb` and run all cells.

The script expects `../DATASET/capr_wide_patients.parquet` and `../DATASET/capr_longitudinal_rehab.parquet`. The sample files have a `_sample_` infix, so the notebook copies them under the expected names into a temporary folder. The script itself is not touched.

With 500 patients the folds are small and the metrics move noticeably from fold to fold. The sample run shows that the pipeline works and what the data looks like. It does not estimate full-cohort performance.

## The full dataset

Fifteen thousand synthetic service members with combat-related limb loss, followed from injury profile and amputation pattern through surgery, prosthesis prescription, functional recovery, a pain panel and service or vocational outcomes. Ten linked tables plus an OMOP CDM export. The **dataset passport** (PDF on the dataset page) holds the schema, calibration sources and provenance in far more detail than any description does; reading it before buying is worth the ten minutes.

## Citation

Chekerskyi, M. (2026). *Combat Amputation and Prosthetic Rehabilitation Dataset (CAPR)* [Data set]. CODE SENTINEL DATA. https://doi.org/10.5281/zenodo.24403459

## License

CC BY-NC 4.0 for the sample and the code in this folder. The full dataset is sold under the license stated on the dataset page.
