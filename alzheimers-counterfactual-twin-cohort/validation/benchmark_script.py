#!/usr/bin/env python3
"""
benchmark_script.py - two benchmark tasks on the ALZ-PATHWAY-TWIN dataset.

  task 1  five-year dementia forecast from the entry visit (natural course, scenario S00)
  task 2  individual treatment effect of early therapy (randomised split between S00 and S15), T-learner

usage: python3 benchmark_script.py --data DATA_DIR --out benchmark_results.parquet
"""
import argparse, os, sys, glob
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import xgboost as xgb

SEED = 20261108


def read_scenario(data, table, sid, columns=None):
    p = os.path.join(data, table, "scenario_id=" + sid)
    return pd.read_parquet(p, columns=columns)


def features(data):
    co = pd.read_parquet(os.path.join(data, "cohort.parquet"))
    v0 = read_scenario(data, "visits", "S00")
    v0 = v0[v0.visit_year == 0][["subject_id", "mmse", "cdr_sb", "ptau217_pgml"]]
    f = co.merge(v0, on="subject_id")
    f["female"] = (f.sex == "female").astype(np.int8)
    f["log_ptau217"] = np.log(f.ptau217_pgml.astype(np.float64))
    return f


def calib_rows(task, model, y, p, bins=10):
    q = pd.qcut(p, bins, duplicates="drop")
    g = pd.DataFrame(dict(y=y, p=p, q=q)).groupby("q", observed=True).agg(pred=("p", "mean"), obs=("y", "mean"), n=("y", "size")).reset_index(drop=True)
    return [dict(task=task, model=model, metric="calibration_bin_%02d" % i, value=float(r.obs), extra="mean predicted %.4f, n %d" % (r.pred, r.n)) for i, r in g.iterrows()]


def make_models():
    return {
        "logistic_regression": lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        "xgboost": lambda: xgb.XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                                              random_state=SEED, n_jobs=2, eval_metric="logloss", verbosity=0),
    }


def task1(data):
    f = features(data)
    out = pd.read_parquet(os.path.join(data, "outcomes.parquet"))
    out = out[out.scenario_id == "S00"][["subject_id", "dementia_event", "age_dementia", "death_event", "age_death_or_censor"]]
    d = f.merge(out, on="subject_id")
    d["t_dem"] = d.age_dementia - d.age_baseline
    d["t_end"] = d.age_death_or_censor - d.age_baseline
    d = d[d.cdr_sb < 4.5]                                           # people without dementia at entry
    pos = d.dementia_event & (d.t_dem <= 5.0)
    neg = ~pos & (d.t_end >= 5.0 - 1e-6)                            # observed for five years without dementia
    keep = pos | neg                                                # dementia-free people who died or ended before year 5 are dropped
    d = d[keep.values]; y = pos[keep.values].astype(int).to_numpy()
    cols = ["age_baseline", "female", "apoe_e4_alleles", "mmse", "cdr_sb", "log_ptau217"]
    X = d[cols].to_numpy(dtype=np.float64)
    rows = [dict(task="task1", model="all", metric="n_people", value=float(len(y)), extra="events %d" % y.sum()),
            dict(task="task1", model="all", metric="event_rate_5y", value=float(y.mean()), extra="")]
    skf = StratifiedKFold(5, shuffle=True, random_state=SEED)
    sets = {"all_features": list(range(len(cols))), "ptau217_only": [cols.index("log_ptau217")],
            "ptau217_mmse_e4": [cols.index(c) for c in ("log_ptau217", "mmse", "apoe_e4_alleles")]}
    for sname, ci in sets.items():
        for mname, mk in make_models().items():
            if sname != "all_features" and mname == "xgboost":
                continue
            pred = np.zeros(len(y))
            for tr, te in skf.split(X, y):
                m = mk(); m.fit(X[tr][:, ci], y[tr]); pred[te] = m.predict_proba(X[te][:, ci])[:, 1]
            tag = "%s [%s]" % (mname, sname)
            rows.append(dict(task="task1", model=tag, metric="roc_auc", value=float(roc_auc_score(y, pred)), extra="5-fold stratified, seed %d" % SEED))
            rows.append(dict(task="task1", model=tag, metric="brier", value=float(brier_score_loss(y, pred)), extra=""))
            if sname == "all_features":
                rows += calib_rows("task1", tag, y, pred)
    return rows


def task2(data):
    f = features(data)
    o0 = read_scenario(data, "truth/truth_quarterly", "S00", ["subject_id", "quarter", "cdr_sb_true"])
    o1 = read_scenario(data, "truth/truth_quarterly", "S15", ["subject_id", "quarter", "cdr_sb_true"])
    q = 40                                                          # ten years from entry
    a = o0[o0.quarter == q][["subject_id", "cdr_sb_true"]].rename(columns={"cdr_sb_true": "t0"})
    b = o1[o1.quarter == q][["subject_id", "cdr_sb_true"]].rename(columns={"cdr_sb_true": "t1"})
    v0 = read_scenario(data, "visits", "S00", ["subject_id", "visit_year", "cdr_sb"]); v0 = v0[v0.visit_year == 10][["subject_id", "cdr_sb"]].rename(columns={"cdr_sb": "y0"})
    v1 = read_scenario(data, "visits", "S15", ["subject_id", "visit_year", "cdr_sb"]); v1 = v1[v1.visit_year == 10][["subject_id", "cdr_sb"]].rename(columns={"cdr_sb": "y1"})
    d = f.merge(a, on="subject_id").merge(b, on="subject_id").merge(v0, on="subject_id").merge(v1, on="subject_id")    # alive at year 10 in both worlds
    d["tau"] = d.t1 - d.t0
    rng = np.random.default_rng(SEED)
    d["treated"] = rng.random(len(d)) < 0.5
    d["y"] = np.where(d.treated, d.y1, d.y0)                        # what the randomised trial would observe
    cols = ["age_baseline", "female", "apoe_e4_alleles", "mmse", "cdr_sb", "log_ptau217"]
    X = d[cols].to_numpy(dtype=np.float64); y = d.y.to_numpy(dtype=np.float64); tr_ = d.treated.to_numpy(); tau = d.tau.to_numpy()
    rows = [dict(task="task2", model="all", metric="n_people", value=float(len(d)), extra="alive at year 10 in both worlds; %d treated, %d control" % (tr_.sum(), (~tr_).sum())),
            dict(task="task2", model="truth", metric="true_mean_effect", value=float(tau.mean()), extra="mean of S15 - S00 true CDR-SB at year 10"),
            dict(task="task2", model="truth", metric="true_effect_sd", value=float(tau.std()), extra="spread of individual effects"),
            dict(task="task2", model="reference", metric="pehe_constant_effect", value=float(tau.std()), extra="error of a model that predicts the true mean effect for everyone"),
            dict(task="task2", model="reference", metric="pehe_zero_effect", value=float(np.sqrt((tau ** 2).mean())), extra="error of a model that predicts no effect")]
    mk = {"ridge_regression": lambda: make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
          "xgboost": lambda: xgb.XGBRegressor(n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.8, random_state=SEED, n_jobs=2, verbosity=0)}
    kf = KFold(5, shuffle=True, random_state=SEED)
    for mname, m in mk.items():
        cate = np.zeros(len(y))
        for tr, te in kf.split(X):
            m1 = m(); m0 = m()
            t = tr[tr_[tr]]; c = tr[~tr_[tr]]
            m1.fit(X[t], y[t]); m0.fit(X[c], y[c])
            cate[te] = m1.predict(X[te]) - m0.predict(X[te])
        rows.append(dict(task="task2", model="T-learner " + mname, metric="ate_bias", value=float(cate.mean() - tau.mean()), extra="estimated mean effect %.4f" % cate.mean()))
        rows.append(dict(task="task2", model="T-learner " + mname, metric="pehe", value=float(np.sqrt(((cate - tau) ** 2).mean())), extra="5-fold cross-fitted"))
        rows.append(dict(task="task2", model="T-learner " + mname, metric="effect_rank_correlation", value=float(pd.Series(cate).corr(pd.Series(tau), method="spearman")), extra=""))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default="benchmark_results.parquet")
    a = ap.parse_args()
    rows = task1(a.data) + task2(a.data)
    df = pd.DataFrame(rows)
    df["value"] = df["value"].astype(np.float64)
    df.to_parquet(a.out, compression="zstd", index=False)
    print(df[~df.metric.str.startswith("calibration")].to_string())


if __name__ == "__main__":
    main()
