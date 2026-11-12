# Benchmark for D04. Usage: python benchmark_script.py --data ../DATASET --out ../VALIDATION
# Python 3.13, pandas 2.3, numpy 2.2, scikit-learn (tested versions are written to benchmark_meta.json).
#
# Task A  Day-0 triage: for each claim, using only what was known on the adjudication date,
#         predict whether the initial order of benefits is wrong.
# Task B  Settlement outcome among demands (is it predictable at demand time?).
# Task C  Days from demand to settlement among demands (service-to-demand time is a feature, so the target excludes it).
#
# Every feature is built from rows and dates visible on the state-0 date. Coverage rows that
# were discovered later, and end dates recorded later, are removed before features are built.
import argparse, json, os, sys
from datetime import date
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "GENERATOR", "GENERATOR"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d04_generator as core  # rule engine and interest table, shipped with the generator

BASE_RATE_REAL = 2022 / 89543  # erroneous share of the audited high-dollar claim lines (REF01 in d04_literature_registry.csv)
TYPES = ["employer", "medicare", "medicaid", "auto", "workers_comp"]


def load(d):
    t = {}
    for n in ["coverage_period", "claim", "coverage_state", "demand", "settlement", "recovery_finding", "mistaken_payment"]:
        t[n] = pd.read_parquet(f"{d}/d04_{n}.parquet")
    return t


def day0_features(t):
    cp, cl, st = t["coverage_period"], t["claim"], t["coverage_state"]
    s0 = st[st.state_id.str.endswith("0")].merge(cl, on="claim_id")
    cpi = {r["coverage_id"]: r for r in cp.to_dict("records")}
    by_payer = {}
    h0 = date(2024, 1, 1)
    rows = []
    for r in s0.itertuples():
        known = json.loads(r.known_coverages)
        cov = [cpi[c] for c in known]
        # drop anything not visible on the state date
        cov = [c for c in cov if c["discovered_at"] <= r.state_date]
        d = {"claim_id": r.claim_id, "patient_id": r.patient_id}
        d["n_known"] = len(cov)
        for ty in TYPES:
            d[f"n_{ty}"] = sum(c["coverage_type"] == ty for c in cov)
        d["n_dependent"] = sum(bool(c["is_dependent"]) for c in cov)
        d["injury_related"] = int(r.injury_related)
        d["log_charge"] = float(np.log(r.total_charge))
        d["adjud_lag_days"] = (r.state_date - r.service_date).days
        d["primary_type"] = TYPES.index(core.ptype(r.determined_primary))
        d["has_secondary"] = int(r.determined_secondary is not None and r.determined_secondary == r.determined_secondary)
        d["service_month"] = r.service_date.month
        d["max_tenure_yrs"] = max([c["plan_tenure_years"] for c in cov], default=0.0)
        d["n_late_discovered"] = sum(c["discovered_at"] > c["effective_from"] for c in cov)
        # coverages with a recorded end that is already visible
        d["n_recorded_end"] = sum((c["end_recorded_at"] is not None and c["end_recorded_at"] == c["end_recorded_at"]
                                   and c["end_recorded_at"] <= r.state_date) for c in cov)
        # the audit rule: recompute the order from visible coverages and compare
        active = []
        for c in cov:
            cc = dict(c)
            cc["tenure_days"] = max(0, (h0 - c["effective_from"]).days)
            b = c["subscriber_birthday_monthday"]
            cc["subscriber_birthday_monthday"] = b if isinstance(b, str) else None
            active.append(cc)
        order = core.resolve_priority(active) if active else []
        d["rule_mismatch"] = int(bool(order) and order[0] != r.determined_primary)
        rows.append(d)
    return pd.DataFrame(rows)


def cv_scores(X, y, groups, make_model, n_splits=5):
    oof = np.zeros(len(y))
    for tr, te in GroupKFold(n_splits=n_splits).split(X, y, groups):
        m = make_model()
        m.fit(X.iloc[tr], y[tr])
        oof[te] = m.predict_proba(X.iloc[te])[:, 1]
    return oof


def reweighted_precision(y, score, k_frac=0.02, base=BASE_RATE_REAL):
    # precision among the top k_frac of scores after reweighting positives to the real base rate
    n = len(y); pos = y.sum(); neg = n - pos
    w = np.where(y == 1, base / (pos / n), (1 - base) / (neg / n))
    top = np.argsort(-score)[: max(1, int(k_frac * n))]
    return float((w[top] * y[top]).sum() / w[top].sum())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t = load(a.data)
    rf = t["recovery_finding"]
    F = day0_features(t).merge(rf[["claim_id", "initial_order_wrong", "scenario_id", "visible_at_adjudication"]], on="claim_id")
    y = F.initial_order_wrong.astype(int).values
    groups = F.patient_id.values
    feats = [c for c in F.columns if c not in ("claim_id", "patient_id", "initial_order_wrong", "scenario_id", "visible_at_adjudication")]
    X = F[feats]
    out = {"n_claims": int(len(F)), "positive_share": float(y.mean())}
    mk = {
        "logistic": lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        "gradient_boosting": lambda: HistGradientBoostingClassifier(max_iter=300, max_depth=4, learning_rate=0.05, random_state=0),
    }
    res = {}
    hidden = (F.scenario_id.isin(["retroactive_termination", "late_discovery_employer", "late_discovery_nghp"]) | (F.scenario_id == "correct_cob")).values
    for name, f in mk.items():
        oof = cv_scores(X, y, groups, f)
        res[name] = {"auc": roc_auc_score(y, oof), "pr_auc": average_precision_score(y, oof),
                     "auc_hidden_errors_vs_correct": roc_auc_score(y[hidden], oof[hidden]),
                     "reweighted_precision_top2pct": reweighted_precision(y, oof)}
        # without the audit-rule feature
        Xn = X.drop(columns=["rule_mismatch"])
        oof2 = cv_scores(Xn, y, groups, f)
        res[name]["auc_without_rule_feature"] = roc_auc_score(y, oof2)
        res[name]["auc_hidden_without_rule_feature"] = roc_auc_score(y[hidden], oof2[hidden])
    out["task_A_day0_triage"] = res
    out["rule_mismatch_only"] = {"auc": roc_auc_score(y, F.rule_mismatch.values),
                                 "recall_visible": float(F.loc[F.visible_at_adjudication, "rule_mismatch"].mean()),
                                 "false_alarm_rate_correct": float(F.loc[F.scenario_id == "correct_cob", "rule_mismatch"].mean())}
    out["recall_by_scenario_rule_mismatch"] = F.groupby("scenario_id").rule_mismatch.mean().round(4).to_dict()

    # Task B/C: demands
    dm, se, mp = t["demand"], t["settlement"], t["mistaken_payment"]
    D = dm.merge(se, on="demand_id").merge(mp[["payment_id", "payer_type", "overpayment"]], on="payment_id").merge(
        t["claim"], on="claim_id").merge(F[["claim_id", "n_known", "injury_related", "max_tenure_yrs"]].rename(columns={"injury_related": "inj"}), on="claim_id")
    D["demand_date"] = pd.to_datetime(D.demand_date); D["service_date"] = pd.to_datetime(D.service_date)
    D["demand_lag"] = (D.demand_date - D.service_date).dt.days
    D["is_medicare"] = (D.recovery_channel == "medicare_recovery").astype(int)
    D["log_principal"] = np.log(D.demand_principal.clip(lower=1))
    D["month"] = D.demand_date.dt.month
    D["rate"] = D.demand_date.map(lambda x: core.rate_at(x.date()))
    for ty in TYPES:
        D[f"dp_{ty}"] = (D.payer_type == ty).astype(int)
    f2 = ["demand_lag", "is_medicare", "log_principal", "month", "rate", "n_known", "max_tenure_yrs"] + [f"dp_{ty}" for ty in TYPES]
    yb = (D.settlement_type == "full").astype(int).values
    ytb = D.settlement_type.values
    oof = cv_scores(D[f2], yb, D.patient_id.values, mk["gradient_boosting"])
    ymed = D.recovery_timeline_days if "recovery_timeline_days" in D else None
    out["task_B_settlement_full_vs_rest"] = {"n": int(len(D)), "auc_gradient_boosting": roc_auc_score(yb, oof),
                                              "majority_class_share": float(pd.Series(ytb).value_counts(normalize=True).max())}
    # Task C timeline
    days = (pd.to_datetime(D.settlement_date) - D.demand_date).dt.days.values
    oofr = np.zeros(len(D))
    for tr, te in GroupKFold(5).split(D[f2], days, D.patient_id.values):
        m = HistGradientBoostingRegressor(max_iter=200, max_depth=3, learning_rate=0.05, random_state=0)
        m.fit(D[f2].iloc[tr], days[tr]); oofr[te] = m.predict(D[f2].iloc[te])
    out["task_C_days_demand_to_settlement"] = {"r2": float(r2_score(days, oofr)), "baseline_r2": 0.0,
                                    "mae_days": float(np.abs(days - oofr).mean()), "mae_mean_baseline": float(np.abs(days - days.mean()).mean())}
    os.makedirs(a.out, exist_ok=True)
    R = pd.DataFrame([{"task": "A", "model": k, **{m: float(v) for m, v in r.items()}} for k, r in res.items()])
    R.to_parquet(os.path.join(a.out, "benchmark_results.parquet"), index=False)
    meta = {"versions": {"pandas": pd.__version__, "numpy": np.__version__, "sklearn": sklearn.__version__},
            "cv": "5-fold GroupKFold by patient_id", "base_rate_real": BASE_RATE_REAL, "results": out}
    with open(os.path.join(a.out, "benchmark_meta.json"), "w") as f:
        json.dump(meta, f, indent=2, default=float)
    print(json.dumps(out, indent=2, default=float))


if __name__ == "__main__":
    main()
