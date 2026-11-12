# =============================================================================
# bTBI Dataset — Baseline Benchmark v1.1
# Task: predict incomplete recovery (GOSE < 8) at 12 months from acute-phase
#       features available at presentation/discharge.
# Model: logistic regression (baseline standard; nothing more).
# Protocol: stratified 80/20 train/test split + 5-fold CV on the train split.
# Metrics: ROC AUC, F1 (threshold 0.5), Brier score, calibration slope/intercept.
# Reproducibility: SEED = 20260926 (numpy / sklearn).
# Pinned versions: Python 3.11 | numpy 2.1.0 | pandas 2.3.1 | pyarrow 21.0.0
#                  | scikit-learn 1.7.1
# Usage:  python benchmark_script.py [path_to_btbi_wide.parquet]
# Output: benchmark_results.parquet (raw metrics, no manual rounding)
# =============================================================================
import os
import sys
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEED = 20260926

# ---- locate dataset ----------------------------------------------------------
if len(sys.argv) > 1:
    DATA = sys.argv[1]
else:
    for cand in ["../DATASET/btbi_wide.parquet", "btbi_wide.parquet",
                 os.path.join(os.path.dirname(__file__), "..", "DATASET",
                              "btbi_wide.parquet")]:
        if os.path.exists(cand):
            DATA = cand
            break
    else:
        raise FileNotFoundError("btbi_wide.parquet not found; pass path as argv[1]")

df = pd.read_parquet(DATA)
print(f"dataset: {DATA}  shape={df.shape}")

# ---- task label ---------------------------------------------------------------
y = (df["gose_12mo"] < 8).astype(int).to_numpy()   # 1 = incomplete recovery at 12 mo
print(f"label prevalence (GOSE<8 at 12 mo): {y.mean():.4f}")

# ---- acute-phase features (available at presentation / discharge) -------------
NUM = ["age_years", "education_years", "gcs_admission", "loc_duration_minutes", "aoc_duration_hours",
       "pta_duration_hours", "midline_shift_mm", "ct_rotterdam_score",
       "mace2_total_0h", "voms_npc_cm", "prior_blast_exposures",
       "lifetime_mtbi_count"]
BIN = ["loc_present", "aoc_present", "pta_present", "ct_abnormal",
       "midline_shift_gt5mm", "mace2_abnormal_0h", "voms_symptom_provocation",
       "voms_npc_abnormal", "voms_vor_positive", "race_minority_flag",
       "hispanic_flag", "psychiatric_history_flag"]
CAT = ["sex", "rank_group", "blast_mechanism", "distance_class", "helmet_type",
       "tbi_severity", "ct_marshall_grade", "ich_subtype"]

X = df[NUM + BIN + CAT].copy()
for c in BIN:
    X[c] = X[c].astype(int)
for c in ["loc_duration_minutes", "aoc_duration_hours", "pta_duration_hours",
          "prior_blast_exposures"]:
    X[c] = np.log1p(X[c].astype(float))

pre = ColumnTransformer([
    ("num", StandardScaler(), NUM),
    ("bin", "passthrough", BIN),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT),
])
model = Pipeline([
    ("pre", pre),
    ("clf", LogisticRegression(max_iter=2000, C=1.0, solver="lbfgs",
                               random_state=SEED)),
])

def calibration_slope_intercept(y_true, p):
    """Logistic recalibration: logit(y) ~ a + b * logit(p)."""
    lp = np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))
    Xd = np.column_stack([np.ones_like(lp), lp])
    coef, *_ = np.linalg.lstsq(Xd, y_true.astype(float), rcond=None)
    # refine with one Newton step via sklearn for stability
    lr = LogisticRegression(C=1e12, max_iter=1000)
    lr.fit(lp.reshape(-1, 1), y_true)
    return float(lr.coef_[0][0]), float(lr.intercept_[0])

def evaluate(y_true, p):
    slope, intercept = calibration_slope_intercept(y_true, p)
    pred = (p >= 0.5).astype(int)
    return {"auc": roc_auc_score(y_true, p),
            "f1": f1_score(y_true, pred),
            "brier": brier_score_loss(y_true, p),
            "calibration_slope": slope,
            "calibration_intercept": intercept}

# ---- split --------------------------------------------------------------------
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.20, random_state=SEED,
                                          stratify=y)
rows = []

# 5-fold CV on train split
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
for k, (itr, iva) in enumerate(skf.split(X_tr, y_tr), 1):
    model.fit(X_tr.iloc[itr], y_tr[itr])
    p = model.predict_proba(X_tr.iloc[iva])[:, 1]
    m = evaluate(y_tr[iva], p)
    rows.append({"split": f"cv_fold_{k}", "n_train": int(len(itr)),
                 "n_eval": int(len(iva)), "prevalence": float(y_tr[iva].mean()), **m})
    print(f"fold {k}: AUC={m['auc']:.4f} F1={m['f1']:.4f} brier={m['brier']:.4f}")

# final model on full train split, evaluated on held-out test
model.fit(X_tr, y_tr)
p_tr = model.predict_proba(X_tr)[:, 1]
p_te = model.predict_proba(X_te)[:, 1]
m_tr = evaluate(y_tr, p_tr)
m_te = evaluate(y_te, p_te)
rows.append({"split": "train_full", "n_train": int(len(y_tr)), "n_eval": int(len(y_tr)),
             "prevalence": float(y_tr.mean()), **m_tr})
rows.append({"split": "test", "n_train": int(len(y_tr)), "n_eval": int(len(y_te)),
             "prevalence": float(y_te.mean()), **m_te})
print(f"train: AUC={m_tr['auc']:.4f} | test: AUC={m_te['auc']:.4f} "
      f"F1={m_te['f1']:.4f} brier={m_te['brier']:.4f} "
      f"cal_slope={m_te['calibration_slope']:.4f}")

res = pd.DataFrame(rows)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "benchmark_results.parquet")
res.to_parquet(out, index=False)
print("saved ->", out, res.shape)
