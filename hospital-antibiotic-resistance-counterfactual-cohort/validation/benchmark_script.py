#!/usr/bin/env python3
"""Benchmark of the ward antibiotic-resistance cohort, control world W0 of one scenario.
Training uses observed/ only; truth/ is read for the two upper-bound rows and the descriptive rows.
usage: python benchmark_script.py DATASET_DIR OUT_PARQUET [scenario_id]
Seed 20261110. python 3.11+, pandas, pyarrow, scikit-learn, xgboost, numpy."""
import sys, numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from xgboost import XGBClassifier

SEED = 20261110
root = sys.argv[1]; outp = sys.argv[2]; sid = sys.argv[3] if len(sys.argv) > 3 else "S12"
rd = lambda p: pd.read_parquet(f"{root}/{p}/scenario_id={sid}/part-0.parquet")
k = ["scenario_id", "world_id", "subject_id"]
adm, oc, cu, ev = rd("observed/admissions"), rd("observed/outcomes"), rd("observed/cultures"), rd("truth/events_truth")
st = pd.read_parquet(f"{root}/truth/subject_truth/subject_truth.parquet")
adm, oc, cu, ev = [d[d.world_id == "W0"] for d in (adm, oc, cu, ev)]
df = adm.merge(oc, on=k).merge(ev, on=k).merge(st[["subject_id", "acq_multiplier_true"]], on="subject_id")
cu = cu.assign(pos=cu.resistant_phenotype.astype(int))
# cultures resulted by day 9 (the day-7 culture of the standard arm is reported on day 8.8)
early = cu[cu.result_available_day <= 9.0].pivot(index="subject_id", columns="culture_day", values="pos")
early.columns = [f"cult_d{int(c)}" for c in early.columns]
early["cult_n_pos"] = early.sum(axis=1)
d14 = cu[cu.culture_day == 14][["subject_id", "pos"]].rename(columns={"pos": "res_day14"})
d28 = cu[cu.culture_day == 28][["subject_id", "pos"]].rename(columns={"pos": "res_day28"})
df = df.merge(early.reset_index(), on="subject_id").merge(d14, on="subject_id").merge(d28, on="subject_id")
df["sex_f"] = (df.sex == "F").astype(int)
for c in ("decolonisation_given", "vaccine_given", "prior_antibiotic_90d", "invasive_device", "transfer_from_other_unit", "surgery_past_year"):
    df[c] = df[c].astype(int)
df["screen_pos"] = df.cult_d0.astype(int)
base = ["age", "sex_f", "serum_creatinine", "crcl_estimated", "dose_tier", "course_days_planned"]
risk = ["prior_antibiotic_90d", "invasive_device", "transfer_from_other_unit", "surgery_past_year"]
FA = base + risk
FD = FA + [c for c in df.columns if c.startswith("cult_")]
neg = df.screen_pos == 0
groups = df.subject_id.values
rows = []


def models():
    return {"logistic_regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=SEED)),
            "xgboost": XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.05, subsample=0.8, random_state=SEED, n_jobs=2, eval_metric="logloss")}


def run(task, label, fs_name, fs, y, mask=None):
    d = df if mask is None else df[mask]
    yy = y[d.index] if mask is not None else y
    X = d[fs].values.astype(float); g = d.subject_id.values
    for mname in ("logistic_regression", "xgboost"):
        oof = np.zeros(len(yy))
        for fold, (tr, te) in enumerate(GroupKFold(n_splits=5).split(X, yy, g)):
            m = models()[mname]; m.fit(X[tr], yy[tr]); p = m.predict_proba(X[te])[:, 1]; oof[te] = p
            for mn, v in (("auc", roc_auc_score(yy[te], p)), ("average_precision", average_precision_score(yy[te], p)),
                          ("brier", brier_score_loss(yy[te], p)), ("prevalence", yy[te].mean())):
                rows.append((task, label, fs_name, mname, fold, mn, float(v)))
        rng = np.random.default_rng(SEED); a = []
        for _ in range(300):
            i = rng.integers(0, len(yy), len(yy))
            if yy[i].min() != yy[i].max(): a.append(roc_auc_score(yy[i], oof[i]))
        rows.append((task, label, fs_name, mname, -1, "auc_pooled", float(roc_auc_score(yy, oof))))
        rows.append((task, label, fs_name, mname, -1, "auc_ci_low", float(np.percentile(a, 2.5))))
        rows.append((task, label, fs_name, mname, -1, "auc_ci_high", float(np.percentile(a, 97.5))))
        rows.append((task, label, fs_name, mname, -1, "n", float(len(yy))))


y_new = df.carrier_day14.astype(int).values
y_d14 = df.res_day14.values.astype(int)
y_mort = df.died_day90.astype(int).values
run("T1_new_resistant_culture_by_day14", "carrier_day14", "admission_data_only", FA, y_new)
run("T2_new_resistant_culture_by_day14_screen_negative", "carrier_day14", "admission_data_only", FA, y_new, neg)
run("T3_resistant_culture_on_day14_whole_cohort", "res_day14", "admission_data_plus_cultures_resulted_by_day9", FD, y_d14)
run("T4_resistant_culture_on_day14_screen_negative", "res_day14", "admission_data_plus_cultures_resulted_by_day9", FD, y_d14, neg)
run("T5_death_by_day90", "died_day90", "admission_data_plus_cultures_resulted_by_day9", FD, y_mort)
# landmark series: same task as T3 with the forecast made earlier or later. Added after the first run of edition 1.1
# (the preregistered task is the day-9 one, T3); reported in full, none of them selected.
for L in (2, 4, 12):
    e = cu[cu.result_available_day <= float(L)].pivot(index="subject_id", columns="culture_day", values="pos")
    e.columns = [f"lm{L}_d{int(c)}" for c in e.columns]
    cols = list(e.columns); e = e.reset_index()
    df = df.drop(columns=[c for c in df.columns if c.startswith(f"lm{L}_")]).merge(e, on="subject_id", how="left")
    df[cols] = df[cols].fillna(0)
    run(f"T3_landmark_day{L:02d}_resistant_culture_on_day14", "res_day14", f"admission_data_plus_cultures_resulted_by_day{L}", FA + cols, y_d14)
    run(f"T4_landmark_day{L:02d}_screen_negative", "res_day14", f"admission_data_plus_cultures_resulted_by_day{L}", FA + cols, y_d14, neg)
# upper bounds with truth (demonstration only, not a task a buyer can solve)
at = ~df.colonised_admission_true
yt = (df.acquisition_day <= 14).fillna(False).astype(int).values
auc_mult = roc_auc_score(yt[at.values], df.acq_multiplier_true.values[at.values])
rows.append(("U1_truth_upper_bound", "acquisition_day<=14 among truly not colonised", "true hazard multiplier", "none", -1, "auc", float(auc_mult)))
auc_adm = roc_auc_score(yt[at.values], LogisticRegression(max_iter=2000).fit(StandardScaler().fit_transform(df.loc[at, FA].values.astype(float)), yt[at.values]).predict_proba(StandardScaler().fit_transform(df.loc[at, FA].values.astype(float)))[:, 1])
rows.append(("U1_truth_upper_bound", "acquisition_day<=14 among truly not colonised", "admission data only, in-sample, truth label", "logistic_regression", -1, "auc", float(auc_adm)))
# persistence among true carriers (observed share of resistant day-28 cultures)
car = df.colonised_admission_true
rows.append(("D1_persistence", "descriptive", "share of day-28 cultures resistant among patients colonised at admission", "-", -1, "share", float(df.loc[car, "res_day28"].mean())))
rows.append(("D1_persistence", "descriptive", "share of day-14 cultures resistant among patients colonised at admission", "-", -1, "share", float(df.loc[car, "res_day14"].mean())))
# task of the culture schedule gap, as in edition 1.0
a14 = df[(~df.colonised_admission_true) & (df.acquisition_day <= 14)]
delay = (a14.first_detection_day - a14.acquisition_day).dropna()
for mn, v in (("n_acquired_by_day14", len(a14)), ("share_not_seen_by_day14_cultures", float((~a14.carrier_day14).mean())),
              ("share_not_known_to_clinician_by_day14", float((~a14.carrier_known_day14).mean())),
              ("median_detection_delay_days", float(delay.median())), ("mean_detection_delay_days", float(delay.mean()))):
    rows.append(("D2_schedule_gap", "descriptive", "-", "-", -1, mn, float(v)))
r = pd.DataFrame(rows, columns=["task", "label", "feature_set", "model", "fold", "metric", "value"])
r.to_parquet(outp, index=False)
print(r[(r.fold == -1)].pivot_table(index=["task", "feature_set", "model"], columns="metric", values="value", aggfunc="first").to_string())
