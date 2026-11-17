"""Machine Learning Anomaly & Outlier Detection Page."""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from src.analytics.anomaly import detect_expense_anomalies
from src.components.ui import render_sidebar_filters
from src.components.charts import plot_anomaly_scatter

st.set_page_config(page_title="Anomaly Detection - WalletAnalyze", page_icon="🚨", layout="wide")

if "transactions_df" not in st.session_state:
    st.warning("No data found in session. Please visit the main dashboard first.")
    st.stop()

df = st.session_state["transactions_df"]
filtered_df = render_sidebar_filters(df)

st.title("🚨 ML-Driven Anomaly Detection")
st.markdown(
    "Detect unusual expenses, potential fraudulent charges, or unexpected spikes using "
    "an **unsupervised Scikit-Learn `IsolationForest`** model conditioned on category distributions."
)

col_ctrl1, col_ctrl2 = st.columns(2)

with col_ctrl1:
    sensitivity = st.slider(
        "Model Sensitivity (Expected Outlier Ratio)",
        min_value=0.01,
        max_value=0.10,
        value=0.03,
        step=0.01,
        help="Higher sensitivity flags more subtle irregularities; lower sensitivity flags only severe outliers."
    )

with col_ctrl2:
    min_amount = st.number_input(
        "Minimum Outlier Amount ($)",
        min_value=10.0,
        max_value=1000.0,
        value=50.0,
        step=10.0,
        help="Transactions below this threshold will not be flagged as outliers."
    )

# Run detection
analyzed_df = detect_expense_anomalies(filtered_df, contamination=sensitivity, min_amount=min_amount)
anomalies = analyzed_df[analyzed_df["is_anomaly"]]

# Summary Metrics
c1, c2, c3 = st.columns(3)
c1.metric("Total Expenses Analyzed", len(analyzed_df))
c2.metric("Flagged Anomalies", len(anomalies), delta=f"{len(anomalies)/max(1, len(analyzed_df))*100:.1f}% of total", delta_color="inverse")
c3.metric("Anomalous Outflow", f"${anomalies['amount'].sum():,.2f}")

st.markdown("---")

# Scatter Chart
st.plotly_chart(plot_anomaly_scatter(analyzed_df), use_container_width=True)

st.markdown("---")

# Flagged List Table
st.subheader("🚩 Flagged Transactions & Algorithmic Explanations")

if anomalies.empty:
    st.success("🎉 No anomalies detected with the current sensitivity parameters!")
else:
    table_data = anomalies.copy()
    table_data["Date"] = table_data["date"].dt.strftime("%Y-%m-%d")
    table_data["Amount"] = table_data["amount"].map("${:,.2f}".format)
    table_data["Anomaly Score"] = table_data["anomaly_score"].map("{:.3f}".format)
    
    st.dataframe(
        table_data[["Date", "category", "Amount", "note", "reason", "Anomaly Score"]].rename(columns={
            "category": "Category",
            "note": "Note",
            "reason": "Detection Reason"
        }),
        use_container_width=True,
        hide_index=True
    )
