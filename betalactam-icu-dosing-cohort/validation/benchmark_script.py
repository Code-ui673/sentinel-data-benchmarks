"""Benchmark: predict failure to keep the free concentration above the MIC for 100 percent of hours 48-72 under regimen A
(label bolus dosing), from information that is available at the bedside. Logistic regression and XGBoost, five folds split by patient.
The decision point is hour 24, when the first drug level is back. Three feature sets are scored: patient characteristics plus the first
measured drug level (taken on the common starting infusion at its known rate); characteristics plus microbiology; and all three together.
Usage: python benchmark_script.py <folder with the parquet tables> <output parquet>
Random seed: 20261119.  Packages used for the published results: python 3.13, numpy 2.5, pandas 3.0, scikit-learn 1.9, xgboost 3.4, pyarrow 26."""
import sys, numpy as np, pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
import xgboost as xgb
SEED = 20261119
src, dst = sys.argv[1].rstrip("/"), sys.argv[2]
o = pd.read_parquet(f"{src}/patients_observed.parquet"); m = pd.read_parquet(f"{src}/regimen_metrics.parquet")
s = pd.read_parquet(f"{src}/tdm_samples.parquet"); ad = pd.read_parquet(f"{src}/tdm_adjustments.parquet")
s1 = s[s.sample_idx == 1][["patient_id", "conc_measured_mg_L"]].rename(columns={"conc_measured_mg_L": "level_24h_mg_L"})
a = m[m.regimen == "A"][["patient_id", "ft_full_flag"]].merge(o, on="patient_id").merge(s1, on="patient_id").merge(ad[["patient_id", "rate_initial_mg_h"]], on="patient_id")
y = (~a.ft_full_flag).astype(int).values
num = ["age_y", "weight_kg", "height_cm", "bmi_kg_m2", "albumin_g_L", "crcl_cg_est_ml_min_173", "egfr_ckdepi_est_ml_min_173", "crrt_effluent_flow_L_h", "tbsa_pct"]
flags = ["crrt_flag", "ecmo_flag", "burn_flag", "surgery_24h_flag"]
X = a[num].copy(); X["male"] = (a.sex == "M").astype(int)
for f in flags: X[f] = a[f].astype(int)
X["piperacillin"] = (a.drug == "piperacillin").astype(int)
lv = a.level_24h_mg_L; rt = a.rate_initial_mg_h
level = pd.DataFrame({"level_24h_mg_L": lv, "start_rate_mg_h": rt, "level_per_rate": lv / rt, "log_level": np.log(lv), "log_level_per_rate": np.log(lv / rt), "implied_clearance_L_h": rt / lv, "implied_clearance_per_cg_crcl": rt / lv / a.crcl_cg_est_ml_min_173})
micro = a[["mic_mg_L"]].copy()
for sp in sorted(a.pathogen.unique()): micro["sp_" + sp] = (a.pathogen == sp).astype(int)
sets = {"characteristics_plus_first_level": pd.concat([X, level], axis=1),
        "characteristics_plus_microbiology": pd.concat([X, micro], axis=1), "characteristics_plus_first_level_plus_microbiology": pd.concat([X, level, micro], axis=1)}
rows = []
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
for name, F in sets.items():
    for k, (tr, te) in enumerate(skf.split(F, y), 1):
        sc = StandardScaler().fit(F.iloc[tr]); lr = LogisticRegression(max_iter=3000).fit(sc.transform(F.iloc[tr]), y[tr]); p = lr.predict_proba(sc.transform(F.iloc[te]))[:, 1]
        rows.append(dict(feature_set=name, model="logistic_regression", fold=k, n_train=len(tr), n_test=len(te), prevalence_test=float(y[te].mean()), auroc=roc_auc_score(y[te], p), auprc=average_precision_score(y[te], p), brier=brier_score_loss(y[te], p)))
        gb = xgb.XGBClassifier(n_estimators=600, max_depth=3, learning_rate=0.03, subsample=0.8, colsample_bytree=0.8, eval_metric="auc", random_state=SEED, n_jobs=2).fit(F.iloc[tr], y[tr]); p = gb.predict_proba(F.iloc[te])[:, 1]
        rows.append(dict(feature_set=name, model="xgboost", fold=k, n_train=len(tr), n_test=len(te), prevalence_test=float(y[te].mean()), auroc=roc_auc_score(y[te], p), auprc=average_precision_score(y[te], p), brier=brier_score_loss(y[te], p)))
R = pd.DataFrame(rows); R.to_parquet(dst, index=False, compression="zstd")
print(R.groupby(["feature_set", "model"])[["auroc", "auprc", "brier"]].agg(["mean", "std", "min"]).round(4).to_string())
