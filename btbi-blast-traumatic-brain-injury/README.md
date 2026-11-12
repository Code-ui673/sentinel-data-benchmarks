# bTBI — Blast Traumatic Brain Injury in Blast-Exposed Service Members — free sample

> **This repository folder contains the technical documentation, validation code and a free evaluation sample (500 of 20,000 subjects) — not the full dataset.**
> **Full dataset:** **[sentineldata.com.ua/dataset/btbi-blast-traumatic-brain-injury](https://sentineldata.com.ua/dataset/btbi-blast-traumatic-brain-injury)**

20,000 synthetic blast-exposed service members: acute injury severity (GCS, LOC/AOC/PTA, CT imaging — Marshall/Rotterdam), serial MACE-2/ImPACT/VOMS cognitive testing, and 6-12 month PTSD, sleep, headache and functional outcomes (540,000 longitudinal rows), mapped to OMOP CDM v5.4. 105/133 parameters VERIFIED against 75 sources; 112/112 validation checks passed; baseline recovery model AUC 0.72 sits inside the published real-data range. Free sample included.

**DOI (Zenodo):** [10.5281/zenodo.23659677](https://doi.org/10.5281/zenodo.23659677)  
**Also archived:** [OSF](https://doi.org/10.17605/OSF.IO/HJCSE)

**Status: MODEL-GENERATED / SYNTHETIC.** This is fully synthetic data from a simulation, not records of real service members or patients. It supports benchmarking, algorithm development and teaching; it is not clinical evidence.

## Sample contents

| File | Rows × Cols | Content |
|---|---:|---|
| `sample/btbi_sample_500.parquet` | 500 × 78 | Wide table, one row per subject, 78 columns, identical schema to the full dataset |
| `sample/data_dictionary.csv` | 78 × 7 | Full 78-column data dictionary, English and Russian |
| `sample/manifest_checksums.csv` | 4 × 3 | SHA-256 checksum per shipped file |
| `sample/PARQUET_HOWTO.txt` | — | How to open the Parquet files (pandas / R arrow / DuckDB) |
| `sample/bTBI_Sample_Passport_EN.pdf` | — | Sample data passport |

The free sample (`btbi_sample_500.parquet`, 500 × 78) is a **true random subset of the full 20,000-row dataset** — not a regeneration and not the first N subjects — drawn with a fixed selection seed and sorted by row index for reproducibility; it is byte-identical to the corresponding rows of the full dataset. Because the rare severity strata (Severe ∼0.5%, Penetrating ∼0.4% of all 20,000 subjects) are thin, a 500-row random draw can under-represent or, for Severe/Penetrating, nearly miss them by chance — this is disclosed, not hidden: the sample actually drawn contains 405 Mild / 84 Moderate / 7 Severe / 4 Penetrating. The sample intentionally excludes the full parameter audit, the literature registry, the automated validation report, the OMOP CDM export, the 540,000-row longitudinal table, and the generator script — all of these ship with the full dataset.

Sample composition (N=500, hand-verified against the shipped file): 421 male / 79 female, 401 enlisted / 99 officer, age 18–60 (mean 28.7); blast mechanism 76.0% IED, 8.0% Mortar, 7.4% RPG, 4.2% Grenade, 2.4% Landmine, 1.8% Rocket, 0.2% Aerial bomb; 24.4% ct_abnormal; 37.6% pre-injury psychiatric history; 70.6% label_prolonged_recovery_30d; 50.2% label_chronic_pcs; 12.2% label_rtd_failure; 32.8% ptsd_screen_positive_6mo; return-to-duty at 12 months: 87.8% Returned, 10.2% Medical discharge, 2.0% Not returned.

## About the dataset

The text below is the dataset's description from the product page, converted to Markdown.

**Fully synthetic. Contains no real persons, no real patient data.** Every generative parameter is traceable to a published source: 105 of 133 parameters VERIFIED (78.9%), 28 anchored to a verified statistic with a modelled within-category shape (21.1%, explicitly flagged), 0 unsourced. A free 500-subject sample is available for evaluation before licensing the full dataset.

### Overview

**bTBI — Blast Traumatic Brain Injury in Blast-Exposed Service Members** is a fully synthetic cohort of **20,000 blast-exposed service members**, covering the full acute-to-chronic arc of a blast traumatic brain injury: injury mechanism and context (blast device, standoff distance, helmet), acute severity (Glasgow Coma Scale, loss of consciousness, alteration of consciousness, post-traumatic amnesia), head CT imaging (Marshall Classification, Rotterdam CT score, midline shift, hemorrhage subtype), serial cognitive testing (MACE-2 at 0h/24h/72h/7d, ImPACT at baseline/30d/90d, VOMS), and 6- and 12-month outcomes (PTSD via PCL-5, sleep via PSQI, headache via HIT-6, depression via PHQ-9, Glasgow Outcome Scale Extended, return-to-duty status). A 540,000-row longitudinal table carries the full repeated-measures history (∼27 timed observations per subject on average). The whole cohort ships pre-mapped to **OMOP CDM v5.4**.

Injury-context distributions (blast mechanism, standoff distance, helmet mix) follow DoD/DVBIC worldwide TBI numbers and USMC/Army helmet-fielding documentation; acute severity bands follow Hoge et al. (NEJM 2008) and published DoD GCS/LOC/PTA bands; CT staging follows the Marshall (1991) and Rotterdam (Maas 2005) classification literature; cognitive-recovery trajectories follow McCrea et al. (2014) MACE day-of-injury norms and Kontos et al. (2015) ImPACT post-injury means; 12-month functional outcome follows Mikolic et al. (CENTER-TBI, 2023) GOSE prognostic models. Seed `20260926` (numpy `default_rng`) makes the build deterministically reproducible.

### Dataset at a Glance

| Property           | Value                                                                                                                                                                       |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Subjects           | 20,000 blast-exposed service members (wide table, one row per subject)                                                                                                      |
| Longitudinal rows  | 540,000 (∼27 timed observations per subject on average)                                                                                                                     |
| Timepoints         | Acute: 0h, 24h, 72h, 7 days (MACE-2) · 30d, 90d (ImPACT) · 6, 12 months (PTSD/sleep/headache/depression/GOSE/RTD)                                                           |
| Wide table         | 78 columns — demographics, injury context, acute clinical, CT imaging, diagnostic coding, serial cognitive, vestibular/ocular, 6–12 month outcomes, ground-truth labels     |
| Long table         | 5 columns — per-subject repeated-measure events across the full follow-up window                                                                                            |
| OMOP CDM v5.4      | 5 tables: person, observation_period, condition_occurrence, measurement, observation (concept_id fields ship unmapped; verified ICD-11/SNOMED/LOINC source codes preserved) |
| Format             | Apache Parquet (columnar) + machine-readable `schema.json`                                                                                                                  |
| Random seed        | 20260926 (numpy `default_rng`) — `generate_btbi.py` included with the full dataset for audit                                                                           |
| Pinned environment | Python 3.11 · numpy 2.1.0 · pandas 2.3.1 · pyarrow 21.0.0 · scipy 1.15.0                                                                                                    |
| Version            | 1.1 (adds `education_years`, `psychiatric_history_flag`; GOSE-12mo labels regenerated on published effect sizes), released 2026-09-28                                       |

### Files & Schema

| File                                            | Rows        | Content                                                                                                                                |
|-------------------------------------------------|-------------|----------------------------------------------------------------------------------------------------------------------------------------|
| `btbi_wide.parquet`                             | 20,000 × 78 | One row per subject: demographics, injury context, acute clinical, CT imaging, coding, serial cognitive, outcomes, ground-truth labels |
| `btbi_longitudinal.parquet`                     | 540,000 × 5 | Long format: one row per measurement event (serial MACE-2, ImPACT follow-ups, VOMS, HIT-6/PCL-5/PSQI/PHQ-9 waves)                      |
| `omop_person.parquet`                           | 20,000 rows | OMOP CDM v5.4 PERSON                                                                                                                   |
| `omop_observation_period.parquet`               | 20,000 rows | OMOP CDM v5.4 OBSERVATION_PERIOD                                                                                                       |
| `omop_condition_occurrence.parquet`             | 20,000 rows | OMOP CDM v5.4 CONDITION_OCCURRENCE (TBI diagnosis, ICD-11/SNOMED source codes preserved)                                               |
| `omop_measurement.parquet`                      | —           | OMOP CDM v5.4 MEASUREMENT (GCS, CT findings)                                                                                           |
| `omop_observation.parquet`                      | —           | OMOP CDM v5.4 OBSERVATION (serial cognitive and outcome scale totals, LOINC source codes preserved)                                    |
| `generate_btbi.py`                              | —           | Deterministic generator script (SEED 20260926, numpy `default_rng`)                                                                    |
| `parameter_audit.csv`                           | 133 rows    | Every generation parameter with VERIFIED / ESTIMATE_SOURCED status and anchor source                                                   |
| `literature_registry.csv`                       | 75 rows     | Every literature source referenced in the audit, each with a DOI/PMID/URL                                                              |
| `schema.json`                                   | —           | Machine-readable column schema (names, dtypes, allowed ranges)                                                                         |
| `validation_checks.csv`, `validation_report.md` | —           | Results of the 112 automated data-quality checks                                                                                       |
| `DATASET_DESCRIPTION.md`                        | —           | The full 78-column data dictionary (also reproduced as Appendix A of the Data Passport)                                                |

### Injury Context & Cohort Population

Age (18–60) follows a Gamma distribution per rank calibrated to DoD 2022/2023 demographic marginals; blast mechanism, standoff-distance banding and helmet mix follow DVBIC worldwide-numbers reporting and USMC/Army helmet-fielding documentation (ACH 55% / LWH 20% / ECH 20% / IHPS 5% target mix); injury severity vs. standoff distance is coupled through a monotone proportional-odds model anchored to Denny, Dickinson & Langdon (2021) blast-loading physics.

| Field                          | Categories                                               | Design anchor                                                                                                |
|--------------------------------|----------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| TBI severity                   | Mild, Moderate, Severe, Penetrating                      | Full cohort carries the exact surveillance marginals; Severe ∼0.5%, Penetrating ∼0.4% of all 20,000 subjects |
| Blast mechanism                | IED, Mortar, RPG, Rocket, Grenade, Landmine, Aerial bomb | DVBIC/DoD worldwide TBI reporting                                                                            |
| Standoff distance              | ≤5m, 5–12m, 12–25m, \>25m                                | Target split 10% / 30% / 35% / 25% — modelled on Denny 2021 blast-loading physics                            |
| Helmet type                    | ACH, ECH, IHPS, LWH                                      | Target mix ACH 55% / LWH 20% / ECH 20% / IHPS 5% — USMC/Army fielding documentation 2018                     |
| Pre-injury psychiatric history | boolean flag                                             | 37.3% prevalence — anchored to Madhok 2020                                                                   |

In the free 500-subject sample, the injury-context distributions track these design targets closely (standoff distance 9.6% / 34.2% / 37.4% / 18.8%; helmet 51.0% ACH / 22.0% ECH / 21.8% LWH / 5.2% IHPS; pre-injury psychiatric history 37.6%) — a useful cross-check of the generator against its own documented design, reported here rather than asserted.

### Acute Clinical Severity & CT Imaging

Admission GCS, LOC/AOC/PTA presence and duration follow published DoD severity bands (Hoge 2008) and the GOAT protocol (1979); head CT findings are staged with the Marshall Classification (Marshall et al. 1991, *J Neurosurg*) and the Rotterdam CT score (Maas et al. 2005, *Neurosurgery*) via a Gaussian copula fit to verified marginals, with midline shift \>5mm (the clinically significant threshold) scored by a gamma model within Marshall grade. All subjects receive a CT scan — a design choice, not a clinical selection effect.

| Field              | Values                                       | Design anchor                                                       |
|--------------------|----------------------------------------------|---------------------------------------------------------------------|
| Marshall CT grade  | I–VI (diffuse/focal injury classification)   | Marshall 1991; evacuation of 25% of mild ICH modelled (Bonney 2020) |
| Rotterdam CT score | 1–6 (prognostic composite)                   | Maas 2005 component marginals via Gaussian copula                   |
| Midline shift      | mm, and \>5mm boolean flag                   | P(\>5mm \| Marshall V/VI) = 0.7; magnitude ~Gamma by grade          |
| ICH subtype        | None, EDH, SDH, TSAH, Contusion-IPH          | Derived from Marshall/Rotterdam staging                             |
| Diagnostic coding  | ICD-11 NA07.x, SNOMED CT 127298000/127302008 | WHO ICD-11 (2022); SNOMED CT (EBI OLS, 2026)                        |

In the 500-subject sample: 24.4% ct_abnormal, Marshall grade I in 77.0% (385/500, expected given the sample is overwhelmingly Mild severity), 5.8% midline shift \>5mm, mean Rotterdam score 2.28.

### Serial Cognitive Testing & Vestibular/Ocular Assessment

MACE-2 (Military Acute Concussion Evaluation 2) is scored serially at the point of injury, 24h, 72h and 7 days, with day-of-injury norms anchored to McCrea et al. (2014, *Military Medicine*) and FITBIR data-element norms; ImPACT verbal memory, visual memory, processing speed and reaction time composites are scored at an estimated pre-injury baseline, 30 days and 90 days, anchored to Kontos et al. (2015, USASOC) post-injury means. VOMS (Vestibular/Ocular Motor Screening) near-point-of-convergence distance and VOR/symptom-provocation results follow Mucha et al. (2014) thresholds, applied at severity-specific rates (mild 61% / moderate 75% / severe 85%).

|                                                                                                                                                                                                                                                                                        |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Acute-tool limitation (documented, not hidden):** MACE-2 is insensitive beyond 12–72h in reality — the 7-day serial value in this dataset is a modelled recovery trajectory, not a measured instrument property. This is stated as a known limitation, not implied as clinical fact. |

### 6- and 12-Month Outcomes & Ground-Truth Labels

Chronic headache (HIT-6), PTSD screening (PCL-5), sleep quality (PSQI) and depression (PHQ-9) are scored at 6 and 12 months with published psychometric cutoffs (PCL-5 ≥33 probable PTSD per Bovin et al. 2016; PSQI \>5 poor sleep per Buysse et al. 1989). Functional recovery is scored with the Glasgow Outcome Scale Extended (GOSE 1–8) at 12 months, modelled with a binary logistic link anchored to Mikolic et al. (2023) and a day-0 MACE-2 severity term (McCrea 2014); subjects below the GOSE\<8 threshold draw their 1–7 value from the marginals in Nelson (2019) and McCrea (2021).

| Field                           | Type                                      | Definition                                                             |
|---------------------------------|-------------------------------------------|------------------------------------------------------------------------|
| label_prolonged_recovery_30d    | boolean                                   | Ground truth: recovery prolonged beyond 30 days                        |
| label_rtd_failure               | boolean                                   | Ground truth: failed to return to duty at 12 months                    |
| label_chronic_pcs               | boolean                                   | Ground truth: chronic post-concussive syndrome                         |
| gose_12mo / gose_favorable_12mo | score 1–8 / boolean (≥7)                  | Glasgow Outcome Scale Extended at 12 months and favorable-outcome flag |
| rtd_status_12mo                 | Returned, Not returned, Medical discharge | Return-to-duty status at 12 months                                     |

In the 500-subject sample: 70.6% label_prolonged_recovery_30d, 12.2% label_rtd_failure, 50.2% label_chronic_pcs, 32.8% ptsd_screen_positive_6mo, 95.4% gose_favorable_12mo (477/500). *Note the GOSE favorable-outcome rate in this 500-row sample is not comparable to the 12-month incomplete-recovery prevalence (GOSE\<8, 59.5%) reported for the full 20,000-subject model-training split in the Baseline Validation Report (Section 11) — the favorable (≥7) and incomplete-recovery (\<8) thresholds overlap at GOSE=7 by design, and the 500-row free sample is a true random subset, not a stratified one, so rare and borderline strata can be over- or under-represented purely by chance (see Section 13).*

### OMOP CDM v5.4 Mapping

The cohort re-ships into 5 OMOP CDM v5.4 tables (PERSON, OBSERVATION_PERIOD, CONDITION_OCCURRENCE, MEASUREMENT, OBSERVATION). Standard `concept_id` fields are set to 0 (unmapped) — a valid OMOP convention when vocabulary tables are not bundled — while verified ICD-11, SNOMED CT and LOINC source codes are preserved in the corresponding `*_source_value` columns for local vocabulary mapping (ICD-11 NA07.x per WHO 2022; SNOMED CT 127298000/127302008; LOINC 9269-2 Glasgow coma score total).

### Quality Assurance & Validation

The post-generation validation suite executes **112 automated checks**; all 112 pass, with zero NULL values anywhere in the delivered tables. Every check on a subgroup of 1,000+ subjects deviates from its published target by at most 1.9 percentage points; the single larger deviation (5.1pp, in the severe-TBI outcome subgroup, n∼110) lies within that subgroup's own 99.9% binomial sampling interval — disclosed rather than tuned away. Checks cover value ranges, cross-column coherence (severity vs. GCS bands, LOC/PTA durations within severity bands, CT-negative implies Marshall I and Rotterdam 2), and integer dtypes for count/score columns.

| Generator stage | Parameters | VERIFIED | ESTIMATE_SOURCED | % VERIFIED |
|-----------------|------------|----------|------------------|------------|
| S2              | 39         | 31       | 8                | 79.5%      |
| S2/S3           | 3          | 3        | 0                | 100.0%     |
| S3              | 30         | 21       | 9                | 70.0%      |
| S3/S7           | 2          | 2        | 0                | 100.0%     |
| S4              | 19         | 16       | 3                | 84.2%      |
| S5              | 19         | 18       | 1                | 94.7%      |
| S6              | 19         | 12       | 7                | 63.2%      |
| S7              | 2          | 2        | 0                | 100.0%     |

**Independent baseline benchmark (not tuned for this listing):** a plain logistic-regression baseline (32 acute-phase features available at presentation/discharge — demographics, GCS, LOC/AOC/PTA, CT findings, day-0 MACE-2, VOMS, blast-exposure history, education, pre-injury psychiatric history; 59 columns after one-hot encoding) predicting 12-month incomplete recovery (GOSE\<8, prevalence 0.595) on a stratified 80/20 split with 5-fold cross-validation:

| Split               | N         | Prevalence | AUC        | F1         | Brier      | Cal. slope |
|---------------------|-----------|------------|------------|------------|------------|------------|
| cv_fold_1           | 3,200     | 0.5950     | 0.7249     | 0.7155     | 0.2053     | 0.9068     |
| cv_fold_2           | 3,200     | 0.5950     | 0.7170     | 0.7078     | 0.2082     | 0.8503     |
| cv_fold_3           | 3,200     | 0.5950     | 0.7400     | 0.7403     | 0.2004     | 1.0249     |
| cv_fold_4           | 3,200     | 0.5947     | 0.7560     | 0.7431     | 0.1946     | 1.1099     |
| cv_fold_5           | 3,200     | 0.5947     | 0.7437     | 0.7323     | 0.1993     | 1.0130     |
| train_full          | 16,000    | 0.5949     | 0.7405     | 0.7308     | 0.2002     | 1.0035     |
| **test (held out)** | **4,000** | **0.5950** | **0.7185** | **0.7213** | **0.2073** | **0.8813** |

Held-out test: AUC 0.719, F1 0.721, Brier 0.207, calibration slope 0.88. For comparison, Mikolic et al. (CENTER-TBI, *J Neurotrauma* 2023, doi:10.1089/neu.2022.0320) report ordinal logistic models on 2,376 real mild-TBI patients predicting 6-month GOSE reaching concordance C=0.68 (Core model) and C=0.70 (Clinical model); external validation of published mTBI GOSE models reported C-index 0.58–0.79 (Mikolic et al. 2021, doi:10.1089/neu.2020.7074). The synthetic baseline (test AUC 0.719) sits inside this published real-data range, between the CENTER-TBI Clinical model and its extended models — with two honest caveats disclosed in the validation report: the outcome labels here are themselves generated from a logistic model built on published effect sizes, so a logistic baseline on overlapping features recovers the embedded signal close to optimally (on real data this level is reached only by richer extended models); and the synthetic feature set excludes early-symptom questionnaires that drive part of the real-world signal. The dataset carries realistic, learnable — but not trivially separable — outcome signal (AUC well below 0.80; CV spread 0.717–0.756).

### Provenance

All 133 generative parameters carry a parameter-level audit record (parameter, value, anchor source). **105 parameters (78.9%) are VERIFIED** against 75 published sources (DOI/PMID/URL, each independently resolvable); **28 parameters (21.1%) are anchored estimates** — tied to a verified published statistic with a modelled within-category shape — and are explicitly flagged below so a buyer can judge fit for their own use case. No parameter is an unsourced guess.

| Parameter                         | Anchor source                                                                                           |
|-----------------------------------|---------------------------------------------------------------------------------------------------------|
| distance_class_distribution       | Denny, Dickinson, Langdon 2021                                                                          |
| helmet_type_mix                   | USMC/Army program offices 2018                                                                          |
| loc_within_band_distribution      | Hoge 2008 + DoD bands 2008                                                                              |
| pta_within_band_distribution      | DoD bands + GOAT protocol 1979                                                                          |
| midline_shift_gt5mm_pct           | Maas et al. (Rotterdam component) 2005                                                                  |
| mace_serial_means_0h_24h_72h_7d   | McCrea 2014 + FITBIR norm + Kontos 2014/2015                                                            |
| impact_postinjury_means_30d_90d   | Kontos et al. (USASOC) 2015                                                                             |
| rtd_post_evacuation_modsevere_pct | Bahadur 2017; Dillahunt-Aspillaga 2017                                                                  |
| prolonged_recovery_30d_label      | McCrea 2014 + Nelson 2019                                                                               |
| cte_risk_index                    | Goldstein 2012; McKee 2014/2023; Brix 2017                                                              |
| age_distribution_form             | 18 + Gamma(k, theta) per rank — calibrated to DoD 2022/2023 marginals                                   |
| distance_class_split              | ≤5m 10% / 5-12m 30% / 12-25m 35% / \>25m 25% — model on Denny 2021 physics                              |
| helmet_mix                        | ACH 55% / LWH 20% / ECH 20% / IHPS 5% — model on fielding docs 2018                                     |
| severity_distance_coupling        | IPF proportional-odds, monotone — model; marginals DoD 2023/2024                                        |
| gcs_within_modsev                 | moderate: GCS 12/11/10/9 = 35/30/20/15%; severe: mode GCS 6–7 — model on GCS bands 1974                 |
| loc_aoc_pta_mild_models           | presence: LOC 32% / AOC 80% / PTA 85% (of mild) — Hoge 2008 ratio + DoD bands + GOAT 2008               |
| ct_modsevere_point                | 90 (moderate/severe); 100 (penetrating) — Maas 2005 lower bound as point                                |
| marshall_mild_ctplus              | II default; V if evacuated (evacuation 25% of mild ICH) — model on Marshall 1991 + Bonney 2020          |
| rotterdam_model                   | Gaussian copula on verified marginals + scoring rubric — Maas 2005                                      |
| mls_model                         | P(\>5mm \| Marshall V/VI) = 0.7; mm ~ Gamma by grade — model on Rotterdam component 2005                |
| voms_modsevere_application        | mild 61 / moderate 75 / severe 85 — Mucha 2014 anchor + gradient model                                  |
| chronic_instrument_forms          | PCL-5 mixture per LOC/AOC group; PSQI severity-conditional — Hoge 2008 + Walker 2017/2023 + Buysse 1989 |
| chronic_pcs_modsevere             | moderate 60 / severe 75 — gradient on Schwab 2017 + Machamer 2022                                       |
| education_years_mapping           | no-HS=11; HS=12; some college=13 — standard US schooling convention                                     |
| psychiatric_history_prevalence    | 37.3% — Madhok 2020                                                                                     |
| gose_model_form                   | binary logistic link on P(GOSE\<8 \| stratum) — Mikolic 2023 anchor                                     |
| gose_beta_mace_day0               | 0.45 x z(MACE day-0 total) — McCrea 2014 anchor                                                         |
| gose_conditional_shape            | subjects below the GOSE\<8 threshold draw GOSE 1-7 from v1.0 marginals — Nelson 2019 + McCrea 2021      |

Key references underpinning the audit include Hoge et al. (*NEJM* 2008), Marshall et al. (*J Neurosurg* 1991), Maas et al. (*Neurosurgery* 2005), McCrea et al. (*Military Medicine* 2014), Kontos et al. (*J Trauma Acute Care Surg* 2015), Mikolic et al. (*J Neurotrauma* 2021 & 2023, CENTER-TBI), Bovin et al. (*Psychol Assess* 2016), Buysse et al. (*Psychiatry Res* 1989), and the VA/DoD Clinical Practice Guideline for Management and Rehabilitation of Post-Acute Mild TBI (v3.0, 2021). Full registry: 75 sources, each independently resolvable via DOI/PMID/URL.

### Known Limitations

- 28 of 133 parameters are anchored estimates: tied to a verified published statistic, with modelled within-category shape (listed in Section 10).
- OMOP `concept_id` fields ship unmapped (0); verified ICD-11/SNOMED/LOINC source codes are preserved in `*_source_value` columns for local vocabulary mapping.
- All subjects receive a CT scan (design choice, not a clinical selection effect).
- Injury dates are uniformly distributed across 2022–2024 (design choice).
- Acute cognitive tools (MACE-2) are insensitive beyond 12–72h in reality; serial values here are a modelled recovery trajectory, not a measured instrument property.
- PCL-5 ≥33 is a PTSD screening threshold, not a diagnosis.
- Pre-injury psychiatric history influences the 12-month GOSE label but is not cross-coupled to the 6/12-month PCL-5/PHQ-9 scores — no published military effect size exists for that coupling; flagged in the audit.

|                                                                                                                                                                                                                                                                                                                                               |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **IMPORTANT — CTE risk index:** the `cte_risk_index` and `cte_exposure_score` columns are hypothesis-generation features only. A 2017 NIH/NINDS expert panel (Brix et al., *J Neurotrauma*, doi:10.1089/neu.2017.5222) found no quantitative dose-response evidence linking blast exposure to CTE. Do not use them as a validated risk score. |

### Use Cases

**Suitable for:** acute-severity and 12-month recovery-prediction model development and benchmarking in military/blast TBI research; return-to-duty and chronic post-concussive syndrome risk stratification; CT-staging and imaging-pipeline testing against Marshall/Rotterdam ground truth; serial cognitive-trajectory modeling (MACE-2, ImPACT, VOMS); OMOP CDM v5.4 ETL, phenotype and cohort-definition pipeline testing; epidemiological simulation; teaching military neurotrauma epidemiology, concussion assessment or clinical ML on reproducible, fully documented synthetic data.

**NOT suitable for:** estimating real-world clinical effectiveness, individual clinical decisions, CTE risk assessment or diagnosis, or training models intended for deployment on real patients without external validation on real data. The dataset is fully synthetic and contains no real patient data.

## Reproducing the validation on the sample

`validation/benchmark_script.py` is the script used for the published benchmark, reproduced here **unmodified** from the dataset's validation package. It predicts incomplete recovery at 12 months (GOSE < 8) from acute-phase features only, with 5-fold cross-validation on the training part and a held-out test split.

**Published result, full dataset:**

- Checks passed: 112/112
- Parameters verified: 105/133 (75 sources)
- Held-out test AUC: 0.719 (real-world range 0.58-0.79)

**Note on the published result.** Labels come from the same logistic model the benchmark is scored against, so this baseline recovers the signal close to optimally — real data needs richer models to reach the same level. The feature set also leaves out early-symptom questionnaires that carry part of the real-world signal.

**What `notebook/validate_sample.ipynb` does.** The notebook copies the unmodified script and the sample Parquet file to a temporary directory and runs it there; the script takes the data path as its first argument. The notebook is executed, with its outputs saved in the file, and writes nothing into the repository.

**What it produced on the sample.** On the 500-row sample the held-out test split has 100 subjects: AUC 0.691, F1 0.689, calibration slope 0.56. The published full-dataset values are AUC 0.719, F1 0.721, calibration slope 0.88. The gap is what a 100-subject test set produces.

Figures computed on the sample are **not** a benchmark of the dataset and should not be quoted; the numbers to cite are the published full-dataset ones above. `validation/requirements.txt` pins the package versions the notebook was executed with.

## Licensing

This free sample (data, script and notebook) is released under **CC BY-NC 4.0**: non-commercial use is permitted with attribution. The full dataset is sold under a commercial research license; see the [dataset page](https://sentineldata.com.ua/dataset/btbi-blast-traumatic-brain-injury) and the [licence terms](https://sentineldata.com.ua/dataset-license).

## Citation

> Code Sentinel Data, Chekerskyi, M. (2026). *bTBI — Blast Traumatic Brain Injury in Blast-Exposed Service Members*. Zenodo. https://doi.org/10.5281/zenodo.23659677

## Links

- Full dataset and passport: https://sentineldata.com.ua/dataset/btbi-blast-traumatic-brain-injury
- Zenodo record (DOI): https://doi.org/10.5281/zenodo.23659677
- OSF: https://doi.org/10.17605/OSF.IO/HJCSE