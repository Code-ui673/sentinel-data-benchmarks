# Post-Landing Orthostatic Intolerance Dataset — free sample

> **This repository contains the full technical documentation and a free evaluation sample (32 of 10,000 subjects) — not the full dataset.**
> **Full dataset (10,000 subjects, 10 linked tables):** **[sentineldata.com.ua/dataset/post-landing-orthostatic-intolerance](https://sentineldata.com.ua/dataset/post-landing-orthostatic-intolerance)**

10,000 virtual astronauts, 10-minute head-up tilt test immediately after landing, mechanistic cardiovascular simulation (Ursino-Magosso variant). Noisy monitor observations, unobserved ground-truth physiology, paired factual/counterfactual outcomes, four countermeasure arms. Built for orthostatic-intolerance (OI) classification, hemodynamic monitoring research and countermeasure evaluation.

**DOI (Zenodo):** [10.5281/zenodo.23816244](https://doi.org/10.5281/zenodo.23816244)
**Also archived:** [OSF](https://doi.org/10.17605/OSF.IO/XF6ZS)

**Status: MODEL-GENERATED / HYPOTHETICAL.** This is fully synthetic data from a mechanistic simulation, not recordings of real astronauts or patients. It supports benchmarking, algorithm development and countermeasure-research prototyping; it is not clinical evidence and is not a substitute for real flight-surgeon data.

## Sample contents

This repository ships a true row-level subset of the full dataset (same seed `20261027`, same generation pass, selected by `subject_id` — not a separate generation run).

| File | Rows × Cols | Content |
|---|---:|---|
| `sample/crew.parquet` / `.csv` | 32 × 7 | Subject demographics and mission profile — same schema as the full dataset |
| `sample/observations.parquet` / `.csv` | 5,312 × 8 | Noisy monitor readings (beat-to-beat BP, ECG HR, symptom/dropout flags) at 2-second resolution, for the 32-subject sample |
| `sample/truth.parquet` / `.csv` | 9,632 × 11 | Unobserved ground-truth physiology (MAP, HR, SV, CO, TPR, plasma volume deficit, contractility index) at 1-second resolution, for the 32-subject sample |
| `sample/outcomes.parquet` / `.csv` | 64 × 9 | Factual + counterfactual outcome per subject (2 rows each): presyncope, tolerance time, recovery days |
| `sample/sample_passport_EN.pdf` | — | Sample data passport |
| `sample/sample_manifest.json` | — | Per-file SHA-256, build environment, generator kernel hash |
| `sample/working_with_parquet.txt` | — | How to open the Parquet files (pandas / R arrow / DuckDB) |

The full dataset additionally ships `population_timeseries_summary`, `countermeasure_comparison_summary`, `validation_checks`, `audit_constants`, `literature_registry` and `benchmark_results` — not included in this sample, see the full dataset page.

## Validation / benchmark

`validation/benchmark_script.py` is the exact script run against the full 10,000-subject dataset — reproduced here unmodified. It predicts `outcomes.presyncope` from observation-layer features only (never from ground truth), in two tasks:

- **Task A — during-test detection.** Near-perfect by construction (presyncope is *defined* as MAP crossing a threshold, and `beat_to_beat_bp` is a direct noisy observation of that same signal). Reported for transparency, not as a meaningful result.
- **Task B — pre-test crew screening.** The commercially relevant number: predicting presyncope from crew covariates alone, *before* any tilt-test reading exists — the real flight-surgeon triage question.

**Published result, full dataset (n=10,000, 5-fold CV, logistic regression):** Task B AUC = **0.779**, accuracy = 80.9%. Real-world reference (not a like-for-like comparison, included per the project's own validation doctrine): Hart et al. (2021), *Classification of orthostatic intolerance through data analytics*, Med Biol Eng Comput 59(3), DOI [10.1007/s11517-021-02314-0](https://doi.org/10.1007/s11517-021-02314-0), >95% accuracy classifying real patients by OI subtype using a different feature set and population — cited as evidence this class of physiological signal is predictable at all, not as a target this benchmark should match.

`notebook/validate_sample.ipynb` runs this same script against the 32-subject sample in this repo, as a reproducibility smoke test. **The AUC/accuracy numbers it produces on n=32 are not statistically meaningful** (5-fold CV on 32 subjects means ~6 test subjects per fold) and should not be quoted — only the published n=10,000 numbers above are the real benchmark. The notebook exists to prove the code runs end-to-end against the delivered schema, not to reproduce the published metric at sample scale.

## Known limitations

- Compression-garment and LBNP countermeasure arms are modelled descriptively — no quantitative hemodynamic effect is applied; don't use them to evaluate countermeasure efficacy.
- No cerebral autoregulation component; presyncope triggers on a MAP threshold alone.
- No numerical cross-validation against the Heldt CVSim (PhysioNet) reference implementation.
- Full list and rationale: see the [full dataset page](https://sentineldata.com.ua/dataset/post-landing-orthostatic-intolerance), section "Known Limitations".

## Licensing

This free sample (data + script + notebook) is released under **CC BY-NC 4.0** — non-commercial use permitted with attribution. The full 10,000-subject dataset is sold under a commercial research license; see the [dataset page](https://sentineldata.com.ua/dataset/post-landing-orthostatic-intolerance) and [licence terms](https://sentineldata.com.ua/dataset-license).

## Citation

> Code Sentinel Data, Chekerskyi, M. (2026). *Post-Landing Orthostatic Intolerance Dataset*. Zenodo. https://doi.org/10.5281/zenodo.23816244

## Links

- Full dataset & passport: https://sentineldata.com.ua/dataset/post-landing-orthostatic-intolerance
- Zenodo record (DOI): https://doi.org/10.5281/zenodo.23816244
- OSF mirror: https://doi.org/10.17605/OSF.IO/XF6ZS
