# Patient Liability & Financial Assistance Ledger — free sample

> **This repository folder contains the technical documentation, validation code and a free evaluation sample (250 of 5,000 hospital accounts) — not the full dataset.**
> **Full dataset:** **[sentineldata.com.ua/dataset/patient-liability-financial-assistance-ledger](https://sentineldata.com.ua/dataset/patient-liability-financial-assistance-ledger)**

A synthetic ledger of 5,000 hospital accounts walked through the financial-assistance cascade: six linked tables, four planted processing errors in 18.6% of accounts, and a per-account answer key with the correct and the actual patient liability.

**DOI (Zenodo):** [10.5281/zenodo.24159846](https://doi.org/10.5281/zenodo.24159846)  
**Also archived:** [OSF](https://doi.org/10.17605/OSF.IO/EAM5C) · [Figshare](https://doi.org/10.6084/m9.figshare.34993918) · [Harvard Dataverse](https://doi.org/10.7910/DVN/HTEV1B)

**Status: MODEL-GENERATED / SYNTHETIC.** This is fully synthetic data from a simulation. No real patients, hospitals, providers or claims are in it. It supports detection-logic development, policy simulation and teaching; it is not clinical, billing or compliance evidence.

## Sample contents

| File | Rows × Cols | Content |
|---|---:|---|
| `sample/assistance_application.parquet` / `.csv` | 157 × 10 | One application as it was processed: the policy version applied, household income and size, the recorded poverty percentage, the eligibility decision, the discount and the assistance amount. |
| `sample/assistance_policy_version.parquet` / `.csv` | 3 × 12 | One version of the assistance policy: effective dates, the three discount bands and their poverty-level thresholds, eligible services, lookback. |
| `sample/liability_finding.parquet` / `.csv` | 250 × 6 | The answer key: one row per account with the correct final liability, the actual final liability, the error type (empty when the waterfall is correct) and the scenario id. |
| `sample/patient_account.parquet` / `.csv` | 250 × 8 | One hospital account: service type and date, gross charge, insurance adjustment, contractual write-off, balance after insurance. |
| `sample/payment.parquet` / `.csv` | 1,001 × 5 | One payment event with date, amount and source: patient, charity, payment plan or collection agency. |
| `sample/waterfall_step.parquet` / `.csv` | 2,158 × 8 | One cascade step: booking order, step type, amount before, signed adjustment, amount after, effective date. |
| `sample/manifest.json` | — | Manifest: tables, row counts and checksums |
| `sample/parquet_howto.txt` | — | How to open the Parquet files (pandas / R arrow / DuckDB) |
| `sample/passport_sample_EN.pdf` | — | Sample data passport |

The sample is a true subset of the baseline cohort: 250 accounts with all of their linked rows (157 applications, 1,001 payments, 2,158 cascade steps, 250 answer-key rows and the three policy versions). Nothing was regenerated. Accounts were allocated across error types by the largest-remainder method, so every type appears at its cohort proportion, including the rarest: 203 correct accounts, 17 FPL miscalculations, 13 wrong policy versions, 10 collections before screening, 6 excluded services and 1 discount not applied. Prevalence in the sample is 18.8% against 18.6% in the full cohort. Every table has the same columns as the full product and a CSV copy next to the Parquet file, so anything that runs on the sample runs unchanged on the full dataset.

The sample is meant for format checks, query and notebook prototyping, and teaching. It is too small for statistics: prevalence, medians and distributions estimated on 250 accounts are not the cohort's numbers, the rarest error type has a single account, and the published AUC comes from the full 5,000 accounts only.

## About the dataset

The text below is the dataset's description from the product page, converted to Markdown.

A hospital bill does not arrive as one number. Before the patient sees a figure, the account has already been through a chain of corrections: the chargemaster price, the insurer's adjustment, a contractual write-off, and then the step most people never hear about, the screening for financial assistance. A household at 180% of the federal poverty level should owe nothing. A household at 240% should get a partial discount. Somebody in the billing office has to check which version of the hospital's policy was in force on the day the application came in, work out the household's poverty percentage from income and family size, and decide whether the service is covered at all. Then, and only then, may the account be sent to a collection agency.

Patient Liability & Financial Assistance Ledger is a synthetic dataset that follows 5,000 hospital accounts through exactly that chain. It covers 3,225 patients and service dates from 2025-01-01 to 2026-06-30. Every account has a row in the answer key that states what the patient should have owed if the cascade had been processed correctly, and what the patient actually owed after the processing that took place. In 931 accounts (18.6%) the two numbers differ, because one of four processing errors was planted in the account. The other 4,069 accounts close through a correct waterfall and serve as the negative control.

The data is built for people who have to find those errors: revenue-integrity analysts, audit-automation teams, anyone training a model on billing data, and anyone who teaches how a hospital bill actually works. You get the bill the patient received and the bill a correct cascade would have produced, side by side, for every single account.

**Status: model-generated.** The dataset is fully synthetic. It contains no real patient, provider or claim. The planted errors model documented kinds of processing failure, and they do not describe any specific hospital. Federal poverty guidelines, the IRS Section 501(r) rules, published hospital assistance tiers and collection statistics come from primary sources captured on 2026-11-10. Please do not use the data as evidence of how any real hospital behaves, and do not use it for real billing or compliance decisions.

### At a glance

| Item                          | Value                                                                                                         |
|-------------------------------|---------------------------------------------------------------------------------------------------------------|
| Unit of observation           | One hospital account                                                                                          |
| Scope                         | 5,000 accounts, 3,225 patients                                                                                |
| Service window                | 2025-01-01 to 2026-06-30 (18 months)                                                                          |
| Tables                        | 6 linked tables, Apache Parquet with a CSV mirror of each, plus a manifest with SHA-256 per table             |
| Volume                        | 80,184 rows across the six tables, roughly 2 MB                                                               |
| Planted errors                | 931 accounts (18.6%), exactly one error per affected account, four error types                                |
| Answer key                    | `liability_finding`: one row per account with correct liability, actual liability, error type and scenario id |
| Policy versions               | 3 versions of the assistance policy, with different discount bands, in force at different times               |
| Detection benchmark           | AUC 0.9927 ± 0.0042 (XGBoost, 5-fold patient-level cross-validation); registered bar 0.87                     |
| Benchmark without audit flags | AUC 0.8646 on the raw observable fields alone                                                                 |
| Preregistered checks          | 11 of 12 passed; one failed (P8) and its investigation is published                                           |
| Dollar conservation           | 0 violations; every cascade closes to the cent                                                                |
| Determinism                   | Two generation runs are byte-identical; seed 20261110                                                         |
| Free sample                   | 250 accounts with all linked rows, stratified by error type                                                   |

### The cascade the data walks through

A correct account moves through a fixed order of steps, and the dataset records every step of every account in `waterfall_step`: gross charge, insurance adjustment, contractual write-off, financial-assistance screening, charity care or a discount, patient payment, payment plan, collection placement and bad debt. The engine that produced the data is a small state machine (billed, insurance adjudicated, screened, assistance adjudicated, paying, placed, closed) with cent rounding at every step. If an account does not close to zero within one cent, the generator raises an exception and stops. That is why the validation report can say that 100% of cascades reconcile.

The balance after insurance is the eligibility base. Households at or below 200% of the federal poverty level receive full charity care in the correct waterfall (613 of 613 eligible accounts in the baseline cohort do). Above that line the discount shrinks band by band, according to whichever policy version was in force on the application date.

### The six tables

| Table                       | Rows (full) | What one row is                                                                                                                                                                                |
|-----------------------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `patient_account`           | 5,000       | One hospital account: service type and date, gross charge, insurance adjustment, contractual write-off, balance after insurance.                                                               |
| `assistance_policy_version` | 3           | One version of the assistance policy: effective dates, the three discount bands and their poverty-level thresholds, eligible services, lookback.                                               |
| `assistance_application`    | 3,227       | One application as it was processed: the policy version applied, household income and size, the recorded poverty percentage, the eligibility decision, the discount and the assistance amount. |
| `payment`                   | 21,996      | One payment event with date, amount and source: patient, charity, payment plan or collection agency.                                                                                           |
| `waterfall_step`            | 44,958      | One cascade step: booking order, step type, amount before, signed adjustment, amount after, effective date.                                                                                    |
| `liability_finding`         | 5,000       | The answer key: one row per account with the correct final liability, the actual final liability, the error type (empty when the waterfall is correct) and the scenario id.                    |

Everything joins on `account_id`; `patient_id` groups accounts to a person and drives the patient-level split in the benchmark. The label lives only in `liability_finding`. Keep it out of your features.

#### Columns

| Table                       | Columns                                                                                                                                                                                          |
|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `patient_account`           | account_id, patient_id, service_date, gross_balance, insurance_adjustment, contractual_write_off, balance_after_insurance, service_type                                                          |
| `assistance_policy_version` | policy_id, version, effective_from, effective_to, fpl_threshold_100, fpl_threshold_200, fpl_threshold_300, discount_at_100, discount_at_200, discount_at_300, eligible_services, lookback_months |
| `assistance_application`    | application_id, account_id, policy_version, application_date, household_income, household_size, fpl_percentage, eligible, discount_applied, assistance_amount                                    |
| `payment`                   | payment_id, account_id, payment_date, amount, source                                                                                                                                             |
| `waterfall_step`            | step_id, account_id, step_order, step_type, amount_before, adjustment, amount_after, step_date                                                                                                   |
| `liability_finding`         | finding_id, account_id, correct_final_liability, actual_final_liability, error_type, scenario_id                                                                                                 |

### The four planted errors

Each error type is injected by one mechanism and leaves one signature in the observable tables, the same signature a hospital revenue-integrity audit would look for. Five scenarios exist in total, because the correct waterfall is a scenario of its own.

| Error type                    | Accounts | What the processor did wrong, and where it shows                                                                                                                                                                                     |
|-------------------------------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `wrong_policy_version`        | 260      | The application was screened under a policy version that was not in force on the application date. Visible by comparing `assistance_application.policy_version` with the effective range in `assistance_policy_version`.             |
| `fpl_miscalculation`          | 329      | The poverty percentage was computed with a household size that is off by one, while the recorded size stays correct. The recorded percentage contradicts the recorded income and size under the published guideline table.           |
| `eligible_service_excluded`   | 118      | A service the policy covers was treated as excluded, so no assistance was granted despite eligibility. The service type sits in `eligible_services`, the poverty percentage is inside the thresholds, and `eligible` is still false. |
| `discount_not_applied`        | 25       | A legacy policy that denies all assistance above 250% of the poverty level was applied where the correct version grants a discount. This is the observable sub-class of the wrong-policy mechanism, and it is rare on purpose.       |
| `collection_before_screening` | 199      | The account was placed with a collection agency before the screening decision, inside the 120-day window that IRS Section 501(r) reserves. Visible as a collection step dated earlier than the screening step in `waterfall_step`.   |
| (no error, negative control)  | 4,069    | Correct waterfall: lawful final liability, ordered steps, closed chain. Correct and actual liability coincide.                                                                                                                       |

The injection rates are declared parameters: 6%, 6%, 5% and 4% of accounts across the four mechanisms, against a 79% correct-waterfall control. They are generator decisions, not measurements of any real hospital. The registered acceptance window for overall prevalence was 18 to 24%, with about 21% expected. The delivered cohort lands at 18.6%, inside the window and near its lower edge. For orientation, a published study of financial-assistance screening in emergency-department care reports 71.7% accuracy, which implies something like 28% errors in a real process. The dataset is therefore cleaner than the process it models, and the passport says so before you buy.

### Policy versions

Three versions of the assistance policy are in force across the window, each with its own effective dates, three discount bands at poverty-level thresholds, a list of eligible services and a lookback period. The first version caps assistance at 250% of the poverty level, which is what makes the rare discount-not-applied case possible. Later versions widen the bands to 300%. The published tier structures behind the three versions come from real hospital assistance policies (for example 100/80/60/40/20% write-off bands and a 240-day application window), and the wrong-policy error works as a natural experiment: the same household gets two different bills depending on which version the processor picked.

### Where the numbers come from

All 68 external parameters were captured verbatim from primary sources on 2026-11-10 and kept in a capture archive. Every parameter carries a tier: VERIFIED (captured word for word from the source), DERIVED (arithmetic on verified values), ESTIMATE_SOURCED (anchored in a sourced range) or DESIGN (a generator decision, documented in the assumptions log). The parameter groups are the HHS federal poverty guidelines for 2025 and 2026, the IRS Section 501(r) and collection rules (including the 120-day waiting period), the discount tiers and application windows published by real hospitals, KFF charity-care statistics, CFPB figures on medical collections (about \$49.2 billion in collections and 15 million people with medical collection accounts as of June 2023), payment-plan terms and default behaviour. The passport lists 26 references with locations and tiers.

Payment behaviour follows those sources. Thirty percent of balances draw a direct patient payment of 20 to 100% of the remainder. About 55% of balances over \$200 enrol in a zero-interest payment plan of 6 to 24 months with a \$25 minimum, and 15% of those plans default. Unpaid residuals are placed with an agency after the 120-day window, and agencies recover 16% of placed dollars half of the time. The cohort median household sits at 260.2% of the poverty level, inside the registered 200 to 350% design window.

### Validation

The validation suite was run against the delivered tables, not against generator internals. It has three layers: structure (schemas against the specification, referential integrity, answer-key coverage), conservation (every cascade closes within one cent) and eight predictions that were fixed and hashed before the first generation run. The registration hash is printed in the footer of every page of the passport and the validation report.

| ID  | Check                                                                             | Result                       | Verdict  |
|-----|-----------------------------------------------------------------------------------|------------------------------|----------|
| S0  | Specification columns present in all six tables                                   | all present                  | PASS     |
| S1  | Orphan foreign keys                                                               | 0                            | PASS     |
| S2  | Answer key covers every account exactly once                                      | 5,000 of 5,000               | PASS     |
| P1  | Error prevalence between 18% and 24%                                              | 18.6%                        | PASS     |
| P2  | Benchmark AUC at least 0.87 (patient-held 5-fold CV)                              | 0.9927                       | PASS     |
| P3  | Balance invariant violations above \$0.01                                         | 0                            | PASS     |
| P4  | Collection before screening in 100% of that scenario and 0% of the control        | 199 of 199; 0 in the control | PASS     |
| P5  | Median household income between 200% and 350% of the poverty level                | 260.2%                       | PASS     |
| P6  | Cascades reconciling to zero within \$0.01                                        | 100.00%                      | PASS     |
| P7  | Eligible households at or below 200% receive full charity care (correct scenario) | 100.00% of 613               | PASS     |
| L1  | No answer-key column among the features                                           | clean                        | PASS     |
| P8  | Benchmark AUC does not exceed 0.99 (leakage guard)                                | 0.9927                       | **FAIL** |

The engine also ships with 46 unit tests, one per error type plus the negative control, the invariants and a 300-cascade randomised conservation sweep. All of them pass on the delivered code.

#### The check that failed, and why it is printed

P8 was registered as a leakage guard: if the benchmark AUC went above 0.99, something would need explaining. It came in at 0.9927, so the prediction failed, and the registration itself committed to an investigation. That investigation found no leakage. No answer-key column appears among the features, which was checked programmatically against the answer-key schema. The three strongest features are audit rules: whether the recorded policy version was in force on the application date, whether the recorded poverty percentage matches income and household size, and whether the collection date precedes the screening decision. Each is a deterministic function of the observable tables, and each is exactly what a revenue-integrity audit runs. Without these three derived flags, the same model reaches 0.8646. The high ceiling is the design of the planted errors. The failed check is reported as registered, and no threshold was changed afterwards.

If you want a harder task, drop the three audit flags and work from the raw fields. If you want to know how an audit gets to 0.99, keep them.

#### Detection benchmark

The benchmark is account-level binary classification: any processing error against a correct waterfall. Features come only from the four observable tables, and the answer key supplies the label and nothing else. The model is XGBoost (300 rounds, depth 5, learning rate 0.1) under 5-fold cross-validation grouped by patient, so no patient appears on both sides of a fold.

| Fold          | AUC                 | Train accounts | Test accounts | Test prevalence |
|---------------|---------------------|----------------|---------------|-----------------|
| 1             | 0.9862              | 4,000          | 1,000         | 16.9%           |
| 2             | 0.9923              | 4,000          | 1,000         | 18.8%           |
| 3             | 0.9925              | 4,000          | 1,000         | 19.6%           |
| 4             | 0.9930              | 4,000          | 1,000         | 18.2%           |
| 5             | 0.9994              | 4,000          | 1,000         | 19.6%           |
| **Mean ± SD** | **0.9927 ± 0.0042** | —              | —             | —               |

Prevalence in the test folds ranges from 16.9% to 19.6%, close to the cohort rate, so the AUC is not inflated by fold imbalance. The naive feature set without the derived audit flags scores 0.8646. For context, published models on adjacent financial-burden tasks report AUROC 0.84 for financial toxicity in cancer cohorts, 0.85 for breast cancer, and 0.883 for high-cost patient identification. Those tasks are real and noisy, while this one is synthetic with planted errors, so the numbers are not directly comparable. The ordering is still informative: the naive D06 score lands in the same range as published human-level tasks.

#### Defects found and fixed during validation

Validation surfaced four defects. Each was fixed in the generator or the engine, the cohort was regenerated and the full check suite was rerun from scratch.

| Defect                                                                                                                              | Fix                                                                                                          |
|-------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| Collection placement was missing from `waterfall_step` when the agency collected nothing, which hid 109 of 199 ordering violations. | Placement is always booked as a step; the ordering check now sees 199 of 199.                                |
| The Parquet round-trip returned dates as plain objects and broke date arithmetic in the validator.                                  | Dates are normalised to datetime64 on load, with the dtype asserted before feature building.                 |
| The numpy random state was never seeded, so two generation runs gave different error counts.                                        | The global state is seeded with the cohort seed; determinism is verified by comparing manifests of two runs. |
| Mixed integer and string values in the audit table broke the Parquet writer.                                                        | Value columns are cast to strings before serialisation.                                                      |

### What you can build with it

- **Error-detection models.** The label is whether the error type is filled; the features come from the four observable tables; split by patient. The published benchmark is exactly this task.
- **Audit-rule mining.** Recover the rules themselves: which joins and comparisons flag each error type. The three audit flags (policy-version validity, poverty-percentage recomputation, date ordering) are documented and reproducible.
- **Policy-impact simulation.** Re-price accounts under a different policy version. Three versions with different bands are in force across the window, and the wrong-policy accounts give you the same households under two bills.
- **Payment-behaviour models.** 21,996 payment events across four sources, with plan terms, defaults and collection recoveries, support take-up and default modelling.
- **Teaching and interviews.** The cascade is small enough to walk through by hand, and the answer key makes every exercise gradeable, from SQL joins to a full detection model.

### Who uses this data

- Revenue-cycle and revenue-integrity teams who want to build or test audit automation without touching real patient accounts.
- Data scientists and ML engineers training models on billing data, who need a labelled error set to score against.
- Health-policy researchers studying how assistance policy versions, poverty thresholds and collection timing interact.
- Product teams building financial-assistance screening or patient-billing software, who need a realistic fixture with known-correct answers.
- Educators and interviewers who want a billing dataset where every exercise can be graded.

## What is in the full delivery

The full delivery contains the six tables as Parquet with the manifest, the constants audit with tiers and sources, a 250-account stratified sample with the same schema, a column-level data dictionary, the validation report and benchmark results, the generator with its code, config and requirements, a guarded demo notebook, a user guide, the dataset passport and the generator passport.

### Limits you should know about

- The errors are rule-shaped. Each type is injected by one mechanism with a deterministic signature. Real processing errors are messier, and a model trained here will need retraining on institutional data.
- The benchmark ceiling is high by design (AUC 0.9927), and the leakage guard P8 failed as registered. The cause and the investigation are in the validation report.
- The 18.6% error prevalence is a design parameter, not a finding. Real-world error rates are likely higher (the sourced screening-accuracy figure implies about 28%).
- `discount_not_applied` is rare: 25 accounts (0.5%). If your task needs many of these, this dataset will not supply them.
- One payer mix and one hospital. Insurance adjustment ratios and the service mix are drawn from published averages, not from any provider's chargemaster.
- Income is anchored to multiples of the poverty guideline, and the cohort median sits at 260% by construction. It is a billing population, not a census sample.
- Household size drives the poverty percentage and nothing else does. There is no age, geography or state-level Medicaid variation, and the guideline figures are the 48-state federal ones.
- `lookback_months` is recorded but does not drive any decision.
- A small tail of applications lands in 2027, where HHS guidelines are not yet published. The most recent table is applied and the share is reported in the assumptions log.
- Collection recoveries are simplified to a single liquidation-rate parameter.
- There are no diagnoses, procedures or outcomes. The data covers the financial chain only, and the cascade encodes US rules end to end.

## Reproducing the validation on the sample

`validation/benchmark_script.py` is the script used for the published benchmark, reproduced here **unmodified** from the dataset's validation package. It detects planted processing errors at account level with XGBoost, 5-fold patient-level GroupKFold, and also reports the AUC without the three derived audit flags.

**Published result, full dataset:**

- Preregistered checks passed: 11/12 (P8 failure published)
- Unit tests passed: 46/46
- Detection AUC (5-fold, patient-level CV): 0.9927 +/- 0.0042, registered bar 0.87
- Detection AUC without audit flags: 0.8646

**Note on the published result.** The one failed check, P8, is a leakage guard registered at AUC 0.99; the measured value is 0.9927. The registered investigation found no leakage: no answer-key column is among the features, and the ceiling comes from the deterministic audit signatures of the planted errors (policy version in force on the application date, poverty percentage recomputed from income and size, collection date before screening date). Without those three derived flags the same model reaches 0.8646. The result is reported as registered and no threshold was changed afterwards.

**What `notebook/validate_sample.ipynb` does.** The notebook copies the sample and the unmodified script to a temporary directory and runs it with `--data sample`; the table names in the sample match the ones the script reads. The notebook is executed, with its outputs saved in the file, and writes nothing into the repository.

**What it produced on the sample.** On the 250-account sample the mean AUC is 0.980 (folds 0.950 to 1.000) and the AUC without the audit flags is 0.754. The published values on 5,000 accounts are 0.9927 and 0.8646. Folds hold 50 accounts and the rarest error type has one account.

Figures computed on the sample are **not** a benchmark of the dataset and should not be quoted; the numbers to cite are the published full-dataset ones above. `validation/requirements.txt` pins the package versions the notebook was executed with.

## Licensing

This free sample (data, script and notebook) is released under **CC BY-NC 4.0**: non-commercial use is permitted with attribution. The full dataset is sold under a commercial research license; see the [dataset page](https://sentineldata.com.ua/dataset/patient-liability-financial-assistance-ledger) and the [licence terms](https://sentineldata.com.ua/dataset-license).

## Citation

> Code Sentinel Data, Chekerskyi, M. (2026). *Patient Liability & Financial Assistance Ledger*. Zenodo. https://doi.org/10.5281/zenodo.24159846

## Links

- Full dataset and passport: https://sentineldata.com.ua/dataset/patient-liability-financial-assistance-ledger
- Zenodo record (DOI): https://doi.org/10.5281/zenodo.24159846
- OSF: https://doi.org/10.17605/OSF.IO/EAM5C
- Figshare: https://doi.org/10.6084/m9.figshare.34993918
- Harvard Dataverse: https://doi.org/10.7910/DVN/HTEV1B