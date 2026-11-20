#!/usr/bin/env python3
"""
CAPR synthetic dataset — benchmark script
==========================================
Sentinel Data, 2026.

Purpose
-------
Reproducible machine-learning benchmark on the delivered CAPR dataset.
Four tasks, logistic regression only, 5-fold stratified cross-validation,
fixed seed. Raw per-fold metrics are written to benchmark_results.parquet.

Tasks
-----
A1 (primary):  multiclass prediction of Medicare functional classification
               level at 24 months post injury (klevel_24mo, K1-K4) from
               contemporaneous functional measures (6MWT, TUG, PROMIS PF).
               Mirrors the published functional-assessment design of
               Dillon et al. 2018 (Prosthet Orthot Int 42(2):191-197).
A2:            binary K2 vs K3 discrimination at 24 months from the same
               functional measures; directly comparable to the published
               >80% accuracy figure of Dillon et al. 2018.
B:             return-to-duty (rtd_flag) from intake features
               (demographics + injury anatomy), full cohort.
C:             chronic pain risk (pain_chronicity_risk_flag) from intake
               features + 1-month pain scores, full cohort.

Leakage control: task B/C features are restricted to variables knowable
within 1 month of injury; no rehabilitation, treatment, milestone, or
outcome columns are used. Tasks A1/A2 use only contemporaneous functional
measures, mirroring the published functional-assessment design.

Model: logistic regression (scikit-learn), standardized numeric features,
one-hot encoded categoricals. No class weighting.

Reproducibility
---------------
Fixed seed: 20261006
Package versions used to produce the delivered benchmark_results.parquet:
  python       3.11.13
  numpy        2.1.0
  pandas       2.3.1
  scikit-learn 1.7.1
  pyarrow      21.0.0

Usage
-----
  cd VALIDATION
  python benchmark_script.py            # reads ../DATASET/, writes benchmark_results.parquet
"""

import sys
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score,
                             balanced_accuracy_score, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEED = 20261006
DATASET_DIR = "../DATASET"
OUT_PATH = "benchmark_results.parquet"

INTAKE_NUM = ["age_at_injury_years"]
INTAKE_CAT = ["sex", "ll_group"]
INTAKE_BOOL = ["officer_flag", "mechanism_blast_flag", "any_upper",
               "bilateral_lower_flag", "multiple_amputations_flag"]
FUNC_24MO = ["sixmwt_m_24mo", "tug_s_24mo", "promis_pf_t_24mo"]


def load_features():
    pw = pd.read_parquet(f"{DATASET_DIR}/capr_wide_patients.parquet")
    pr = pd.read_parquet(f"{DATASET_DIR}/capr_longitudinal_rehab.parquet")
    p1 = (pr[pr["months_post_injury"] == 1]
          [["patient_id", "plp_flag", "plp_nrs_0_10", "rlp_flag", "rlp_nrs_0_10"]]
          .rename(columns={"plp_flag": "plp_flag_1mo", "plp_nrs_0_10": "plp_nrs_1mo",
                           "rlp_flag": "rlp_flag_1mo", "rlp_nrs_0_10": "rlp_nrs_1mo"}))
    df = pw.merge(p1, on="patient_id", how="left")
    for c in INTAKE_BOOL + ["plp_flag_1mo", "rlp_flag_1mo"]:
        df[c] = df[c].fillna(False).astype(int)
    for c in ["plp_nrs_1mo", "rlp_nrs_1mo"]:
        # NRS is NaN when that pain type is absent -> impute 0 (no pain)
        df[c] = df[c].astype(float).fillna(0.0)
    return df


def make_pipeline(num, cat, boo, binary):
    pre = ColumnTransformer([
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
        ("bool", "passthrough", boo),
    ])
    clf = LogisticRegression(max_iter=2000, random_state=SEED)
    return Pipeline([("pre", pre), ("clf", clf)])


def run_task(name, df, y, num, cat, boo, binary):
    rows = []
    X = df[num + cat + boo]
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    for i, (tr, te) in enumerate(skf.split(X, y), start=1):
        pipe = make_pipeline(num, cat, boo, binary)
        pipe.fit(X.iloc[tr], y.iloc[tr])
        pred = pipe.predict(X.iloc[te])
        row = {"task": name, "fold": i, "n_train": int(len(tr)),
               "n_test": int(len(te)),
               "accuracy": accuracy_score(y.iloc[te], pred),
               "balanced_accuracy": balanced_accuracy_score(y.iloc[te], pred)}
        if binary:
            proba = pipe.predict_proba(X.iloc[te])[:, 1]
            row.update({
                "prevalence_test": float(y.iloc[te].mean()),
                "roc_auc": roc_auc_score(y.iloc[te], proba),
                "average_precision": average_precision_score(y.iloc[te], proba),
                "sensitivity": recall_score(y.iloc[te], pred),
                "specificity": recall_score(y.iloc[te], pred, pos_label=0),
                "precision": precision_score(y.iloc[te], pred),
                "f1": f1_score(y.iloc[te], pred)})
        else:
            row.update({
                "f1_macro": f1_score(y.iloc[te], pred, average="macro")})
            labels = sorted(y.unique())
            for cls, rec in zip(labels, recall_score(y.iloc[te], pred,
                                                     average=None,
                                                     labels=labels)):
                row[f"recall_{cls}"] = rec
        rows.append(row)
        extra = f"auc={row['roc_auc']:.3f}" if binary else f"f1_macro={row['f1_macro']:.3f}"
        print(f"  {name} fold {i}: acc={row['accuracy']:.3f} {extra} "
              f"bal_acc={row['balanced_accuracy']:.3f}")
    return rows


def main():
    print(f"CAPR benchmark · seed {SEED}")
    print(f"versions: python {sys.version.split()[0]}, numpy {np.__version__}, "
          f"pandas {pd.__version__}, sklearn {__import__('sklearn').__version__}, "
          f"pyarrow {__import__('pyarrow').__version__}")
    df = load_features()
    rows = []

    # Task A1: 4-class K-level at 24 months from functional measures
    da = df[df["klevel_24mo"].isin(["K1", "K2", "K3", "K4"])].dropna(subset=FUNC_24MO).copy()
    ya = da["klevel_24mo"]
    print(f"Task A1: n={len(da)}, classes={ya.value_counts().to_dict()}")
    rows += run_task("A1_klevel_4class_functional", da, ya, FUNC_24MO, [], [], binary=False)

    # Task A2: K2 vs K3 at 24 months from functional measures
    da2 = da[da["klevel_24mo"].isin(["K2", "K3"])].copy()
    ya2 = (da2["klevel_24mo"] == "K3").astype(int)
    print(f"Task A2: n={len(da2)}, K3 share={ya2.mean():.3f}")
    rows += run_task("A2_klevel_K2vsK3_functional", da2, ya2, FUNC_24MO, [], [], binary=True)

    # Task B: return to duty from intake features
    yb = df["rtd_flag"].astype(int)
    print(f"Task B: n={len(df)}, prevalence={yb.mean():.4f}")
    rows += run_task("B_return_to_duty_intake", df, yb,
                     INTAKE_NUM, INTAKE_CAT, INTAKE_BOOL, binary=True)

    # Task C: chronic pain risk from intake + 1-month pain
    yc = df["pain_chronicity_risk_flag"].astype(int)
    print(f"Task C: n={len(df)}, prevalence={yc.mean():.4f}")
    rows += run_task("C_pain_chronicity_early", df, yc,
                     INTAKE_NUM + ["plp_nrs_1mo", "rlp_nrs_1mo"],
                     INTAKE_CAT, INTAKE_BOOL + ["plp_flag_1mo", "rlp_flag_1mo"],
                     binary=True)

    res = pd.DataFrame(rows)
    res["seed"] = SEED
    res.to_parquet(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH} ({len(res)} rows)")
    print(res.groupby("task")[["accuracy", "balanced_accuracy"]].mean().round(4))


if __name__ == "__main__":
    main()
