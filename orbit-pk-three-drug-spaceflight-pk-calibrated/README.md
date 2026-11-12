# ORBIT-PK: THREE-DRUG SPACEFLIGHT PK CALIBRATED — free sample

> **This repository folder contains the technical documentation, validation code and a free evaluation sample (600 of 105,000 subjects, 100 per group) — not the full dataset.**
> **Full dataset:** **[sentineldata.com.ua/dataset/orbit-pk-three-drug-spaceflight-pk-calibrated](https://sentineldata.com.ua/dataset/orbit-pk-three-drug-spaceflight-pk-calibrated)**

105,000 simulated adults on three real drugs (acetaminophen, scopolamine, zolpidem), oral and transdermal patch, with a flight arm calibrated against the real in-flight studies that exist for each drug. Six Parquet tables put exact noise-free PK parameters next to noisy 12-point concentration curves. 41 of 41 structural checks passed, and the literature benchmark publishes its two failures.

**DOI (Zenodo):** [10.5281/zenodo.24018154](https://doi.org/10.5281/zenodo.24018154)  
**Also archived:** [OSF](https://doi.org/10.17605/OSF.IO/HKNU8) · [Harvard Dataverse](https://doi.org/10.7910/DVN/REUM3L)

**Status: MODEL-GENERATED / SYNTHETIC.** This is fully synthetic data from a pharmacokinetic simulation, not measurements from real astronauts or volunteers. It supports benchmarking, algorithm development and mission-planning research prototypes; it is not clinical or dosing evidence.

## Sample contents

| File | Rows × Cols | Content |
|---|---:|---|
| `sample/observations_sample.parquet` | 7,200 × 3 | Concentration-time observations (7,200 rows across 600 subjects) |
| `sample/outcomes_sample.parquet` | 600 × 12 | Outcome table with reference-interval bounds taken from the full dataset's ground arm |
| `sample/schema.csv` | 51 × 6 | Column listing for the six tables |
| `sample/subjects_sample.parquet` | 600 × 7 | Subject covariates and drug/route/arm assignment (600 subjects) |
| `sample/truth_pk_metrics_sample.parquet` | 600 × 6 | Ground-truth derived PK metrics (Cmax, Tmax, terminal half-life and others) |
| `sample/truth_pk_parameters_sample.parquet` | 600 × 15 | Ground-truth individual PK parameters (CL, V1, Q, V2 and others) |
| `sample/zolpidem_multidose_steady_state_sample.parquet` | 100 × 8 | Zolpidem multidose steady-state rows (100 subjects) |
| `sample/sample_passport_EN.pdf` | — | Sample data passport |
| `sample/working_with_parquet.txt` | — | How to open the Parquet files (pandas / R arrow / DuckDB) |

The free sample holds 600 subjects, 100 from each of the six groups, as the first 100 rows of each group in the full tables. It is sliced out of the real Parquet files and not re-simulated, and the build script asserts exact equality with the full dataset for the same subject IDs. It contains the same six tables in the same column layout (7,200 observation rows, 100 zolpidem multidose rows), with `schema.csv` and a short guide to opening Parquet. Reference-interval bounds in the sample's outcomes table come from the full dataset's ground arm, not from the 100-subject groups, and 100 subjects per group is enough to check shapes and ranges but not to reproduce the full dataset's medians.

## About the dataset

The text below is the dataset's description from the product page, converted to Markdown.

When an astronaut swallows an ordinary tablet in orbit, does the drug behave the way it does on the ground? The published answer is mixed. Four in-flight acetaminophen comparisons exist, and they disagree about both the direction and the size of the microgravity effect. ORBIT-PK is a synthetic pharmacokinetic dataset built around that disagreement: 105,000 simulated adults, three real drugs (acetaminophen, scopolamine and zolpidem), two routes of administration, and a flight arm calibrated against the real spaceflight studies that exist for each drug.

Each subject is one instance of an explicit two-compartment model, solved exactly by matrix exponentiation. A subject carries a full set of exact, noise-free pharmacokinetic parameters (ka, F, CL, V1, Q, V2), the true summary metrics computed from them (Cmax, Tmax, AUC, half-life), and a sparse twelve-point blood-concentration curve with measurement noise added on top. The truth tables sit next to the noisy observations, so you can fit a model to the observations and then check the result against the parameters that generated them. Real flight data almost never allows that.

For acetaminophen, every simulated flight subject is assigned one of the four real in-flight perturbation triples (absorption rate, bioavailability, clearance) and keeps it. No averaged consensus effect is invented. Where the literature has no in-flight measurement at all, as for zolpidem and for the scopolamine patch, the dataset ships a ground arm only and says so.

**Status: model-generated.** The dataset is fully synthetic. No real crew member or patient appears in any row. Every number is the output of a published, cited model, and it must not be used for clinical dosing decisions for any real patient or crew member. The reference intervals inside `outcomes.parquet` are descriptive statistics computed from the dataset's own ground arm, and they are not safety limits or toxicity thresholds.

### At a glance

| Item            | Value                                                                                                                         |
|-----------------|-------------------------------------------------------------------------------------------------------------------------------|
| Subjects        | 105,000 simulated adults, joined across all tables by `subject_id` (format SSPK-NNNNNN)                                       |
| Drugs           | 3: acetaminophen, scopolamine, zolpidem                                                                                       |
| Routes          | Oral (all three drugs) and transdermal patch (scopolamine only)                                                               |
| Arms            | GROUND for every drug and route; FLIGHT for oral acetaminophen and oral scopolamine                                           |
| Tables          | 6 Apache Parquet files, 1,260,000 rows in the largest one, plus `schema.csv` with type, unit and description for every column |
| Observations    | 12 noisy concentration points per subject: 0.25 to 24 h for oral, 2 to 96 h for the patch                                     |
| Ground truth    | Exact noise-free PK parameters and summary metrics for every subject, kept in separate tables                                 |
| Literature base | 42 cited sources; an audit table of 44 model constants, none of them an unsourced estimate                                    |
| Validation      | 41 of 41 structural checks passed; 8 of 10 published-literature benchmarks passed and 2 are disclosed failures                |
| Random seed     | 20261028 (deterministic generator)                                                                                            |
| Edition         | 2.0, validation re-run 2026-10-29 against the delivered files                                                                 |
| Free sample     | 600 subjects, 100 from each of the six drug, route and arm groups, sliced bit-identically from the full tables                |

### The six tables

All six tables share the key `subject_id`. The truth tables and the observation table are kept apart on purpose: `observations.parquet` contains no column that ends in `_true`, and none of the sampled observation points is bit-identical to the noise-free curve.

| Table                                     | Rows      | What it holds                                                                                                                                                                |
|-------------------------------------------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `subjects.parquet`                        | 105,000   | One row per subject: drug, route, arm, dose, body weight, age.                                                                                                               |
| `truth_pk_parameters.parquet`             | 105,000   | Exact PK parameters (ka, F, CL, V1, Q, V2) and the microgravity perturbation factors that were actually applied, with the real study each flight subject was resampled from. |
| `truth_pk_metrics.parquet`                | 105,000   | Exact summary metrics: Cmax, Tmax, AUC to infinity, terminal rate constant, half-life.                                                                                       |
| `observations.parquet`                    | 1,260,000 | Twelve blood-concentration points per subject with proportional measurement noise, clipped at zero.                                                                          |
| `outcomes.parquet`                        | 105,000   | Cmax and AUC of each subject set against a reference interval computed per drug and route from this dataset's own ground arm.                                                |
| `zolpidem_multidose_steady_state.parquet` | 30,000    | One row per zolpidem subject: steady-state Cmax, Cmin and AUC after seven nightly doses, plus an observed and a theoretical accumulation ratio.                              |

### Drug, route and arm groups

| Drug          | Route             | Arm    | Subjects | In-flight calibration                                  |
|---------------|-------------------|--------|----------|--------------------------------------------------------|
| Acetaminophen | Oral              | GROUND | 15,000   | Baseline                                               |
| Acetaminophen | Oral              | FLIGHT | 15,000   | Four real in-flight comparisons, resampled per subject |
| Scopolamine   | Oral              | GROUND | 15,000   | Baseline                                               |
| Scopolamine   | Oral              | FLIGHT | 15,000   | One real in-flight comparison (Cintron 1987b)          |
| Scopolamine   | Transdermal patch | GROUND | 15,000   | No published in-flight data, ground arm only           |
| Zolpidem      | Oral              | GROUND | 30,000   | No published in-flight data, ground arm only           |

Doses are fixed per drug and route: 650 mg acetaminophen, 0.4 mg oral scopolamine, 1.0 mg scopolamine delivered by the patch over 72 hours, and 10 mg zolpidem, as they appear in the free sample and the validation documents.

### Model structure

Oral subjects follow a linear two-compartment model with first-order absorption: a gut compartment feeds a central blood compartment, which exchanges drug with a peripheral compartment at rate Q. The system is solved at every time point by matrix exponentiation. That is the exact analytic solution of a linear system, so there is no step-size error of the kind Euler or Runge-Kutta integrators carry.

The scopolamine patch has no absorption step and no bioavailability term. It is modelled as a constant zero-order infusion into the central compartment for the length of wear (1 mg over 72 hours), solved exactly by variation of parameters. An early draft used a per-step bolus approximation. It passed the mass-balance tolerance at 0.334% error, the non-zero residue prompted a review, and the exact solution replaced it (0.000% now).

Scopolamine and zolpidem come from sources that report a one-compartment model. For those two drugs the two-compartment structure is driven to the exact limit of one compartment, with intercompartmental clearance set numerically large and peripheral volume set numerically small. The audit table records this as a structural device and not as a literature constant, and it agrees with the closed-form one-compartment solution to within 0.1%.

Mass is conserved for every subject. For oral subjects AUC times clearance equals dose times bioavailability, and for patch subjects it equals the total delivered dose. The 2026-10-29 re-run found a maximum relative error of 0.21% over all 90,000 oral subjects and 0.00% over all 15,000 patch subjects, against a tolerance of 1%.

### Microgravity calibration

#### Acetaminophen: four comparisons that disagree, kept as structure

For each real in-flight comparison, the perturbation triple (absorption-rate factor, bioavailability factor, clearance factor) was solved so that the model reproduces that study's own reported Cmax and Tmax ratios, with clearance fixed by the exact AUC-ratio mass balance. Three of the four fit to within 5 to 9% residual. Each flight subject then draws one of the four triples at random, plus small jitter sized from that study's own reported between-subject spread. The triples are never recombined into a combination that no real study reported.

| Source                               | Setting                               | Reported flight / ground ratio     | Fit to the model                                                                                             |
|--------------------------------------|---------------------------------------|------------------------------------|--------------------------------------------------------------------------------------------------------------|
| Cintron et al. 1987a (NASA TM-58280) | Space Shuttle, short missions, 650 mg | Cmax 11.40 / 10.78 = 1.057         | Reproduced, residual within 5 to 9%                                                                          |
| Kovachevich et al. 2009, tablets     | Long-duration flight, 500 mg          | Cmax 4.80 / 5.13 = 0.936           | Reproduced, residual within 5 to 9%                                                                          |
| Kovachevich et al. 2009, capsules    | Long-duration flight, 500 mg          | Cmax 4.17 / 5.00 = 0.834           | Reproduced, residual within 5 to 9%                                                                          |
| Polyakov et al. 2021, tablets        | Long-duration flight, 625 mg          | Cmax ratio 0.470, Tmax ratio 2.308 | Does not fit the three-parameter family; best achievable point kept, residual 35 to 40% on at least one axis |

The column `mission_duration_class` narrows the resampling. Cintron 1987a used short Shuttle missions, and the two long-duration studies are both titled, verbatim, "under long-term space flight conditions". Exact day counts for those two were not retrievable after a documented search (the full texts are paywalled), and that is recorded as a negative result and not filled in. In the sample, 48 of 100 flight subjects fall in the short class and 52 in the long class. The 50/50 split is a disclosed design choice, because no real frequency of short and long missions exists in the source studies' donor populations.

#### Scopolamine: one real comparison, calibrated as a point

Only one in-flight oral scopolamine comparison was found: Cintron et al. 1987b, as reproduced in Dello Russo et al. 2022, Table 1. Control Cmax was 406.33 ± 169.09 pg/mL (n = 3) against 375.25 ± 194.38 pg/mL in flight (n = 4). Control Tmax was 2.0 ± 0.82 h against 2.5 ± 1.06 h in flight. The flight perturbation is a point estimate solved from that comparison, with a spread built from the standard deviations the comparison itself reports. It reflects one study's variability and does not represent disagreement between studies, and the dataset says so.

#### Zolpidem and the patch: a documented negative search

Three independently varied searches for in-flight or bed-rest-analog zolpidem pharmacokinetics returned studies of how often crews use sleep aids, never a Cmax, Tmax or AUC measurement. The same discipline was applied to the scopolamine patch, including two NASA bed-rest reports on an intranasal scopolamine gel (a different formulation). Neither drug and route borrows another's flight calibration by analogy, so both ship GROUND only. The ground-based zolpidem model itself traces fully to a published population-PK paper.

### Covariates

| Drug          | Covariate handling                                                                                                                                                                                                                                                                                                                                | Source                           |
|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------|
| Acetaminophen | Body weight and age drawn from a truncated normal on the source range (mean 73 ± 13 kg, 49.2 to 120 kg; mean 46 ± 23 years, 19 to 88.5 years). Clearance scales as CL = CL_std × (weight/70)^0.75. Peripheral volume V2 is multiplied by 0.838 above 60 years. V1 has no weight term and sex is not applied, because the source retained neither. | Allegaert et al. 2014            |
| Scopolamine   | V1 = 1.4 L/kg × body weight (oral and patch). Clearance (65.3 L/h) stays an absolute value, since the source gives no per-kilogram clearance. Weight is drawn from the same population as acetaminophen, a disclosed substitution.                                                                                                                | Putcha et al. 1989               |
| Zolpidem      | No covariates. Body weight is a flat 70 kg for every subject, and age is empty. The source model tested sex, retained nothing, and could not assess other demographics; a second re-analysis agrees on sex.                                                                                                                                       | Cha et al. 2024; Kim et al. 2025 |

Age is filled for acetaminophen subjects only. In the sample it spans 19.7 to 87.6 years, and body weight spans 49.9 to 108.4 kg for acetaminophen and scopolamine.

### Observations, steady state and outcomes

**Observations.** Oral subjects are sampled at 0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8, 12 and 24 hours. Patch subjects are sampled at 2, 4, 8, 12, 24, 36, 48, 60, 72, 78, 84 and 96 hours, which covers the wear period and the decay after removal. The observed concentration is the true value with drug-appropriate proportional noise, clipped at zero.

**Zolpidem multi-dose.** Every zolpidem subject has one row with seven consecutive nightly doses, 24 hours apart. The table reports steady-state Cmax, Cmin and AUC over one interval, the observed accumulation ratio from the simulated curve and the theoretical ratio 1/(1 − exp(−λz · τ)). Zolpidem's half-life is short against the 24-hour interval, so both ratios sit close to 1: median observed 1.0021, median theoretical 1.0017 across all 30,000 subjects. That follows from the published half-life and was not assumed when the table was built.

**Outcomes.** For each subject, Cmax and AUC are divided by the midpoint of a 2.5th to 97.5th percentile reference interval computed per drug and route from the dataset's own ground arm, and each is labelled BELOW, WITHIN or ABOVE the interval. Oral and patch exposures are physically incomparable, so the reference interval is grouped by drug and route together. This was a defect in an early draft, caught in design review. No outcome column is a clinical verdict.

### Validation

Two scripts produce every figure in the validation report, and the dataset was re-checked against its delivered files on 2026-10-29. `validate_dataset.py` tests internal consistency. `benchmark_script.py` compares medians computed from the dataset's ground arm with independently published ranges that were not used to build the model. The two checks are reported separately and never blended into a single score.

#### Structural checks: 41 of 41 passed

| Category                      | Checks | What was found                                                                                                                                                                                                        |
|-------------------------------|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Completeness                  | 7      | 0 null cells outside the columns the schema declares nullable (age_years for scopolamine and zolpidem; ka_true and F_true for the patch).                                                                             |
| Shape and keys                | 7      | 105,000 unique subject_id values; expected row counts in every table, including 1,260,000 = 105,000 × 12 observations and 30,000 multidose rows.                                                                      |
| Column types                  | 3      | Truth, observation and demographic columns hold the numeric types the schema declares.                                                                                                                                |
| Physical ranges               | 12     | No negative clearance, volume or absorption rate; oral bioavailability inside (0, 1\]; weight std 11.95 kg over 75,000 distinct values; zolpidem weight exactly 70 kg; flight factors inside the calibrated envelope. |
| Cross-table coherence         | 5      | Subject sets match across all tables; drug, route and arm labels agree; zero zolpidem FLIGHT rows and zero patch FLIGHT rows.                                                                                         |
| Mass-balance invariants       | 2      | Maximum relative error 0.2056% over 90,000 oral subjects and 0.0000% over 15,000 patch subjects, tolerance 1%.                                                                                                        |
| Degenerate limit              | 1      | Every GROUND subject has all three perturbation factors exactly 1.0.                                                                                                                                                  |
| Truth and observation leakage | 2      | 0 of 3,295 sampled observation points are identical to the noise-free curve; the observation table has no \*\_true column.                                                                                            |
| Multi-dose consistency        | 2      | Stored accumulation ratio matches independent recomputation with 0.00e+00 difference; median observed ratio 1.0021.                                                                                                   |

#### Benchmark against published literature: 8 of 10 passed

| Metric (median, ground arm)                                    | Drug              | Dataset      | Published range       | Result              |
|----------------------------------------------------------------|-------------------|--------------|-----------------------|---------------------|
| Clearance CL                                                   | Acetaminophen     | 16.77 L/h    | 14.20 to 24.15 L/h    | PASS                |
| V1 + V2 per kg                                                 | Acetaminophen     | 0.62 L/kg    | 0.30 to 1.00 L/kg     | PASS                |
| Tmax                                                           | Acetaminophen     | 1.40 h       | 1.05 to 1.95 h        | PASS                |
| Terminal half-life                                             | Zolpidem          | 2.61 h       | 1.50 to 3.90 h        | PASS                |
| Tmax, oral                                                     | Scopolamine       | 2.04 h       | 1.40 to 2.60 h        | PASS                |
| Terminal half-life, oral                                       | Scopolamine       | 1.89 h       | 2.80 to 6.20 h        | **FAIL, disclosed** |
| Tmax                                                           | Zolpidem          | 0.90 h       | 0.75 to 2.60 h        | PASS                |
| Cavg, patch, windowed AUC(0 to 72 h)/72 h (500-subject sample) | Scopolamine patch | 209.78 pg/mL | 52.20 to 139.20 pg/mL | **FAIL, disclosed** |
| Flight / ground Cmax ratio, short-duration class               | Acetaminophen     | 0.77         | 0.53 to 1.90          | PASS                |
| Flight / ground Cmax ratio, long-duration class                | Acetaminophen     | 0.69         | 0.24 to 1.40          | PASS                |

The two failures were known structural limits before the report was written. A suite that never fails against an honest model built from sources that genuinely disagree would be the thing to distrust, so both are shown with their exact numbers.

#### The two disclosed failures

**Scopolamine half-life.** Putcha et al. 1989 report a terminal half-life of 4.5 ± 1.7 h, but only clearance and volume of distribution, with no two-compartment split. Run through a one-compartment reduction, that clearance and volume imply a half-life of about 1 h at the point estimate. The population median with full between-subject variability is 1.89 h, still below the paper's own range. Treat `t_half_true` for scopolamine as understating the real terminal phase, and consult the paper directly for that one quantity.

**Patch average concentration.** The FDA Transderm Scop label reports a mean free-scopolamine plasma concentration of about 87 pg/mL over the three-day wear period. The simulated patch subjects come out at 209.78 pg/mL, about 2.4 times higher. The patch shares the systemic clearance and volume of the oral route, which the label itself says are not well characterised for the transdermal route, and the model has no dermal depot compartment, so skin retention is not represented. The delivery rate was left at the label's own figure and was not lowered to force a match.

#### Defects found and fixed during the build

| Defect                                                                                                                                   | How it was found                                                             | Fix                                                                                          |
|------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| The observation sampler built a route-aware time grid but the loop still used the oral-only constant for every row, patch rows included. | Code review before any data was generated.                                   | A separate patch sampling grid and three corrected references.                               |
| The reference interval was grouped by drug alone, which would have judged every patch subject against an oral-scale band.                | Design review while adding the patch route.                                  | Grouping changed to drug and route throughout.                                               |
| Body weight was hard-coded to 70.0 kg in the subjects table, discarding the real per-subject draws.                                      | Code review of the main routine.                                             | The subjects table now takes weight and age from the truth table; the flat override is gone. |
| The first patch solver used a per-step bolus approximation.                                                                              | Mass-balance invariant: 0.334% error, inside tolerance but visibly non-zero. | Exact variation-of-parameters solution, now 0.000% error.                                    |

### Assumptions that are logged, not hidden

| Assumption                                                                                                             | Why                                                                                       | What to do if it matters to you                                                                               |
|------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| Short and long missions split 50/50 for flight acetaminophen subjects.                                                 | No real mission-mix frequency exists in the source studies' donor populations.            | Resample the two classes from `mission_duration_class` at your own ratio; the per-class triples stay valid.   |
| Scopolamine V1 scaling (1.4 L/kg) and the acetaminophen weight and age distribution are reused across all three drugs. | Neither the scopolamine nor the zolpidem source reports its own demographic distribution. | If your analysis is sensitive to between-drug demographic covariance, check this against your own population. |
| Zolpidem carries no weight or age covariate.                                                                           | The cited population-PK paper tested covariates and retained none.                        | Nothing to correct; this is the source's own finding.                                                         |
| The outcome reference interval is internal, computed per drug and route from the ground arm.                           | No independently captured toxicity threshold exists for this therapeutic-dose scope.      | Apply your own sourced threshold to the raw Cmax_true and AUC_true values.                                    |

### Literature base

The model runs on 42 cited sources, listed in full with PMID, DOI or URL in the Data Passport. An audit table covers 44 model constants, and each one is verified against a source, estimated with a citation, or tagged as a scan-design choice. None is an unsourced estimate. The main sources are:

- Allegaert K et al. 2014. Covariates of intravenous paracetamol pharmacokinetics in adults. BMC Anesthesiology 14:77. DOI 10.1186/1471-2253-14-77.
- Putcha L et al. 1989. Pharmacokinetics and oral bioavailability of scopolamine in normal subjects. Pharmaceutical Research 6(6):481-485. DOI 10.1023/A:1015916423156.
- Cha HJ et al. 2024. Development of a web application for simulating plasma drug concentrations in patients with zolpidem intoxication. Pharmaceutics 16(5):689. DOI 10.3390/pharmaceutics16050689.
- Cintron NM, Putcha L, Vanderploeg JM. 1987. Results of the Life Sciences DSOs conducted aboard the Space Shuttle 1981-1986. NASA TM-58280.
- Kovachevich IV et al. 2009. Pharmacokinetics of acetaminophen administered in tablets and capsules under long-term space flight conditions. Pharmaceutical Chemistry Journal 43(3):130-133. DOI 10.1007/s11094-009-0255-6.
- Polyakov AV et al. 2021. Study of the pharmacokinetics of various drugs under conditions of antiorthostatic hypokinesia and the pharmacokinetics of acetaminophen under long-term spaceflight conditions. Drug Metabolism and Personalized Therapy. DOI 10.1515/dmdi-2021-0159.
- Dello Russo C et al. 2022. Physiological adaptations affecting drug pharmacokinetics in space: what do we really know? British Journal of Pharmacology 179(11):2538-2557. DOI 10.1111/bph.15822.
- FDA label, Transderm Scop (scopolamine transdermal system), NDA 017874. Pensado-Lopez A et al. 2021, skin pharmacokinetics of transdermal scopolamine, Molecular Pharmaceutics.
- Salva P, Costa J. 1995. Clinical pharmacokinetics and pharmacodynamics of zolpidem. Clinical Pharmacokinetics 29(3):142-153. DOI 10.2165/00003088-199529030-00002.

### Key columns

Every column, with type, unit, origin and description, is in `schema.csv`. The main ones:

| Table                             | Columns                                                                                                                                                                                                                                                                                                  |
|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `subjects`                        | subject_id, drug, arm, route, dose_mg, body_weight_kg, age_years (7 columns)                                                                                                                                                                                                                             |
| `truth_pk_parameters`             | ka_true (1/h), F_true (fraction), CL_true (L/h), V1_true (L), Q_true (L/h), V2_true (L), f_ka_applied, f_F_applied, f_CL_applied, perturbation_source_study, mission_duration_class (15 columns). ka_true, F_true and the first two factors are empty for patch subjects, which have no absorption step. |
| `truth_pk_metrics`                | Cmax_true (mg/L), Tmax_true (h), AUC_true (mg·h/L), lambda_z_true (1/h), t_half_true (h) (6 columns)                                                                                                                                                                                                     |
| `observations`                    | subject_id, sample_time_h, concentration_observed (mg/L) (3 columns)                                                                                                                                                                                                                                     |
| `outcomes`                        | cmax and auc reference interval bounds, cmax_vs_reference_ratio, auc_vs_reference_ratio, cmax_outcome, auc_outcome (12 columns)                                                                                                                                                                          |
| `zolpidem_multidose_steady_state` | n_doses, tau_h, Cmax_steady_state, Cmin_steady_state, AUC_tau_steady_state, accumulation_ratio_observed, accumulation_ratio_theoretical (8 columns)                                                                                                                                                      |

The column `perturbation_source_study` names the real study behind each acetaminophen flight subject: `Cintron_1987a_650mg_n5`, `Kovachevich_2009_tablets_500mg_n5`, `Kovachevich_2009_capsules_500mg_n5` or `Polyakov_2021_tablets_625mg_n8v5`. Scopolamine oral flight subjects carry `Cintron_1987b_single_study`. Ground and no-flight-data subjects carry an N/A label that says which case applies.

### Who uses this data

- Aerospace-medicine and pharmacometrics researchers who need a labelled ground truth to test population-PK fitting pipelines, including how a fit behaves when the true flight effect is split between disagreeing studies.
- Engineers and data scientists building dosing, alerting or monitoring software for long missions, who need noisy, sparse, realistic concentration curves and not clean textbook ones.
- Instructors teaching population pharmacokinetics or space medicine who want a dataset large enough for real statistics, with every constant traceable to a citation.

## What is in the full delivery

The full delivery contains the six Parquet tables for 105,000 subjects, the complete schema, the Data Passport and the Validation Report.

### Limits you should know about

- Zolpidem and the scopolamine patch have no flight arm, because no published in-flight measurement exists for either.
- Scopolamine's half-life runs shorter than the source paper's own measured value, and the patch Cavg runs about 2.4 times above the FDA label figure. Both are listed above with their numbers.
- Acetaminophen's Polyakov 2021 comparison cannot be matched by the three-parameter model, and the best achievable point is kept as it is.
- Weight and age distributions are shared across drugs by a disclosed substitution, and zolpidem weight is a flat 70 kg.

## Reproducing the validation on the sample

`validation/benchmark_script.py` is the script used for the published benchmark, reproduced here **unmodified** from the dataset's validation package. It compares the medians of the ground arm and the flight/ground ratios against published literature ranges, one benchmark per row.

**Published result, full dataset:**

- Structural checks passed: 41/41
- Literature benchmarks: 8 of 10 passed, 2 disclosed failures, 0 unexpected
- Scopolamine half-life (disclosed failure): 1.89 h vs 2.80-6.20 h published
- Scopolamine patch Cavg (disclosed failure): 209.78 pg/mL vs 52.20-139.20 pg/mL, FDA label about 87

**Note on the published result.** Two of the ten literature benchmarks fail, and both were known structural limits before the report was written. Scopolamine's terminal half-life comes out at 1.89 h against 4.5 +/- 1.7 h in the source paper, because that paper's own clearance and volume imply a much shorter half-life once the drug is reduced to one compartment. The patch route's average concentration is about 2.4 times the FDA label figure, because the model has no dermal depot and sends the full nominal dose straight into blood. The delivery rate was left at the label's value and was not lowered to force a match. In practice, treat t_half_true for scopolamine as too short and patch-route concentrations as too high. The 41 structural checks test internal consistency (keys, ranges, mass balance, leakage), and the benchmarks compare medians with published ranges that were not used to build the model.

**What `notebook/validate_sample.ipynb` does.** The sample files carry a `_sample` suffix, so the notebook copies the three tables the script reads under the names it expects, inside a temporary directory, and runs an unmodified copy of the script there. The notebook is executed, with its outputs saved in the file, and writes nothing into the repository.

**What it produced on the sample.** Nine of the ten benchmarks can be computed from the sample: 8 PASS, 1 FAIL_DISCLOSED (scopolamine half-life, the same disclosed failure as in the full dataset), 0 FAIL_UNEXPECTED. The tenth, the scopolamine patch Cavg, needs the simulation kernel from the generator and is skipped with a warning.

Figures computed on the sample are **not** a benchmark of the dataset and should not be quoted; the numbers to cite are the published full-dataset ones above. `validation/requirements.txt` pins the package versions the notebook was executed with.

## Licensing

This free sample (data, script and notebook) is released under **CC BY-NC 4.0**: non-commercial use is permitted with attribution. The full dataset is sold under a commercial research license; see the [dataset page](https://sentineldata.com.ua/dataset/orbit-pk-three-drug-spaceflight-pk-calibrated) and the [licence terms](https://sentineldata.com.ua/dataset-license).

## Citation

> Code Sentinel Data, Chekerskyi, M. (2026). *ORBIT-PK: THREE-DRUG SPACEFLIGHT PK CALIBRATED*. Zenodo. https://doi.org/10.5281/zenodo.24018154

## Links

- Full dataset and passport: https://sentineldata.com.ua/dataset/orbit-pk-three-drug-spaceflight-pk-calibrated
- Zenodo record (DOI): https://doi.org/10.5281/zenodo.24018154
- OSF: https://doi.org/10.17605/OSF.IO/HKNU8
- Harvard Dataverse: https://doi.org/10.7910/DVN/REUM3L