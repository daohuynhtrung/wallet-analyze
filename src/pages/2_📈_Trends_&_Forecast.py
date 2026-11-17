"""Time-series Analysis & ML Trend Forecasting Page."""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from src.analytics.forecasting import forecast_spending_trends
from src.analytics.metrics import compute_monthly_summary
from src.components.ui import render_sidebar_filters
from src.components.charts import plot_spending_forecast

st.set_page_config(page_title="Trends & Forecasting - WalletAnalyze", page_icon="📈", layout="wide")

if "transactions_df" not in st.session_state:
    st.warning("No data found in session. Please visit the main dashboard first.")
    st.stop()

df = st.session_state["transactions_df"]
filtered_df = render_sidebar_filters(df)

st.title("📈 Spending Trends & Predictive Forecast")
st.markdown("Leverage statistical moving averages and **Scikit-Learn** linear regression to project future outflows.")

col_controls, col_stats = st.columns([1, 2])

with col_controls:
    forecast_horizon = st.slider(
        "Forecast Horizon (Days)",
        min_value=14,
        max_value=90,
        value=30,
        step=7
    )

forecast_results = forecast_spending_trends(filtered_df, forecast_days=forecast_horizon)
historical_daily = forecast_results["historical"]
forecast_daily = forecast_results["forecast"]

with col_stats:
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Projected 30-Day Outflow",
        f"${forecast_results['projected_monthly_spend']:,.2f}"
    )
    slope = forecast_results["trend_slope_per_day"]
    slope_label = "Increasing" if slope > 0 else "Decreasing"
    c2.metric(
        "Daily Spend Trajectory",
        f"${abs(slope):.2f}/day",
        delta=f"{slope_label} trend",
        delta_color="inverse" if slope > 0 else "normal"
    )
    avg_hist_daily = historical_daily["amount"].mean() if not historical_daily.empty else 0.0
    c3.metric(
        "Historical Daily Avg",
        f"${avg_hist_daily:,.2f}/day"
    )

st.markdown("---")

# Forecast Chart
st.plotly_chart(
    plot_spending_forecast(historical_daily, forecast_daily),
    use_container_width=True
)

st.markdown("---")

# Month-over-Month Comparison Table
st.subheader("🗓️ Monthly Comparison Table")
monthly_df = compute_monthly_summary(filtered_df)

if not monthly_df.empty:
    display_monthly = monthly_df.copy()
    display_monthly["Month"] = display_monthly["month"].dt.strftime("%B %Y")
    display_monthly["Income"] = display_monthly["income"].map("${:,.2f}".format)
    display_monthly["Expense"] = display_monthly["expense"].map("${:,.2f}".format)
    display_monthly["Net Savings"] = display_monthly["net_savings"].map("${:,.2f}".format)
    display_monthly["Savings Rate"] = display_monthly["savings_rate"].map("{:.1f}%".format)

    st.dataframe(
        display_monthly[["Month", "Income", "Expense", "Net Savings", "Savings Rate"]],
        use_container_width=True,
        hide_index=True
    )
