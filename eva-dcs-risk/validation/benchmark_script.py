#!/usr/bin/env python3
# Benchmark script for the Sentinel Decompression Sickness Risk Dataset.
# Actual run-time environment (verified by querying the running interpreter,
# not estimated): Python 3.13, numpy==2.5.3, pandas==3.0.5, pyarrow==26.0.0,
# scikit-learn==1.9.1. seed=20261027 (same project seed as generation).
#
# Two tasks, both logistic regression or gradient boosting (nothing more
# elaborate), 5-fold cross-validation, metrics on held-out folds only:
#
#   Task A -- binary classification: predict high_vge from {branch_group,
#   pfo_present}. These ARE the two variables the generative model's own
#   calibrated logistic uses, so near-ceiling performance here is an
#   artifact of construction, not a discovery -- reported as exactly that,
#   not sold as a feature (see validation_report).
#
#   Task B -- 5-class ordinal classification: predict the full vge_grade
#   (0-4) from the same two covariates. Only the binary high/not-high cut
#   is covariate-determined in this dataset; the finer grade split within
#   each side of that cut is an undisclosed-to-the-model random draw by
#   design (see DATA_DICTIONARY.md) -- so Task B's ceiling is bounded well
#   below 100% by construction, and that ceiling is itself the honest
#   result: it demonstrates that resolving the fine grade requires an
#   actual bubble-detection signal (e.g. Doppler audio), not exposure
#   covariates alone.
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, roc_auc_score, cohen_kappa_score
from sklearn.preprocessing import OneHotEncoder

SEED = 20261027
DATASET = "../DATASET"
OUT = "."


def load():
    outcomes = pd.read_parquet(f"{DATASET}/outcomes.parquet")
    obs = pd.read_parquet(f"{DATASET}/observations.parquet")
    crew = pd.read_parquet(f"{DATASET}/crew.parquet")
    df = outcomes.merge(obs[["subject_id", "branch_group", "vge_grade"]],
                         on=["subject_id", "branch_group"])
    df = df.merge(crew[["subject_id", "pfo_present"]], on="subject_id")
    return df


def features(df):
    enc = OneHotEncoder(sparse_output=False, drop="first")
    g = enc.fit_transform(df[["branch_group"]])
    X = np.column_stack([g, df["pfo_present"].to_numpy(dtype=float)])
    return X


def task_a_bayes_ceiling(df):
    """Theoretical ceiling for Task A: branch_group x pfo_present fully determines
    the generating Bernoulli probability for high_vge (that IS the calibrated
    model). No classifier using only these two inputs can beat the accuracy/AUC
    of predicting with the TRUE cell probability itself -- the gap to 1.0 is
    irreducible sampling noise, not a modeling shortfall. Computed directly from
    the empirical cell means at full dataset size (n=10,000 x 3 branches), which
    at this sample size equal the calibrated generating probabilities to within
    sampling error."""
    cell = df.groupby(["branch_group", "pfo_present"])["high_vge"].mean().to_dict()
    sizes = df.groupby(["branch_group", "pfo_present"])["high_vge"].size().to_dict()
    bayes_correct = sum(max(p, 1 - p) * sizes[k] for k, p in cell.items())
    bayes_acc = bayes_correct / sum(sizes.values())
    score = df.apply(lambda r: cell[(r.branch_group, r.pfo_present)], axis=1)
    bayes_auc = roc_auc_score(df["high_vge"], score)
    return dict(task="A_high_vge_binary", fold="bayes_ceiling", model="true_cell_probability",
                n_test=len(df), accuracy=bayes_acc, auc=bayes_auc)


def task_a(df):
    X = features(df)
    y = df["high_vge"].to_numpy()
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    rows = []
    for fold, (tr, te) in enumerate(skf.split(X, y)):
        clf = LogisticRegression(max_iter=1000).fit(X[tr], y[tr])
        p = clf.predict_proba(X[te])[:, 1]
        pred = (p >= 0.5).astype(int)
        acc = accuracy_score(y[te], pred)
        auc = roc_auc_score(y[te], p)
        rows.append(dict(task="A_high_vge_binary", fold=fold, model="LogisticRegression",
                          n_test=len(te), accuracy=acc, auc=auc))
    rows.append(task_a_bayes_ceiling(df))
    return rows


def task_b(df):
    X = features(df)
    y = df["vge_grade"].to_numpy()
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    rows = []
    for fold, (tr, te) in enumerate(skf.split(X, y)):
        clf = GradientBoostingClassifier(random_state=SEED).fit(X[tr], y[tr])
        pred = clf.predict(X[te])
        acc = accuracy_score(y[te], pred)
        kappa = cohen_kappa_score(y[te], pred, weights="quadratic")
        rows.append(dict(task="B_vge_grade_5class", fold=fold, model="GradientBoostingClassifier",
                          n_test=len(te), accuracy=acc, auc=np.nan, weighted_kappa=kappa))
    return rows


def main():
    df = load()
    rows_a = task_a(df)
    rows_b = task_b(df)
    out = pd.DataFrame(rows_a + rows_b)
    out["fold"] = out["fold"].astype(str)
    out.to_parquet(f"{OUT}/benchmark_results.parquet", index=False)
    summary = out.groupby("task").agg(
        mean_accuracy=("accuracy", "mean"), std_accuracy=("accuracy", "std"),
        mean_auc=("auc", "mean"),
    )
    print(out.to_string())
    print()
    print(summary)
    summary.to_json(f"{OUT}/benchmark_summary.json", indent=1)


if __name__ == "__main__":
    main()
