# Coverage Priority & Recovery Timeline — free sample

> **This repository folder contains the technical documentation, validation code and a free evaluation sample (300 of 6,000 claims) — not the full dataset.**
> **Full dataset:** **[sentineldata.com.ua/dataset/coverage-priority-recovery-timeline](https://sentineldata.com.ua/dataset/coverage-priority-recovery-timeline)**

A synthetic COB dataset of 6,000 claims and 2,183 patients: seven linked tables, a hidden answer key flagging 2,100 wrong-order adjudications across six error scenarios, and a Medicare recovery chain with 13 sourced CMS interest rates.

**DOI (Zenodo):** [10.5281/zenodo.24141460](https://doi.org/10.5281/zenodo.24141460)  
**Also archived:** [Figshare](https://doi.org/10.6084/m9.figshare.34983808.v1)

**Status: MODEL-GENERATED / SYNTHETIC.** This is fully synthetic data from a rule engine. No real patients, plans, payers or claims are in it. It supports detection and recovery-logic development and teaching; it is not billing, legal or compliance evidence.

## Sample contents

| File | Rows × Cols | Content |
|---|---:|---|
| `sample/d04_claim.parquet` / `.csv` | 300 × 5 | One row per claim: patient, service date, total charge, injury-related flag. |
| `sample/d04_coverage_period.parquet` / `.csv` | 595 × 12 | One row per patient-coverage: type, effective and end dates, subscriber birthday, plan tenure, dependent flag, and `discovered_at` (the date the coverage first became known to the payer). |
| `sample/d04_coverage_state.parquet` / `.csv` | 404 × 10 | Two rows per claim (state 0 at adjudication and state 1 after full discovery): `known_coverages` (JSON list of coverage ids visible at that date), determined primary and secondary, amounts applied. |
| `sample/d04_demand.parquet` / `.csv` | 104 × 8 | Recovery demand: channel (Medicare or plan-to-plan), demand date, demand principal. |
| `sample/d04_mistaken_payment.parquet` / `.csv` | 104 × 8 | One row per error claim: payer type, amount paid, correct amount, overpayment. |
| `sample/d04_recovery_finding.parquet` / `.csv` | 300 × 14 | The answer key: one row per claim with scenario id, `initial_order_wrong` flag, and `visible_at_adjudication` (whether the error could have been caught at state 0 from observable features). |
| `sample/d04_settlement.parquet` / `.csv` | 104 × 9 | Settlement outcome: type (full / partial / denied), settlement date, interest (Medicare only), total received. |
| `sample/d04_sample_passport_EN.pdf` | — | Sample data passport |
| `sample/manifest.json` | — | Manifest: tables, row counts and checksums |

The sample contains 300 claims drawn by stratified random sampling within each scenario, keeping the error-scenario proportions of the full dataset. All 7 tables are included, restricted to the sampled claims and their linked rows. The `recovery_finding` answer-key table is included in the sample. Coverage periods have more rows per claim than in a simple slice, because the full coverage history of each sampled patient is retained. The sample has no generator code and no validation report.

## About the dataset

The text below is the dataset's description from the product page, converted to Markdown.

When a patient has more than one health plan, the question of which plan pays first is called the order of benefits. Coordination of benefits (COB) errors arise when a payer applies the wrong order: a plan that should pay second pays first, or a plan is left out of the sequence. The result is an overpayment that must be recovered—from the other plan if it is plan-to-plan, or from the provider and potentially from the federal government if Medicare is involved as a secondary payer.

Coverage Priority & Recovery Timeline is a synthetic dataset that models this mechanism. It follows 6,000 claims from 2,183 patients over 24 months (2024-01-01 to 2025-12-31). Each claim is adjudicated twice: once at the service date with the coverage information available then (state 0), and once again after retroactively discovered or terminated coverage is known (state 1). 2,100 of the 6,000 claims (35.0%) are adjudicated with the wrong order of benefits at state 0. For every error claim there is a demand for overpayment recovery and a settlement. For the 687 demands routed through the Medicare channel, interest accrues at the official CMS rate. The `recovery_finding` table is the hidden answer key: it records the scenario and the initial-order-wrong flag for every claim, while the observable tables carry no scenario identifier.

**Status: model-generated.** The dataset is fully synthetic. It contains no real patient, claim or payer. COB rules (birthday rule, MSP statute, workers’ compensation design rule, Medicaid-last principle) are published federal and insurance-industry policy. CMS interest rates and the real COB error base rate are sourced from published government and industry documents. Do not use it as evidence of how any real payer or patient behaves, and do not use it for real billing, compliance or financial decisions.

### At a glance

| Item                      | Value                                                                                     |
|---------------------------|-------------------------------------------------------------------------------------------|
| Scope                     | 6,000 claims, 2,183 patients, 24-month observation window                                 |
| Observation window        | 2024-01-01 to 2025-12-31                                                                  |
| Tables                    | 7 linked tables delivered as Parquet and CSV                                              |
| Error claims              | 2,100 (35.0%) across 6 COB error scenarios                                                |
| Recovery chain            | 2,100 demands; 687 Medicare channel (interest-bearing), 1,413 plan-to-plan                |
| Interest                  | 13 CMS rates (2023-10-17 to 2026-10-21); \$3,861.54 total interest across 242 settlements |
| Answer key                | `recovery_finding` table, hidden from all observable tables                               |
| Unit tests                | 9 tests, all passed (COB rules, MSP, birthday rule, interest formula)                     |
| Structural checks         | 20/20 passed                                                                              |
| Detection AUC (Task A)    | 0.9332 gradient boosting, 0.9310 logistic regression (5-fold GroupKFold by patient)       |
| Settlement predictability | AUC 0.489 (Task B), R² −0.015 (Task C) — near-random by design                            |
| Free sample               | 300 claims, all 7 tables, stratified by error scenario                                    |

### The seven tables

Six tables are observable adjudication data. The seventh, `recovery_finding`, is the answer key and none of the observable tables carries a scenario id or initial-order-wrong flag.

| Table                  | Rows (full) | What it holds                                                                                                                                                                                         |
|------------------------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `d04_claim`            | 6,000       | One row per claim: patient, service date, total charge, injury-related flag.                                                                                                                          |
| `d04_coverage_period`  | 5,252       | One row per patient-coverage: type, effective and end dates, subscriber birthday, plan tenure, dependent flag, and `discovered_at` (the date the coverage first became known to the payer).           |
| `d04_coverage_state`   | 8,100       | Two rows per claim (state 0 at adjudication and state 1 after full discovery): `known_coverages` (JSON list of coverage ids visible at that date), determined primary and secondary, amounts applied. |
| `d04_mistaken_payment` | 2,100       | One row per error claim: payer type, amount paid, correct amount, overpayment.                                                                                                                        |
| `d04_demand`           | 2,100       | Recovery demand: channel (Medicare or plan-to-plan), demand date, demand principal.                                                                                                                   |
| `d04_settlement`       | 2,100       | Settlement outcome: type (full / partial / denied), settlement date, interest (Medicare only), total received.                                                                                        |
| `d04_recovery_finding` | 6,000       | The answer key: one row per claim with scenario id, `initial_order_wrong` flag, and `visible_at_adjudication` (whether the error could have been caught at state 0 from observable features).         |

#### Columns

| Table                  | Columns                                                                                                                                                                                 |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `d04_claim`            | claim_id, patient_id, service_date, total_charge, injury_related                                                                                                                        |
| `d04_coverage_period`  | coverage_id, patient_id, coverage_type, is_dependent, subscriber_birthday_monthday, plan_tenure_years, effective_from, effective_to, end_recorded_at, discovered_at, group_id, payer_id |
| `d04_coverage_state`   | state_id, claim_id, state_date, known_coverages, determined_primary, determined_secondary, primary_amount, secondary_amount, patient_responsibility, state_sequence                     |
| `d04_mistaken_payment` | payment_id, claim_id, payer_type, amount_paid, correct_amount, overpayment                                                                                                              |
| `d04_demand`           | demand_id, payment_id, claim_id, recovery_channel, demand_date, demand_principal                                                                                                        |
| `d04_settlement`       | settlement_id, demand_id, settlement_date, settlement_type, principal_recovered, interest_accrued, total_received, recovery_timeline_days                                               |
| `d04_recovery_finding` | finding_id, claim_id, scenario_id, initial_order_wrong, visible_at_adjudication                                                                                                         |

### Error scenarios

Six COB error scenarios are injected at known rates. All six appear in the answer key; correct claims (scenario `correct_cob`, 65%) are present as negative controls.

| Scenario                          | Share of claims | Mechanism                                                                                                                          |
|-----------------------------------|-----------------|------------------------------------------------------------------------------------------------------------------------------------|
| `correct_cob`                     | 65.0%           | Correct order at both states; negative control.                                                                                    |
| `processing_error_known_coverage` | 20.1%           | Coverage was fully known at adjudication but applied in the wrong order.                                                           |
| `retroactive_termination`         | 7.5%            | A coverage termination is recorded after the service date, changing the order retroactively.                                       |
| `birthday_rule_misapplied`        | 3.5%            | The birthday rule (earlier month-day = primary for dependents on two parents’ plans) is applied with the wrong winner or skipped.  |
| `late_discovery_employer`         | 2.9%            | An employer-sponsored plan is discovered after adjudication; it would have been primary under the MSP employer-plan rule.          |
| `late_discovery_nghp`             | 1.0%            | A non-group health plan (auto or workers’ comp) is discovered late; it is primary to Medicare and to group health plans under MSP. |

The `visible_at_adjudication` column in the answer key marks whether the error could have been detected from the state 0 snapshot alone. Processing errors on known coverage are always visible (100%); retroactive-termination and late-discovery errors are not visible at state 0 because the information arrives later.

### COB rules as modeled

The rule engine follows the NAIC COB Model Regulation priority sequence, the Medicare Secondary Payer statute (42 U.S.C. §1395y(b)), the birthday rule for dependents, and the design rules for workers’ compensation and Medicaid-last. The resolution order for a claim is:

1.  Non-group health plans (workers’ compensation, auto) are primary to all group plans and to Medicare.
2.  Medicare Secondary Payer: an employer group health plan with 20+ employees is primary to Medicare for an active employee.
3.  Among group plans for a dependent covered on two parents’ plans: the subscriber whose birthday (month and day) falls earlier in the calendar year is primary (birthday rule). Tie on month-day: the plan with longer continuous enrollment is primary.
4.  Medicaid is always last payer.

The rule engine and interest table are shipped with the generator package.

### Recovery and interest

Recovery runs on two channels. Plan-to-plan recovery (1,413 demands) carries no interest. Medicare-channel recovery (687 demands) accrues interest under the CMS schedule published at 42 C.F.R. §405.378.

Interest formula: `monthly_interest = round(principal × rate / 12, 2)`; `periods = days_after_demand ÷ 30` (floored; zero if fewer than 60 days); `interest = monthly_interest × periods`. Total interest across all 242 interest-bearing settlements: \$3,861.54.

Thirteen CMS interest rates are stored in the dataset, covering 2023-10-17 to 2026-10-21. The rate applicable on the demand date is used for the life of that demand.

### Validation

The validation suite covers the full 6,000-claim dataset against its structural contract and against three prediction tasks.

#### Structural checks

| Area                            | What was checked                                                                                      |
|---------------------------------|-------------------------------------------------------------------------------------------------------|
| Primary keys                    | Unique across all 7 tables.                                                                           |
| Foreign keys                    | All join keys resolve; one finding per claim.                                                         |
| Charge arithmetic               | primary + secondary + patient_responsibility = total_charge on every state row (max diff 0.0000).     |
| Amounts                         | No negative or zero amounts.                                                                          |
| Enumerated values               | All coverage types, settlement types, channel values within defined sets.                             |
| Coverage date ordering          | effective_from ≤ effective_to on every coverage row.                                                  |
| State sequencing                | State 0 date is on or after service date; state 1 date is after state 0.                              |
| Payment/demand/settlement chain | payment \< demand \< settlement date; state 1 date \> state 0 date.                                   |
| Coverage visibility             | known_coverages at state date contains only coverages with discovered_at ≤ state_date (0 violations). |
| Medicare interest               | Recomputed from the rate table; plan-to-plan carries no interest.                                     |
| Settlement arithmetic           | total_received = principal_recovered + interest_accrued; denied settlements recover nothing.          |
| Correct claims                  | No payment, demand or overpayment on correct claims.                                                  |
| Error claims                    | Every error claim has a positive overpayment and a demand.                                            |
| Answer-key leakage              | No scenario id, initial-order-wrong or finding id column in any observable table.                     |
| Medicare exclusivity            | At most one Medicare coverage per patient.                                                            |
| Service dates                   | All within the 24-month horizon.                                                                      |

#### Unit tests

Nine unit tests cover the rule engine and interest formula: MSP chapter-3 example, CMS interest example, interest grace boundary, rate table lookup, non-dependent-first rule, birthday rule, birthday tie (longest coverage wins), employer-before-Medicare-before-Medicaid ordering, and NGHP-before-GHP ordering. All 9 passed.

#### Detection benchmark

Task A is day-0 triage: for each claim, using only what was visible at the state-0 adjudication date, predict whether the initial order of benefits is wrong. Features include coverage count, coverage types, injury flag, log charge, adjudication lag, primary type, dependent flag, plan tenure, late-discovered coverage count, recorded-end coverage count, and an audit-rule feature (does re-applying the rule engine to the visible coverages contradict the recorded primary?). The benchmark uses 5-fold GroupKFold stratified by patient, so a patient’s claims never appear in both train and test.

| Model               | AUC    | PR-AUC | AUC w/o rule feature |
|---------------------|--------|--------|----------------------|
| Logistic regression | 0.9310 | 0.9101 | 0.8711               |
| Gradient boosting   | 0.9332 | 0.9135 | 0.8956               |

The rule-mismatch feature alone reaches AUC 0.837 with recall 1.0 on visible-error scenarios and zero false alarms on correct claims. Without the rule feature, AUC drops to 0.87–0.90, which confirms that residual signal comes from coverage attributes (types, counts, tenure, injury flag) rather than from the rule engine alone.

Task B (predict settlement type among the 2,100 demands) gives AUC 0.489: near chance by design, because settlement timing is modeled as independent of observable features. Task C (predict days from demand to settlement) gives R² −0.015, confirming the same independence.

### Who uses this data

- Developers and data scientists building or testing COB resolution algorithms and payer-order engines, with a known answer key to score against.
- Teams training supervised models to detect wrong-order adjudications from observable claim and coverage attributes, using the day-0 feature set and the hidden label.
- Researchers studying Medicare Secondary Payer (MSP) rules, birthday rule, retroactive termination and late-discovery scenarios in a controlled, labeled environment.
- Educators teaching benefit coordination and COB error identification with a dataset where every rule and every error has a source.
- QA engineers testing claim adjudication systems against a dataset where the correct resolution is documented for each of the 6,000 claims.

### Limits you should know about

- The dataset models COB rules as published policy. It does not capture clerical variation, regional payer practices or institutional-specific adjudication workflows.
- Settlement timing (Task C, R² −0.015) and outcome (Task B, AUC 0.489) are near-random: settlement is modeled as independent of observable features, which is declared as an assumption (A7 in the passport). The dataset documents the financial chain, not the settlement-prediction task.
- The error share (35%) is a declared generator parameter, not an estimate of real COB error rates. The real rate from the sourced literature (REF01) is 2.26% of high-dollar claim lines.
- The dataset covers US health insurance COB rules only.
- No diagnosis or procedure codes are present.
- The free sample covers all six scenarios but only 300 of 6,000 claims and proportionally fewer recovery rows.

## Reproducing the validation on the sample

`validation/benchmark_script.py` is the script used for the published benchmark, reproduced here **unmodified** from the dataset's validation package. It runs three tasks: Task A day-0 triage of wrong-order adjudications (logistic regression and gradient boosting, 5-fold GroupKFold), Task B settlement outcome, Task C days to settlement.

**Published result, full dataset:**

- Structural checks passed: 20/20
- Unit tests passed: 9/9
- Task A day-0 triage (5-fold GroupKFold, 5,320 claims, 35% positive):
  - Logistic regression: AUC 0.9310, PR-AUC 0.9101
  - Gradient boosting: AUC 0.9332, PR-AUC 0.9135
  - Rule-mismatch detector only: AUC 0.8371, recall_visible=1.0, false_alarm=0.0
- Task B settlement outcome (n=2,100 demands): AUC 0.4888 (near chance — settlement is not predictable at demand time)
- Task C days to settlement (n=2,100): R²=-0.0148, MAE=31.4 days

**Note on the published result.** Task B AUC of 0.49 is a deliberate finding rather than a modeling failure. The settlement outcome (full vs. partial/waived) is structurally unpredictable at demand time: it depends on post-demand negotiation, payer-specific recovery policies, and legal proceedings that are not observable in the claim or coverage data. Task A validates the core COB rule engine: a pure rule-mismatch detector achieves AUC 0.84 with zero false alarms on correct-COB claims, while a gradient-boosting model using all visible features reaches AUC 0.93.

**What `notebook/validate_sample.ipynb` does.** **The script cannot be run on the sample.** It imports `d04_generator`, the rule engine and interest table that ship with the generator, to recompute claim priority orders and interest rates. The notebook shows the failed import, then verifies what the sample alone supports: every table's SHA-256 and row count against the shipped manifest, and the scenario mix of the answer-key table. The notebook is executed, with its outputs saved in the file, and writes nothing into the repository.

**What it produced on the sample.** All seven tables match the manifest (row counts and hashes). The answer key shows the sampled scenario mix: 196 correct-COB claims (65.3%), 60 processing errors with known coverage, 22 retroactive terminations, 10 birthday-rule errors, 9 late-discovery employer cases and 3 late-discovery NGHP cases.

Figures computed on the sample are **not** a benchmark of the dataset and should not be quoted; the numbers to cite are the published full-dataset ones above. `validation/requirements.txt` pins the package versions the notebook was executed with.

## Licensing

This free sample (data, script and notebook) is released under **CC BY-NC 4.0**: non-commercial use is permitted with attribution. The full dataset is sold under a commercial research license; see the [dataset page](https://sentineldata.com.ua/dataset/coverage-priority-recovery-timeline) and the [licence terms](https://sentineldata.com.ua/dataset-license).

## Citation

> Code Sentinel Data, Chekerskyi, M. (2026). *Coverage Priority & Recovery Timeline*. Zenodo. https://doi.org/10.5281/zenodo.24141460

## Links

- Full dataset and passport: https://sentineldata.com.ua/dataset/coverage-priority-recovery-timeline
- Zenodo record (DOI): https://doi.org/10.5281/zenodo.24141460
- Figshare: https://doi.org/10.6084/m9.figshare.34983808.v1