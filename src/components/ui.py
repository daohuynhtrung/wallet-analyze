"""Reusable UI components, KPI card renderers, and sidebar filters."""
import streamlit as st
import pandas as pd
from typing import Tuple


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Renders unified sidebar filters (Date range, Accounts, Categories) and returns filtered df."""
    st.sidebar.markdown("### 🔍 Filters")

    if df.empty:
        return df

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    # Date range selector
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_d, end_d = date_range
        filtered_df = df[(df["date"].dt.date >= start_d) & (df["date"].dt.date <= end_d)].copy()
    else:
        filtered_df = df.copy()

    # Accounts multi-select
    all_accounts = sorted(list(df["account"].unique()))
    selected_accounts = st.sidebar.multiselect(
        "Accounts",
        options=all_accounts,
        default=all_accounts
    )
    if selected_accounts:
        filtered_df = filtered_df[filtered_df["account"].isin(selected_accounts)]

    # Categories multi-select
    all_categories = sorted(list(df["category"].unique()))
    selected_categories = st.sidebar.multiselect(
        "Categories",
        options=all_categories,
        default=all_categories
    )
    if selected_categories:
        filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]

    st.sidebar.caption(f"Showing **{len(filtered_df):,}** of **{len(df):,}** transactions")
    return filtered_df


def render_kpi_cards(kpis: dict[str, any]):
    """Renders responsive 4-column metric cards for high-level KPIs."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Income",
            value=f"${kpis['total_income']:,.2f}",
            delta=None
        )

    with col2:
        st.metric(
            label="Total Expenses",
            value=f"${kpis['total_expenses']:,.2f}",
            delta=f"${kpis['daily_burn_rate']:,.2f}/day",
            delta_color="inverse"
        )

    with col3:
        net = kpis["net_savings"]
        delta_color = "normal" if net >= 0 else "inverse"
        st.metric(
            label="Net Savings",
            value=f"${net:,.2f}",
            delta=f"{kpis['savings_rate_pct']:.1f}% rate",
            delta_color=delta_color
        )

    with col4:
        st.metric(
            label="Top Spending Area",
            value=kpis["top_expense_category"],
            delta=f"${kpis['top_category_spend']:,.2f}",
            delta_color="off"
        )
