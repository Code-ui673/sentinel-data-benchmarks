#!/usr/bin/env python3
"""
Post-landing orthostatic intolerance dataset -- VALIDATION/benchmark_script.py
Code Sentinel Data. Real run, not pseudocode. Packages pinned: see
requirements.txt (python 3.11.x, pandas 2.x, scikit-learn 1.9.x, pyarrow
18.x). seed=20261027, same project seed as the generator and kernel.

Task: predict outcomes.presyncope (factual scenario) from OBSERVATIONS-only
features plus crew covariates -- NEVER from truth (that would be exactly the
leakage Article V forbids: the buyer who trains on truth gets a meaningless
perfect score). Model: logistic regression (Doctrine Article VII-1 caps the
model choice at logistic regression or gradient boosting; logistic regression
is used here deliberately as the SIMPLER of the two permitted options, since
the point of this benchmark is to show the data supports a real predictive
signal, not to chase the highest possible number).
"""
import sys, json, time
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.preprocessing import StandardScaler

SEED = 20261027
DATASET = sys.argv[1] if len(sys.argv) > 1 else "../BUILD/ПОСТАВКА/DATASET"
OUT = sys.argv[2] if len(sys.argv) > 2 else "../BUILD/ПОСТАВКА/VALIDATION/benchmark_results.parquet"

def build_features():
    crew = pd.read_parquet(f"{DATASET}/crew.parquet")
    obs = pd.read_parquet(f"{DATASET}/observations.parquet")
    outcomes = pd.read_parquet(f"{DATASET}/outcomes.parquet")
    factual = outcomes[outcomes["scenario"] == "factual"].set_index("subject_id")

    g = obs.groupby("subject_id")
    feat = pd.DataFrame({
        "hr_ecg_max": g["hr_ecg"].max(),
        "hr_ecg_mean": g["hr_ecg"].mean(),
        "bp_min": g["beat_to_beat_bp"].min(),
        "bp_mean": g["beat_to_beat_bp"].mean(),
        "bp_missing_frac": g["beat_to_beat_bp"].apply(lambda s: s.isna().mean()),
        "finger_cuff_dropout_frac": g["finger_cuff_dropout"].mean(),
        "symptoms_reported_any": g["symptoms_reported"].max().astype(int),
        # NOTE: a "rows recorded" / test-duration feature was tried and
        # removed -- see validation_report, "known model limitation". The
        # kernel's second_of_presyncope has ~zero variance (always the first
        # post-standing sample when it occurs at all; verified against the
        # delivered truth.parquet, not assumed), so any feature that encodes
        # how long the test ran is a near-exact proxy for the label itself
        # and produces a trivial, dishonest 100% benchmark. Removed per
        # Doctrine Art 9.7/9.8: a suspiciously perfect result gets
        # investigated and the fabricated-looking feature dropped, not kept.
    })
    df = feat.join(crew.set_index("subject_id")[["age", "fitness", "mission_days", "prior_flights"]])
    df = df.join(pd.get_dummies(crew.set_index("subject_id")["countermeasure"], prefix="cm"))
    df = df.join(pd.get_dummies(crew.set_index("subject_id")["sex"], prefix="sex"))
    df["y"] = factual["presyncope"].astype(int)
    df = df.dropna()
    return df

def run_cv(df, cols, label):
    X = df[cols].to_numpy(dtype=np.float64)
    y = df["y"].to_numpy()
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    fold_rows = []
    for fold, (tr, te) in enumerate(skf.split(X, y)):
        scaler = StandardScaler().fit(X[tr])
        Xtr, Xte = scaler.transform(X[tr]), scaler.transform(X[te])
        clf = LogisticRegression(max_iter=2000, random_state=SEED)
        clf.fit(Xtr, y[tr])
        p = clf.predict_proba(Xte)[:, 1]
        pred = (p >= 0.5).astype(int)
        fold_rows.append(dict(
            task=label, fold=fold, n_test=len(te), auc=float(roc_auc_score(y[te], p)),
            accuracy=float(accuracy_score(y[te], pred)),
            positive_rate_test=float(y[te].mean()),
        ))
    results = pd.DataFrame(fold_rows)
    return results, dict(
        n_subjects=len(df), n_features=len(cols), feature_names=cols, seed=SEED,
        mean_auc=float(results["auc"].mean()), std_auc=float(results["auc"].std()),
        mean_accuracy=float(results["accuracy"].mean()), std_accuracy=float(results["accuracy"].std()),
        fold_results=fold_rows,
    )

def main():
    df = build_features()
    all_cols = [c for c in df.columns if c != "y"]
    obs_cols = ["hr_ecg_max", "hr_ecg_mean", "bp_min", "bp_mean", "bp_missing_frac",
                "finger_cuff_dropout_frac", "symptoms_reported_any"]
    covariate_cols = [c for c in all_cols if c not in obs_cols]

    results_detect, summary_detect = run_cv(df, all_cols, "A_detection_during_test")
    results_screen, summary_screen = run_cv(df, covariate_cols, "B_screening_pretest_only")
    results = pd.concat([results_detect, results_screen], ignore_index=True)
    results.to_parquet(OUT, index=False)

    summary = dict(
        task_A_detection=dict(
            description=("Predict presyncope from DURING-THE-TEST observations (BP/HR readings + crew "
                          "covariates) -- NOT from truth. Near-perfect by construction: presyncope is "
                          "clinically DEFINED as MAP crossing a threshold, and beat_to_beat_bp is that "
                          "same signal plus small observation noise, so this mainly confirms the noise "
                          "model preserves the diagnostic signal, not that a hard prediction problem was "
                          "solved. Reported honestly rather than hidden (Doctrine Art 9.7/9.8): a 100% "
                          "number here is expected, not impressive."),
            **summary_detect),
        task_B_screening=dict(
            description=("The actually informative number: predict presyncope using ONLY pre-test crew "
                          "covariates (age, fitness, mission_days, prior_flights, countermeasure, sex) -- "
                          "i.e. BEFORE any tilt-test reading exists, the real screening/triage question a "
                          "flight surgeon would ask before testing an astronaut."),
            **summary_screen),
        real_world_comparison=dict(
            citation="Hart JL, Gilmore S, Gremaud P, Olsen CH, Mehlsen J, Olufsen MS (2021). "
                     "Classification of orthostatic intolerance through data analytics. "
                     "Medical and Biological Engineering and Computing 59(3). "
                     "DOI 10.1007/s11517-021-02314-0 (Sandia report SAND2020-2937J).",
            real_world_metric=">95% accuracy classifying patients with a single orthostatic-intolerance condition (exact AUC not reported)",
            honesty_note=("NOT a like-for-like comparison: Hart et al. classify real patients by "
                           "condition subtype using their own feature set and population; this benchmark "
                           "predicts a synthetic cohort's presyncope OUTCOME from synthetic noisy "
                           "observations only. The citation is included because Article VII-1 requires "
                           "one, not because the two numbers measure the same thing. Treat the >95% figure "
                           "as a real-world existence proof that this class of signal IS predictable from "
                           "physiological observations, not as a target this benchmark should match."),
        ),
    )
    print(json.dumps(summary, indent=1))
    return summary

if __name__ == "__main__":
    main()
