"""Analytical metrics and aggregation computations."""
from typing import Any
import pandas as pd


def compute_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Computes high-level financial summary KPIs."""
    if df.empty:
        return {
            "total_income": 0.0,
            "total_expenses": 0.0,
            "net_savings": 0.0,
            "savings_rate_pct": 0.0,
            "daily_burn_rate": 0.0,
            "transaction_count": 0,
            "active_days": 0,
            "top_expense_category": "N/A",
            "top_category_spend": 0.0
        }

    income_df = df[df["type"] == "income"]
    expense_df = df[df["type"] == "expense"]

    total_income = float(income_df["amount"].sum())
    total_expenses = float(expense_df["amount"].sum())
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0

    # Date range calculations
    min_date = df["date"].min()
    max_date = df["date"].max()
    active_days = max(1, (max_date - min_date).days + 1)
    daily_burn = total_expenses / active_days

    # Top category
    if not expense_df.empty:
        cat_sums = expense_df.groupby("category")["amount"].sum()
        top_cat = cat_sums.idxmax()
        top_cat_amount = float(cat_sums.max())
    else:
        top_cat = "N/A"
        top_cat_amount = 0.0

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_savings": round(net_savings, 2),
        "savings_rate_pct": round(savings_rate, 1),
        "daily_burn_rate": round(daily_burn, 2),
        "transaction_count": len(df),
        "active_days": active_days,
        "top_expense_category": top_cat,
        "top_category_spend": round(top_cat_amount, 2)
    }


def compute_category_breakdown(df: pd.DataFrame, transaction_type: str = "expense") -> pd.DataFrame:
    """Computes category-wise aggregated statistics."""
    subset = df[df["type"] == transaction_type]
    if subset.empty:
        return pd.DataFrame(columns=["category", "total_amount", "percentage", "count", "average_amount"])

    total = subset["amount"].sum()
    grouped = subset.groupby("category").agg(
        total_amount=("amount", "sum"),
        count=("amount", "count"),
        average_amount=("amount", "mean")
    ).reset_index()

    grouped["percentage"] = (grouped["total_amount"] / total * 100).round(1)
    grouped["total_amount"] = grouped["total_amount"].round(2)
    grouped["average_amount"] = grouped["average_amount"].round(2)
    return grouped.sort_values(by="total_amount", ascending=False).reset_index(drop=True)


def compute_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates transactions into monthly periods for trend analysis."""
    if df.empty:
        return pd.DataFrame(columns=["month", "income", "expense", "net_savings", "savings_rate"])

    temp = df.copy()
    temp["month"] = temp["date"].dt.to_period("M").dt.to_timestamp()

    monthly_income = temp[temp["type"] == "income"].groupby("month")["amount"].sum()
    monthly_expense = temp[temp["type"] == "expense"].groupby("month")["amount"].sum()

    all_months = sorted(list(set(temp["month"])))
    records = []
    for m in all_months:
        inc = float(monthly_income.get(m, 0.0))
        exp = float(monthly_expense.get(m, 0.0))
        net = inc - exp
        rate = (net / inc * 100) if inc > 0 else 0.0
        records.append({
            "month": m,
            "income": round(inc, 2),
            "expense": round(exp, 2),
            "net_savings": round(net, 2),
            "savings_rate": round(rate, 1)
        })

    return pd.DataFrame(records)


def compute_cumulative_balance(df: pd.DataFrame, initial_balance: float = 0.0) -> pd.DataFrame:
    """Computes running net worth / cumulative cash flow over time."""
    if df.empty:
        return pd.DataFrame(columns=["date", "daily_flow", "cumulative_balance"])

    daily = df.groupby("date")["signed_amount"].sum().reset_index()
    daily = daily.rename(columns={"signed_amount": "daily_flow"})
    daily["cumulative_balance"] = initial_balance + daily["daily_flow"].cumsum()
    return daily
