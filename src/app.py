"""Main entrypoint for the WalletAnalyze Streamlit application."""
import sys
from pathlib import Path

# Ensure project root is in sys.path regardless of how Streamlit or Python was invoked
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from src.config.settings import settings
from src.data.loader import load_dataset
from src.analytics.metrics import compute_kpis, compute_monthly_summary, compute_cumulative_balance
from src.components.ui import render_sidebar_filters, render_kpi_cards
from src.components.charts import plot_monthly_cashflow, plot_cumulative_balance

# Page Configuration
st.set_page_config(
    page_title=f"{settings.app_name} - Financial Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom header styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_default_data() -> pd.DataFrame:
    """Loads and caches synthetic default transaction history."""
    return load_dataset(None)


def init_session():
    """Initializes session state data if not present."""
    if "transactions_df" not in st.session_state:
        st.session_state["transactions_df"] = get_default_data()
        st.session_state["data_source"] = "Synthetic Mock Dataset (180 days)"


init_session()
df = st.session_state["transactions_df"]

# Sidebar Header & Info
st.sidebar.title(f"💳 {settings.app_name}")
st.sidebar.caption(f"Data Source: **{st.session_state.get('data_source', 'Default')}**")

# Apply filters
filtered_df = render_sidebar_filters(df)

# Main Title
st.title("📊 Financial Health Overview")
st.markdown("Real-time cash flow metrics, category breakdowns, and predictive analytics.")

# Compute and render KPIs
kpis = compute_kpis(filtered_df)
render_kpi_cards(kpis)

st.markdown("---")

# Visualizations Row: Cashflow Bar & Cumulative Net Worth
col_left, col_right = st.columns([1, 1])

with col_left:
    monthly_df = compute_monthly_summary(filtered_df)
    st.plotly_chart(plot_monthly_cashflow(monthly_df), use_container_width=True)

with col_right:
    cum_df = compute_cumulative_balance(filtered_df, initial_balance=5000.0)
    st.plotly_chart(plot_cumulative_balance(cum_df), use_container_width=True)

st.markdown("---")

# Quick Insights & Recent Transactions
col_tx, col_actions = st.columns([2, 1])

with col_tx:
    st.subheader("📋 Recent Transactions")
    display_cols = ["date", "category", "account", "type", "amount", "note"]
    recent = filtered_df.sort_values(by="date", ascending=False).head(8)[display_cols]
    st.dataframe(
        recent.style.format({"amount": "${:,.2f}", "date": lambda t: t.strftime("%Y-%m-%d")}),
        use_container_width=True,
        hide_index=True
    )

with col_actions:
    st.subheader("💡 Analysis Highlights")
    st.info(
        f"• **Savings Rate:** You saved **{kpis['savings_rate_pct']}%** of income during this period.\n\n"
        f"• **Daily Average Burn:** Spending averages **${kpis['daily_burn_rate']:,.2f}/day**.\n\n"
        f"• **Primary Outflow:** **{kpis['top_expense_category']}** accounts for **${kpis['top_category_spend']:,.2f}**.\n\n"
        f"• Explore **Expenses**, **Trends & Forecast**, and **Anomaly Detection** in the sidebar!"
    )
