"""
D06 - Patient Liability & Financial Assistance Ledger
Detection benchmark: trains a gradient-boosted classifier on the observable
tables and evaluates it against the answer key (liability_finding), using
5-fold cross-validation grouped by patient so no patient appears in both a
train and a test fold.

Reproduces the published metric on the baseline cohort:
    mean AUC 0.9927 +/- 0.0042  (acceptance bar 0.87)
    naive AUC without the three derived audit flags: 0.8646

Usage:
    python3 benchmark_script.py --data ./DATASET --out ./benchmark_out

Environment the published number was produced in (2026-11-10):
    python 3.11, xgboost 3.2.0, scikit-learn 1.8.0, pandas 2.3.3, numpy 2.3.5
Seed fixed at 20261110 throughout; the split is deterministic.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
import xgboost
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier

SEED = 20261110

# HHS poverty guidelines used by the cohort (published annual values);
# applications in years without a published table use the most recent one.
FPL_GUIDELINES = {
    2025: {"base": 15650, "per_additional": 5500},
    2026: {"base": 15960, "per_additional": 5680},
}


def fpl_percentage(income: float, household_size: int, year: int) -> float:
    g = FPL_GUIDELINES[min(year, max(FPL_GUIDELINES))]
    n = max(1, int(household_size))
    return 100.0 * income / (g["base"] + (n - 1) * g["per_additional"])


def load_tables(data_dir: Path):
    tables = {}
    for t in ["patient_account", "assistance_policy_version",
              "assistance_application", "payment", "waterfall_step",
              "liability_finding"]:
        tables[t] = pd.read_parquet(data_dir / f"{t}.parquet")
    for t, df in tables.items():
        for c in df.columns:
            if c.endswith("_date") or c.startswith("effective_"):
                df[c] = pd.to_datetime(df[c])
    return tables


def build_features(t: dict) -> tuple:
    pa, ap, pv, pay, ws, lf = (t["patient_account"], t["assistance_application"],
                               t["assistance_policy_version"], t["payment"],
                               t["waterfall_step"], t["liability_finding"])

    feats = pa[["account_id", "patient_id", "gross_balance",
                "insurance_adjustment", "contractual_write_off",
                "balance_after_insurance", "service_type", "service_date"]].copy()
    feats["insured"] = (feats.insurance_adjustment > 0).astype(int)
    feats["adj_ratio"] = feats.insurance_adjustment / feats.gross_balance
    feats["cwo_ratio"] = feats.contractual_write_off / feats.gross_balance
    feats["service_year"] = feats.service_date.dt.year
    feats["service_month"] = feats.service_date.dt.month

    ap2 = ap.copy()
    ap2["fpl_recomputed"] = [
        fpl_percentage(r.household_income, r.household_size,
                       min(r.application_date.year, max(FPL_GUIDELINES)))
        for r in ap2.itertuples()]

    app_f = ap2[["account_id", "household_income", "household_size",
                 "fpl_percentage", "fpl_recomputed", "eligible",
                 "discount_applied", "assistance_amount", "policy_version",
                 "application_date"]].copy()
    pv_by_version = {r.version: r for r in pv.itertuples()}
    app_f["policy_version_valid"] = [
        pv_by_version[r.policy_version].effective_from <= r.application_date
        <= pv_by_version[r.policy_version].effective_to
        for r in app_f.itertuples()]
    app_f["fpl_mismatch"] = (app_f.fpl_percentage - app_f.fpl_recomputed).abs() > 1.0
    svc_date = feats.set_index("account_id").service_date
    bai = feats.set_index("account_id").balance_after_insurance
    app_f["app_delay_days"] = (app_f.application_date
                               - app_f.account_id.map(svc_date)).dt.days
    app_f["assistance_ratio"] = app_f.assistance_amount / app_f.account_id.map(bai)

    pay_f = pay.pivot_table(index="account_id", columns="source", values="amount",
                            aggfunc="sum", fill_value=0.0)
    for c in ["patient", "charity", "payment_plan", "collection_agency"]:
        if c not in pay_f.columns:
            pay_f[c] = 0.0
    pay_f["n_payments"] = pay.groupby("account_id").size()
    pay_f = pay_f.rename(columns={"patient": "paid_patient", "charity": "paid_charity",
                                  "payment_plan": "paid_plan",
                                  "collection_agency": "paid_collection"})

    ws_f = ws.groupby("account_id").agg(
        n_steps=("step_order", "count"),
        has_bad_debt=("step_type", lambda s: float((s == "bad_debt").any())))
    ws_f["bad_debt_amount"] = ws.loc[ws.step_type == "bad_debt"] \
        .groupby("account_id")["adjustment"].sum().abs()
    coll_scr = ws.pivot_table(index="account_id", columns="step_type",
                              values="step_date", aggfunc="first")
    ws_f["collection_before_screening"] = [
        float(pd.notna(coll_scr.at[a, "collection"])
              and (pd.isna(coll_scr.at[a, "fap_screening"])
                   or coll_scr.at[a, "collection"] < coll_scr.at[a, "fap_screening"]))
        for a in ws_f.index]

    X = feats.merge(app_f.drop(columns=["application_date", "policy_version"]),
                    on="account_id", how="left") \
             .merge(pay_f, on="account_id", how="left") \
             .merge(ws_f, on="account_id", how="left")
    X["has_application"] = X.fpl_percentage.notna().astype(int)
    for c in ["household_income", "household_size", "fpl_percentage",
              "fpl_recomputed", "discount_applied", "assistance_amount",
              "app_delay_days", "assistance_ratio", "eligible",
              "policy_version_valid", "fpl_mismatch"]:
        X[c] = X[c].astype(float)
    X = pd.get_dummies(X, columns=["service_type"], drop_first=False, dtype=float)

    y = lf.set_index("account_id").loc[X.account_id, "error_type"] \
        .notna().astype(int).values
    groups = X.patient_id
    feature_cols = [c for c in X.columns
                    if c not in ("account_id", "patient_id", "service_date")]

    # leakage guard: no answer-key column may enter the features
    leak = [c for c in feature_cols if c in
            ("correct_final_liability", "actual_final_liability", "error_type",
             "scenario_id", "finding_id")]
    if leak:
        raise RuntimeError(f"answer-key columns leaked into features: {leak}")
    return X, y, groups, feature_cols


def main():
    ap = argparse.ArgumentParser(description="D06 detection benchmark")
    ap.add_argument("--data", default="./DATASET",
                    help="directory with the six parquet tables + manifest.json")
    ap.add_argument("--out", default="./benchmark_out",
                    help="output directory for benchmark_results.parquet")
    args = ap.parse_args()

    print(f"D06 benchmark | data={args.data} out={args.out}")
    print(f"versions: xgboost {xgboost.__version__}, scikit-learn {sklearn.__version__}, "
          f"pandas {pd.__version__}, numpy {np.__version__}")

    t = load_tables(Path(args.data))
    X, y, groups, feature_cols = build_features(t)

    model = XGBClassifier(n_estimators=300, max_depth=5, learning_rate=0.1,
                          subsample=0.9, colsample_bytree=0.9, eval_metric="logloss",
                          random_state=SEED, n_jobs=8, verbosity=0)
    gkf = GroupKFold(n_splits=5)
    folds = []
    for k, (tr, te) in enumerate(gkf.split(X[feature_cols], y, groups), 1):
        model.fit(X[feature_cols].iloc[tr], y[tr])
        p = model.predict_proba(X[feature_cols].iloc[te])[:, 1]
        auc = roc_auc_score(y[te], p)
        folds.append({"fold": str(k), "auc": auc, "n_train": len(tr),
                      "n_test": len(te), "prevalence_test": float(y[te].mean())})
        print(f"  fold {k}: AUC {auc:.4f}  (n_test={len(te)}, prev={y[te].mean():.3f})")

    aucs = [f["auc"] for f in folds]
    mean_auc, std_auc = float(np.mean(aucs)), float(np.std(aucs))
    print(f"  mean AUC: {mean_auc:.4f} +/- {std_auc:.4f}  (acceptance bar 0.87)")

    naive_cols = [c for c in feature_cols if c not in
                  ("policy_version_valid", "fpl_mismatch",
                   "collection_before_screening")]
    folds_naive = []
    for tr, te in gkf.split(X[naive_cols], y, groups):
        model.fit(X[naive_cols].iloc[tr], y[tr])
        folds_naive.append(roc_auc_score(y[te],
                                         model.predict_proba(X[naive_cols].iloc[te])[:, 1]))
    naive_auc = float(np.mean(folds_naive))
    print(f"  naive AUC (no audit flags): {naive_auc:.4f}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    bench = pd.DataFrame(folds)
    mean_row = pd.DataFrame([{"fold": "mean", "auc": mean_auc, "n_train": None,
                              "n_test": None, "prevalence_test": None}])
    bench = pd.concat([bench, mean_row], ignore_index=True)
    bench["naive_auc_no_audit_flags"] = naive_auc
    bench.to_parquet(out / "benchmark_results.parquet", index=False)
    print(f"wrote {out / 'benchmark_results.parquet'}")


if __name__ == "__main__":
    main()
