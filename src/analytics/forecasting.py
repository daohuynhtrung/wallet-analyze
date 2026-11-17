"""Time-series forecasting and trend projection using scikit-learn."""
from datetime import timedelta
from typing import Any
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def forecast_spending_trends(
    df: pd.DataFrame,
    forecast_days: int = 30
) -> dict[str, Any]:
    """
    Fits a linear trend model on daily cumulative expense data and forecasts future trajectory.
    Returns historical daily data, forecast points, and key projected statistics.
    """
    expenses = df[df["type"] == "expense"].copy()
    if expenses.empty or len(expenses["date"].unique()) < 5:
        return {
            "historical": pd.DataFrame(),
            "forecast": pd.DataFrame(),
            "projected_monthly_spend": 0.0,
            "trend_slope_per_day": 0.0
        }

    # Aggregate daily spending
    daily = expenses.groupby("date")["amount"].sum().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values(by="date").reset_index(drop=True)

    # Reindex over full continuous date range
    full_range = pd.date_range(start=daily["date"].min(), end=daily["date"].max(), freq="D")
    daily = daily.set_index("date").reindex(full_range, fill_value=0.0).rename_axis("date").reset_index()

    # Cumulative spending and 7-day rolling mean
    daily["rolling_7d"] = daily["amount"].rolling(window=7, min_periods=1).mean()
    daily["day_index"] = (daily["date"] - daily["date"].min()).dt.days

    # Fit Linear Regression on day_index -> 7-day rolling mean
    X = daily[["day_index"]].values
    y = daily["rolling_7d"].values

    reg = LinearRegression()
    reg.fit(X, y)

    last_day_index = int(daily["day_index"].max())
    last_date = daily["date"].max()

    future_indices = np.arange(last_day_index + 1, last_day_index + forecast_days + 1).reshape(-1, 1)
    future_dates = [last_date + timedelta(days=int(i - last_day_index)) for i in future_indices.flatten()]
    future_predictions = np.clip(reg.predict(future_indices), a_min=0, a_max=None)

    forecast_df = pd.DataFrame({
        "date": future_dates,
        "predicted_daily_spend": future_predictions.round(2)
    })

    projected_monthly = float(np.mean(future_predictions) * 30.0)
    slope = float(reg.coef_[0])

    return {
        "historical": daily,
        "forecast": forecast_df,
        "projected_monthly_spend": round(projected_monthly, 2),
        "trend_slope_per_day": round(slope, 3)
    }
