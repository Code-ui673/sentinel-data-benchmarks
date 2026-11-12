# Research Grant Full-Cost Ledger — free sample

> **This repository folder contains the technical documentation, validation code and a free evaluation sample (2 of 80 awards (438 of 16,356 expenditure rows)) — not the full dataset.**
> **Full dataset:** **[sentineldata.com.ua/dataset/research-grant-full-cost-ledger](https://sentineldata.com.ua/dataset/research-grant-full-cost-ledger)**

A synthetic ledger of 80 research grants from five funders (NIH, MRC, Wellcome, Horizon Europe, UKRI): ten linked tables, a daily cash-gap series and a separate answer key of 401 findings. It reproduces how funder rules leave a university out of pocket. 31 of 31 checks passed, one prediction is reported as failed.

**DOI (Zenodo):** [10.5281/zenodo.24090703](https://doi.org/10.5281/zenodo.24090703)  
**Also archived:** [OSF](https://doi.org/10.17605/OSF.IO/EDY2H) · [Harvard Dataverse](https://doi.org/10.7910/DVN/S1X0HL)

**Status: MODEL-GENERATED / SYNTHETIC.** This is fully synthetic data from a rule-based generator. The awards, funders' rule sets and numbers are modelled on published funder policies; no real institution, grant or expenditure is in it. It supports detection-logic development, cash-flow research and teaching; it is not audit evidence.

## Sample contents

| File | Rows × Cols | Content |
|---|---:|---|
| `sample/d09_sample.parquet` / `.csv` | 438 × 21 | Denormalised table: expenditure rows joined with their award attributes, 21 columns |
| `sample/d09_sample_passport_EN.pdf` | — | Sample data passport |
| `sample/working_with_parquet.txt` | — | How to open the Parquet files (pandas / R arrow / DuckDB) |

The sample is a strict row subset of the full dataset: 2 awards and 438 expenditure rows, joined with their award attributes into one denormalized table of 21 columns, delivered as Parquet and as a CSV twin. Its purpose is to check schema, formats and value ranges before licensing the full dataset. The two awards are AW0001 (Oncology, 204 rows, 2023-03-31 to 2025-12-31) and AW0002 (Infection and Immunity, 234 rows, 2022-10-31 to 2025-12-31). Both are NIH awards in USD, so the sample shows the NIH rule set only and none of the other four funders. Each of the six categories has 73 rows. Four of the 438 rows are flagged as ineligible (two alcohol, one PhD studentship, one publication cost). The sample has no answer key and no claim or receipt tables, and it does not contain the daily cash-gap series.

## About the dataset

The text below is the dataset's description from the product page, converted to Markdown.

A university spends money on a research grant first and gets it back later, and usually gets back less than it spent. The UK sector ran a research deficit of £5,367 million in 2023-24 and recovered 66.0% of the full economic cost of its research (median 58.1%), according to the TRAC annual return. MRC and UKRI pay 80% of full economic cost, Wellcome caps overheads at 20%, Horizon Europe pays a 25% flat indirect rate, and NIH reimburses facilities and administrative costs on a modified total direct cost base. Each funder also pays on its own schedule, so the gap between what has been spent and what has arrived changes every day and differs from funder to funder.

Research Grant Full-Cost Ledger is a synthetic ledger of that mechanism. It follows 80 research awards at a medical university across five funders (NIH, MRC, Wellcome, Horizon Europe and UKRI) from 2022-01-01 to 2025-12-31. The ledger holds budgets, monthly expenditures, claims to funders, cash receipts, indirect-cost allocation and a derived daily cash-gap series for every award and for the whole portfolio. A separate answer key marks five kinds of violation, so the same data can be used for supervised detection as well as for forecasting and policy simulation.

**Status: model-generated.** The dataset is fully synthetic. It contains no real award, person or transaction. The funder rules and sector figures are published policies captured on the dates given in the source list below, and the scenario injection rates are declared parameters of the generator. Do not use it as evidence of how any real institution or funder behaves, and do not use it for real financial or compliance decisions.

### At a glance

| Item                | Value                                                                                                                                        |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| Scope               | 80 research awards at one medical university, 5 departments, 5 funders: NIH, MRC, Wellcome, Horizon Europe, UKRI                             |
| Observation window  | 2022-01-01 to 2025-12-31                                                                                                                     |
| Tables              | 10 linked tables, 111,676 rows in total, delivered as Parquet and CSV                                                                        |
| Largest tables      | daily_cash_gap 91,102 rows; expenditure 16,356 rows                                                                                          |
| Currencies          | Award currency USD, EUR or GBP; portfolio aggregation in GBP at ECB reference rates                                                          |
| Answer key          | 401 findings across five violation scenarios, plus negative-control awards whose gap is fully explained by policy design                     |
| Constants           | 44 audited constants; 36 VERIFIED and 7 ESTIMATE_SOURCED with explicit derivations; no unsourced estimates                                   |
| Sources             | 12 verbatim source captures with queries, dates and URLs                                                                                     |
| Validation          | 31 machine checks, 0 failures; 6 of 7 pre-registered predictions passed and the failed one is disclosed                                      |
| Detection benchmark | Ineligible-cost detection from observable features: AUC 0.8633 (logistic regression) and 0.8826 (gradient boosting), 5-fold cross-validation |
| Random seed         | 20261101                                                                                                                                     |
| Free sample         | 2 awards, 438 expenditure rows joined with award attributes, in Parquet and CSV                                                              |

### The ten tables

Nine tables are observable ledger data. The tenth, `finding`, is the answer key and none of the observable tables carries a finding type, finding id or scenario id.

| Table                      | Rows   | What it holds                                                                                                                                                       |
|----------------------------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `award`                    | 80     | One row per award: funder, program, awarded amount, start and end dates, principal investigator, department and the funder policy that applies.                     |
| `award_financials`         | 80     | Award currency, annual direct budget, FTE count, negotiated F&A rate and overhead rate.                                                                             |
| `funder_policy`            | 5      | One row per funder: direct and indirect cost coverage, indirect cap, payment schedule, payment lag, eligible and ineligible cost categories, cofunding requirement. |
| `budget_version`           | 480    | Budget lines by category (personnel, equipment, consumables, travel, subcontract, overhead), versioned with an effective date.                                      |
| `expenditure`              | 16,356 | Monthly expenditure rows with an eligibility flag and an ineligibility reason.                                                                                      |
| `indirect_cost_allocation` | 336    | Quarterly actual and claimable indirect cost plus the institutional contribution, for UK full-economic-cost awards.                                                 |
| `claim_to_funder`          | 1,411  | Claims with the direct and indirect split and the submission date.                                                                                                  |
| `cash_receipt`             | 1,425  | Cash receipts with withholding, including Horizon Europe prefinancing and MIM retention.                                                                            |
| `daily_cash_gap`           | 91,102 | Award-day rows: cumulative cost, cumulative received, cash gap and portfolio cash gap, in GBP at ECB reference rates.                                               |
| `finding`                  | 401    | The answer key: findings from five violation scenarios, with recomputed amounts and evidence record ids. Ships as a separate table.                                 |

#### Columns

| Table                      | Columns                                                                                                                                                                                          |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `award`                    | award_id, funder, program, awarded_amount, start_date, end_date, pi_id, department, funder_policy_id                                                                                             |
| `award_financials`         | award_id, currency, annual_direct, n_fte, negotiated_fa_rate, overhead_rate                                                                                                                      |
| `funder_policy`            | policy_id, funder, direct_cost_coverage, indirect_cost_coverage, indirect_cost_cap, payment_schedule, payment_lag_days, eligible_cost_categories, ineligible_cost_categories, cofunding_required |
| `budget_version`           | budget_id, award_id, version, effective_date, category, budgeted_amount                                                                                                                          |
| `expenditure`              | expenditure_id, award_id, date, category, amount, description, eligible, ineligibility_reason                                                                                                    |
| `indirect_cost_allocation` | allocation_id, award_id, period_start, period_end, actual_indirect_cost, claimable_indirect_cost, institutional_contribution                                                                     |
| `claim_to_funder`          | claim_id, award_id, period, direct_claimed, indirect_claimed, total_claimed, submission_date                                                                                                     |
| `cash_receipt`             | receipt_id, award_id, claim_id, receipt_date, amount_received, withholding                                                                                                                       |
| `daily_cash_gap`           | date, award_id, cumulative_cost, cumulative_received, cash_gap, portfolio_cash_gap                                                                                                               |
| `finding`                  | finding_id, award_id, finding_type, amount, evidence_record_ids, scenario_id                                                                                                                     |

### Funder policies as modeled

| Funder         | Direct coverage | Indirect coverage | Payment schedule        | Lag, days |
|----------------|-----------------|-------------------|-------------------------|-----------|
| NIH            | 1.0             | 0.58              | monthly_advance         | 5         |
| MRC            | 0.8             | per_fte_fec       | quarterly_in_arrears    | 25        |
| Wellcome       | 1.0             | 0.2               | quarterly_reimbursement | 30        |
| Horizon Europe | 1.0             | 0.25              | periodic_report         | 90        |
| UKRI           | 0.8             | per_fte_fec       | quarterly_in_arrears    | 25        |

The table above is the generator's policy configuration, taken from the captured sources. MRC and UKRI pay 80% of full economic cost, and the remaining 20% is the institutional share. For both, indirect and estates costs enter as per-FTE full-economic-cost rates. NIH is modeled with a negotiated F&A mean of 0.58. Ineligible categories differ by funder, for example publication costs under MRC, and alcohol and NHS basic computing under UKRI.

### How the cash gap is built

Most synthetic financial datasets are static tables. This one is a state machine. Expenditure accrues continuously, month by month, while claims go out in discrete cycles and cash comes back after a funder-specific lag. Horizon Europe adds prefinancing and retention, and the funders apply ceilings, so the cash gap of an award follows a sawtooth: it grows as costs accrue and drops on each receipt date. Portfolio-level effects also come out of the data and are not painted on top. One grant's surplus can cover another grant's gap, and the portfolio series shows it.

The daily series obeys one identity that is tested on every award-day row: `cash_gap(t) = cumulative_cost(t) − cumulative_received(t)`. The largest violation in the validation run was 7e-10, which is float noise. The portfolio gap series is identical across all awards for a given date. In the validation report, a run with full coverage, zero payment lag and no injected errors (degenerate limit, pre-registered seed 777) gives a maximum absolute cash gap of 0.00 at horizon close across all 80 awards.

One behavior is worth knowing before you build on the series. Horizon Europe awards that settle after the observation window closes keep an unclaimed tail at the end of the window. The validation report classes this as arrears semantics of the funder and not as a model error.

### The answer key

The `finding` table holds 401 findings. Every finding carries a recomputed amount and the ids of the records that prove it, so a detection system can be scored on the cash value it finds and not only on a hit count. The five scenarios are:

- an ineligible cost charged to a grant;
- an indirect cost claimed over the funder's cap;
- a claimable period that was never claimed;
- a cofunding shortfall;
- a payment delay that exceeds the funder's policy.

The set also includes negative-control awards, whose gap is fully explained by policy design and which should raise no finding. Injection rates are declared knobs of the generator and are not claimed to match any real audit rate. In the expenditure table, 2.1% of the 16,356 rows are flagged as ineligible, and that share is the prevalence in the detection benchmark below.

The validation report checks that the key does not leak. No finding-type, finding-id or scenario-id column appears in any observable table, and the detection benchmark stays well under the leakage ceiling (AUC below 0.995).

### Sourced constants

Every empirical constant was captured verbatim from a live source during generation. The audit covers 44 constants: 36 are VERIFIED against a source, 7 are ESTIMATE_SOURCED with an explicit derivation, and none is an unsourced estimate. Scenario injection rates are declared knobs. An excerpt of the audit:

| Parameter                                     | Value                | Tier     |
|-----------------------------------------------|----------------------|----------|
| `ukri_fec_coverage`                           | 0.8                  | VERIFIED |
| `ukri_institutional_share`                    | 0.2                  | VERIFIED |
| `mrc_ineligible_publication_costs`            | 1                    | VERIFIED |
| `ukri_ineligible_alcohol_nhs_basic_computing` | 1                    | VERIFIED |
| `ukri_payment_schedule`                       | quarterly_in_arrears | VERIFIED |
| `ukri_claim_payment_days`                     | 30                   | VERIFIED |
| `trac_research_deficit_2023_24`               | 5367                 | VERIFIED |
| `trac_research_fec_recovery_2023_24`          | 0.66                 | VERIFIED |
| `trac_ukri_councils_recovery`                 | 0.681                | VERIFIED |
| `trac_uk_charities_recovery`                  | 0.556                | VERIFIED |
| `trac_industry_recovery`                      | 0.75                 | VERIFIED |
| `trac_research_income_total`                  | 10440                | VERIFIED |
| `trac_research_fec_total`                     | 15807                | VERIFIED |
| `nih_negotiated_fa_mean`                      | 0.58                 | VERIFIED |

The 12 source captures, each stored with its search query, capture date (2026-11-01) and URL:

- Annual TRAC 2023-24, sector summary and analysis by TRAC peer group, Office for Students (sector aggregates).
- UKRI, MRC research grant financial support (80% full economic cost policy).
- Congressional Research Service IN12516, NIH Indirect Costs Policy for Research (F&A rates).
- Horizon Europe Model Grant Agreement (funding rates and payment mechanics).
- Wellcome, Overheads Policy.
- NIH Data Book, R01-equivalent grants: average size.
- NIH Modular Grant Application update, peer review (composition of budgets).
- UKRI, Getting your funding (payment mechanics).
- NIH, Federal Financial Report (payment mechanics).
- UKRI, Roles in funding applications (institutional 20% share).
- TRAC guidance v3.0, section 5, calculation of research project costs (indirect and estates as per-FTE rates).
- ECB reference exchange rates through the frankfurter.dev API (portfolio conversion).

### Validation

The validation report covers the generated baseline (80 awards, 5 funders, 2022-01-01 to 2025-12-31) against its structural contract: nulls, shapes, distributions, ranges, cross-table coherence, invariants, the degenerate limit and answer-key leakage. The result is 31 checks and 0 failures.

#### Structural checks

| Area                  | What was checked                                                                                                            |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------|
| Completeness          | No nulls in the key fields of all six core tables.                                                                          |
| Shape                 | 80 awards, 5 funders, 5 departments.                                                                                        |
| Dates and amounts     | All expenditure dates inside the award life and the observation horizon; all amounts strictly positive.                     |
| Referential integrity | No orphan claims and no orphan receipts.                                                                                    |
| Policy                | The MRC and UKRI direct claim ratio equals the 80% FEC policy (0.7925 after injections).                                    |
| Categories            | All six expenditure categories are present.                                                                                 |
| Cash-gap identity     | cash_gap(t) = cumulative_cost(t) − cumulative_received(t) holds for every award-day row; maximum violation 7e-10.           |
| Portfolio series      | The portfolio gap series is identical across awards for each date.                                                          |
| Degenerate limit      | Full coverage, zero lag and no injected errors give a maximum absolute cash gap of 0.00 at horizon close for all 80 awards. |
| Answer-key leakage    | No finding-type, finding-id or scenario-id column in any observable table.                                                  |

#### Detection benchmark

The task is to flag ineligible cost charges from observable features: funder, department, category, log amount, month, award age, number of FTE and annual direct budget. The benchmark runs on all 16,356 expenditure rows (prevalence 0.021) with 5-fold stratified cross-validation and a fixed seed. The benchmark script is shown in full in the validation panel of the dataset page, so it can be read before licensing the full dataset.

| Model                                           | AUC (5-fold CV) |
|-------------------------------------------------|-----------------|
| Logistic regression (C = 1.0, max_iter = 2000)  | 0.8633          |
| Gradient boosting (200 estimators, max depth 3) | 0.8826          |

Both results sit inside the band published for machine-learning audit-anomaly detection: AUC 0.85 to 0.95 on journal-entry and misstatement detection (Bakumenko and Elragal 2022, Systems 10(5):130) and AUC 0.88 to 0.92 for random forest, SVM and logistic regression internal-audit risk prediction (Li 2024, Proc. ICEDAI). They are above chance, so the scenario injection carries learnable signal. They are below 1.0, so the answer key does not leak. The number measures how learnable the injected scenarios are and says nothing about performance on real audit data.

#### Pre-registered predictions

Seven predictions were written down before the generation run, and their sheet is fixed by a SHA-256 hash (2e3e3de0a0246ed1… in the passport). Six passed. One failed as worded, and the report says so.

| \#  | Prediction                                                                                | Result                                                       |
|-----|-------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| P1  | Portfolio FEC recovery between 0.60 and 0.72, anchored on the TRAC 2023-24 figure of 0.66 | PASS, observed 0.6591                                        |
| P2  | Funder gap signs                                                                          | **FAILED as worded**                                         |
| P3  | NIH effective indirect recovery between 0.25 and 0.45                                     | PASS, observed 0.4329                                        |
| P4  | Personnel share between 0.60 and 0.75                                                     | PASS, observed 0.6748                                        |
| P5  | Sawtooth dynamics for arrears funders                                                     | PASS, 100% of large negative gap jumps fall on receipt dates |
| P6  | Degenerate limit gives zero gap                                                           | PASS                                                         |
| P7  | Benchmark above chance, below 1.0, no leakage                                             | PASS                                                         |

**About the failed prediction.** P2 was written with the opposite sign convention (gap = received − cost) and assumed a near-zero NIH gap. Under the convention used in the dataset (exposure = cost − received), every funder shows a positive exposure, because under-recovery of overhead outweighs payment timing. The mechanism the prediction was after, that NIH has the smallest mean exposure when converted to GBP, is confirmed. The prediction is reported as failed as worded.

### Reproducibility

Generation runs from a single configuration with seed 20261101. The outputs are byte-identical on Python 3.11, pandas 2.3 and numpy 2.1 (run on Python 3.11.13 and pandas 2.3.1). The delivery includes a manifest with a SHA-256 hash for every file, so you can verify the files you receive.

### Who uses this data

- Research offices and finance teams building cash-flow and working-capital forecasts for grant portfolios.
- Teams that write detection logic for ineligible costs, missed claims, over-cap indirects and late payments, either rule-based or supervised, and need an answer key with amounts and evidence ids.
- Analysts working on portfolio exposure and on funder-policy simulation, for example what happens to the gap when a coverage rate or a payment lag changes.
- Instructors who teach research financial management and want one ledger in which every policy constant has a source.

### Limits you should know about

- The dataset describes one fictional medical university and 80 awards. It reproduces the mechanism of funder-specific cash gaps and does not estimate the real size of any institution's gap.
- Funder constants reflect published policies as of the capture date, 2026-11-01. Policies change.
- Scenario injection rates are declared parameters. The detection AUC shows how learnable the injected scenarios are and cannot be read as a forecast of performance on real ledgers.
- One of seven pre-registered predictions failed as worded, and the report documents it.
- Horizon Europe awards carry an unclaimed tail at the end of the window when they settle after the window closes.
- The free sample covers NIH awards only.

## Reproducing the validation on the sample

`validation/benchmark_script.py` is the script used for the published benchmark, reproduced here **unmodified** from the dataset's validation package. It flags ineligible cost charges from observable features with logistic regression and gradient boosting, 5-fold stratified cross-validation, seed 20261101.

**Published result, full dataset:**

- Structural checks passed: 31/31
- Pre-registered predictions: 6 of 7 passed, 1 failed as worded (P2)
- Detection AUC (5-fold CV, 16,356 rows): 0.8633 logistic regression, 0.8826 gradient boosting
- Degenerate limit: maximum absolute cash gap 0.00 across all 80 awards

**Note on the published result.** Prediction P2 on funder gap signs failed as worded. It was pre-registered with the opposite sign convention and assumed a near-zero NIH gap. Under the dataset's own convention, where exposure is cost minus received, every funder shows positive exposure, because under-recovery of overhead outweighs payment timing. The mechanism it was after, NIH having the smallest mean exposure in GBP, is confirmed. The detection AUC of 0.86 to 0.88 measures how learnable the injected violation scenarios are from observable features. It sits above chance and below 1.0, which means the scenarios carry signal and the answer key does not leak, and it says nothing about accuracy on real audit data. Horizon Europe awards that settle after the window closes keep an unclaimed tail, which the report treats as arrears semantics and not as a model error.

**What `notebook/validate_sample.ipynb` does.** The script expects the full dataset's three tables (`expenditure`, `award`, `award_financials`). The sample ships one denormalised table, so the notebook splits it back into three tables with the same column names in a temporary directory, changing no values, and runs an unmodified copy of the script on them. The notebook is executed, with its outputs saved in the file, and writes nothing into the repository.

**What it produced on the sample.** The sample has 4 ineligible rows out of 438, so scikit-learn warns that the smallest class is below the number of folds. Logistic regression gets AUC 0.833 and gradient boosting 0.426, below chance, which only shows that four positive rows cannot support a benchmark. The published values are 0.8633 and 0.8826 on 16,356 rows.

Figures computed on the sample are **not** a benchmark of the dataset and should not be quoted; the numbers to cite are the published full-dataset ones above. `validation/requirements.txt` pins the package versions the notebook was executed with.

## Licensing

This free sample (data, script and notebook) is released under **CC BY-NC 4.0**: non-commercial use is permitted with attribution. The full dataset is sold under a commercial research license; see the [dataset page](https://sentineldata.com.ua/dataset/research-grant-full-cost-ledger) and the [licence terms](https://sentineldata.com.ua/dataset-license).

## Citation

> Code Sentinel Data, Chekerskyi, M. (2026). *Research Grant Full-Cost Ledger*. Zenodo. https://doi.org/10.5281/zenodo.24090703

## Links

- Full dataset and passport: https://sentineldata.com.ua/dataset/research-grant-full-cost-ledger
- Zenodo record (DOI): https://doi.org/10.5281/zenodo.24090703
- OSF: https://doi.org/10.17605/OSF.IO/EDY2H
- Harvard Dataverse: https://doi.org/10.7910/DVN/S1X0HL