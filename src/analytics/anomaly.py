"""Machine Learning anomaly detection for financial transactions using scikit-learn."""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_expense_anomalies(
    df: pd.DataFrame,
    contamination: float = 0.03,
    min_amount: float = 50.0
) -> pd.DataFrame:
    """
    Detects unusual/abnormal expense transactions using Isolation Forest and category-relative statistics.
    Returns the dataframe enriched with anomaly flags, scores, and human-readable reasons.
    """
    expenses = df[df["type"] == "expense"].copy()
    if len(expenses) < 10:
        expenses["is_anomaly"] = False
        expenses["anomaly_score"] = 0.0
        expenses["reason"] = "Insufficient data"
        return expenses

    # Calculate category baselines
    cat_stats = expenses.groupby("category")["amount"].agg(["mean", "std", "median"]).reset_index()
    cat_stats = cat_stats.rename(
        columns={"mean": "cat_mean", "std": "cat_std", "median": "cat_median"}
    )
    # Fill zero/null std with a minimum default
    cat_stats["cat_std"] = cat_stats["cat_std"].fillna(cat_stats["cat_mean"] * 0.2)

    enriched = expenses.merge(cat_stats, on="category", how="left")

    # Ratio of amount to category median
    enriched["amount_ratio"] = (enriched["amount"] / enriched["cat_median"].clip(lower=1.0)).round(2)

    # Feature matrix for IsolationForest
    # Features: amount, ratio to category median, day of month
    features = np.column_stack([
        enriched["amount"].values,
        enriched["amount_ratio"].values,
        enriched["date"].dt.day.values
    ])

    # Fit Isolation Forest
    iso_forest = IsolationForest(
        contamination=max(0.01, min(0.15, contamination)),
        random_state=42,
        n_estimators=100
    )
    iso_forest.fit(features)
    preds = iso_forest.predict(features)  # -1 for anomaly, 1 for normal
    scores = iso_forest.decision_function(features)

    # Anomaly conditions: predicted -1 AND amount >= min_amount
    is_anomaly = (preds == -1) & (enriched["amount"] >= min_amount)
    enriched["is_anomaly"] = is_anomaly
    enriched["anomaly_score"] = (-scores).round(3)

    # Generate human-readable explanation
    def build_reason(row) -> str:
        if not row["is_anomaly"]:
            return "Normal"
        ratio = row["amount_ratio"]
        med = row["cat_median"]
        return f"{ratio:.1f}x higher than median {row['category']} spending (${med:,.2f})"

    enriched["reason"] = enriched.apply(build_reason, axis=1)

    return enriched.sort_values(by="anomaly_score", ascending=False).reset_index(drop=True)
