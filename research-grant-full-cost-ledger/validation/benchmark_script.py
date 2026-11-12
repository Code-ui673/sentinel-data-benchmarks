"""D09 detection benchmark — flag ineligible cost charges from observable features.
Seed fixed (20261101); package versions: python 3.11, pandas 2.3.1, numpy 2.1.0,
scikit-learn 1.7.1, pyarrow 21.0.0.
Usage: python benchmark_script.py --dataset ../DATASET --out benchmark_results.parquet
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

SEED = 20261101

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="../DATASET")
    ap.add_argument("--out", default="benchmark_results.parquet")
    args = ap.parse_args()
    d = Path(args.dataset)
    e = pd.read_parquet(d / "expenditure.parquet")
    aw = pd.read_parquet(d / "award.parquet").set_index("award_id")
    fin = pd.read_parquet(d / "award_financials.parquet")
    feat = e.merge(fin, on="award_id").merge(aw[["funder", "department", "start_date"]], on="award_id")
    feat["date"] = pd.to_datetime(feat.date)
    feat["log_amount"] = np.log10(feat.amount)
    feat["month"] = feat.date.dt.month
    feat["award_age_days"] = (feat.date - pd.to_datetime(feat.award_id.map(aw.start_date))).dt.days
    X = pd.get_dummies(feat[["funder", "department", "category", "log_amount", "month",
                             "award_age_days", "n_fte", "annual_direct"]],
                       columns=["funder", "department", "category"], drop_first=True)
    y = (~feat.eligible).astype(int).values
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    rows = []
    for name, m in (("logistic_regression", LogisticRegression(max_iter=2000, C=1.0)),
                    ("gradient_boosting", GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=SEED))):
        p = cross_val_predict(m, X, y, cv=cv, method="predict_proba")[:, 1]
        rows.append(dict(model=name, auc=round(float(roc_auc_score(y, p)), 4),
                         n=int(len(y)), prevalence=round(float(y.mean()), 4)))
    res = pd.DataFrame(rows)
    res.to_parquet(args.out, index=False)
    print(res.to_string(index=False))

if __name__ == "__main__":
    main()
