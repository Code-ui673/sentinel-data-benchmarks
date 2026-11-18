#!/usr/bin/env python3
"""Benchmark for the HGPS counterfactual dataset (progerin biomarkers, vascular stiffness, treatment worlds).

usage: python benchmark_script.py <DATASET folder> <results.parquet>

Needs pandas, numpy, scikit-learn, pyarrow. Features come from observed/ only; labels and counterfactual references
come from truth/. Preregistration SHA-256: 4409ec9d487c52decb7459d8006211bd19250130edde39a72f8a5dc5a4e8347a
"""
import sys
import pathlib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ds = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
rd = lambda p: pd.read_parquet(ds / p)
pat, outc, vis, bio = rd("observed/patients.parquet"), rd("observed/outcomes.parquet"), rd("observed/visits.parquet"), rd("observed/skin_biopsies.parquet")
tpat, two, lat = rd("truth/patients.parquet"), rd("truth/world_outcomes.parquet"), rd("truth/latent_states.parquet")
rows = []
HOR = 360.0


def boot_ci(x, f, n=300, seed=1):
    g = np.random.default_rng(seed)
    v = [f(x[g.integers(0, len(x), len(x))]) for _ in range(n)]
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def auc_ci(y, s, n=300, seed=1):
    g = np.random.default_rng(seed)
    y, s = np.asarray(y), np.asarray(s)
    v = []
    for _ in range(n):
        i = g.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(i):
            v.append(roc_auc_score(y[i], s[i]))
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


# ---------------------------------------------------------------- A. treatment effect: observed estimate against counterfactual truth
d = pat.merge(outc, on="patient_id")
d["arm"] = np.where(d.treatment == "none", "W0", np.where((d.treatment == "lonafarnib") & (d.treatment_start_months == d.index_age_months), "W1", "other"))
d = d[(d.arm != "other") & (d.follow_up_months > d.index_age_months)]
W = 60.0


def rmst(g):
    t = np.minimum(g.follow_up_months - g.index_age_months, W)
    return t.mean()


obs_w0, obs_w1 = rmst(d[d.arm == "W0"]), rmst(d[d.arm == "W1"])
tw = two.pivot(index="patient_id", columns="world", values="death_month").fillna(HOR)
ids = d.patient_id.values
idx_age = d.set_index("patient_id").index_age_months if "index_age_months" in d else None
ia = pat.set_index("patient_id").index_age_months
t0 = np.minimum(tw.loc[ids, "W0"].values - ia.loc[ids].values, W)
t1 = np.minimum(tw.loc[ids, "W1"].values - ia.loc[ids].values, W)
alive = (tw.loc[ids, "W0"].values > ia.loc[ids].values) & (tw.loc[ids, "W1"].values > ia.loc[ids].values)
rows.append({"kind": "summary", "label": "restricted mean survival in months, 60 months from the index age, treated minus untreated: observed arms", "value": obs_w1 - obs_w0,
             "n": len(d)})
rows.append({"kind": "summary", "label": "same quantity from the counterfactual truth (every child in both worlds)", "value": float((t1 - t0)[alive].mean()),
             "n": int(alive.sum())})

# ---------------------------------------------------------------- B. biomarker against vascular reading six months after the index age
fu = bio[bio.kind == "followup"].merge(pat[["patient_id", "treatment", "treatment_start_months", "index_age_months"]], on="patient_id")
fu = fu[fu.treatment.isin(["none", "lonafarnib", "lonafarnib+everolimus"])]
fu["lonafarnib_at_index"] = (fu.treatment != "none").astype(int)
s_prog = -fu.progerin_fmol_per_100ug.values
a_prog = roc_auc_score(fu.lonafarnib_at_index, s_prog)
lo, hi = auc_ci(fu.lonafarnib_at_index.values, s_prog)
rows.append({"kind": "summary", "label": "farnesylated progerin, skin biopsy 6 months after the index age: AUC for lonafarnib at the index age", "value": a_prog,
             "lo": lo, "hi": hi, "n": len(fu)})
v = vis.dropna(subset=["cfpwv_ms"]).merge(pat[["patient_id", "treatment", "index_age_months"]], on="patient_id")
v = v[v.treatment.isin(["none", "lonafarnib", "lonafarnib+everolimus"])]
v["gap"] = (v.age_months - (v.index_age_months + 6)).abs()
v = v[v.gap <= 6].sort_values("gap").groupby("patient_id").head(1)
v["lonafarnib_at_index"] = (v.treatment != "none").astype(int)
a_pwv = roc_auc_score(v.lonafarnib_at_index, -v.cfpwv_ms)
lo, hi = auc_ci(v.lonafarnib_at_index.values, -v.cfpwv_ms.values)
rows.append({"kind": "summary", "label": "carotid-femoral PWV at the visit nearest to 6 months after the index age: AUC for lonafarnib at the index age", "value": a_pwv,
             "lo": lo, "hi": hi, "n": len(v)})

# ---------------------------------------------------------------- C. death within 24 months from a visit with a PWV reading
x = vis.dropna(subset=["cfpwv_ms"]).merge(outc[["patient_id", "died", "death_month"]], on="patient_id")
x["y"] = ((x.died == 1) & (x.death_month <= x.age_months + 24)).astype(int)
x = x.merge(tpat[["patient_id", "arm"]], on="patient_id")
L = lat.rename(columns={"world": "arm"})[["patient_id", "arm", "age_months", "damage_index"]]
x = x.merge(L, on=["patient_id", "arm", "age_months"], how="left")
x["fold_group"] = x.patient_id.str[2:].astype(int) % 5
y = x.y.values
sets = {"age only": ["age_months"], "age + carotid-femoral PWV": ["age_months", "cfpwv_ms"],
        "age + PWV + weight + treatment flag": ["age_months", "cfpwv_ms", "weight_kg", "on_lonafarnib"],
        "truth predictor: damage index (upper reference)": ["age_months", "damage_index"]}
for name, cols in sets.items():
    X = x[cols].astype(float).values
    pred = np.zeros(len(x))
    for f in range(5):
        tr, te = x.fold_group.values != f, x.fold_group.values == f
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
        m.fit(X[tr], y[tr])
        pred[te] = m.predict_proba(X[te])[:, 1]
    lo, hi = auc_ci(y, pred, n=200)
    rows.append({"kind": "summary", "label": "death within 24 months, " + name, "value": roc_auc_score(y, pred), "lo": lo, "hi": hi, "n": len(x)})
res = pd.DataFrame(rows)
res.to_parquet(out, index=False)
res.to_csv(str(out).replace(".parquet", "_readable.csv"), index=False)
print(res.to_string())
