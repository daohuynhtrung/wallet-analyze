"""Expenses Breakdown & Category Analysis Page."""
import streamlit as st
import pandas as pd
from src.analytics.metrics import compute_category_breakdown
from src.components.ui import render_sidebar_filters
from src.components.charts import plot_category_donut, plot_category_treemap

st.set_page_config(page_title="Expenses Breakdown - WalletAnalyze", page_icon="💸", layout="wide")

if "transactions_df" not in st.session_state:
    st.warning("No data found in session. Please visit the main dashboard first.")
    st.stop()

df = st.session_state["transactions_df"]
filtered_df = render_sidebar_filters(df)

st.title("💸 Expenses & Outflow Breakdown")
st.markdown("Analyze how money is allocated across categories, accounts, and vendors.")

expense_df = filtered_df[filtered_df["type"] == "expense"]
if expense_df.empty:
    st.warning("No expense transactions match the current filter selection.")
    st.stop()

cat_summary = compute_category_breakdown(filtered_df, transaction_type="expense")

# Charts: Donut & Treemap
col_donut, col_tree = st.columns([1, 1])

with col_donut:
    st.plotly_chart(plot_category_donut(cat_summary), use_container_width=True)

with col_tree:
    st.plotly_chart(plot_category_treemap(filtered_df), use_container_width=True)

st.markdown("---")

# Detailed Category Table
st.subheader("📊 Category Statistics")
col_table, col_top = st.columns([3, 2])

with col_table:
    formatted_cats = cat_summary.copy()
    formatted_cats = formatted_cats.rename(columns={
        "category": "Category",
        "total_amount": "Total ($)",
        "percentage": "Share (%)",
        "count": "Transactions",
        "average_amount": "Avg Ticket ($)"
    })
    st.dataframe(
        formatted_cats.style.format({
            "Total ($)": "${:,.2f}",
            "Share (%)": "{:.1f}%",
            "Avg Ticket ($)": "${:,.2f}",
            "Transactions": "{:,}"
        }),
        use_container_width=True,
        hide_index=True
    )

with col_top:
    st.subheader("🔍 Top Individual Expenses")
    top_expenses = expense_df.sort_values(by="amount", ascending=False).head(5)[
        ["date", "category", "amount", "note"]
    ]
    st.dataframe(
        top_expenses.style.format({"amount": "${:,.2f}", "date": lambda t: t.strftime("%Y-%m-%d")}),
        use_container_width=True,
        hide_index=True
    )

# All Transactions Table with CSV Export
st.markdown("---")
st.subheader("📑 Filtered Expense Records")
csv_data = expense_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Export Filtered Expenses (CSV)",
    data=csv_data,
    file_name="expenses_export.csv",
    mime="text/csv"
)

st.dataframe(
    expense_df[["id", "date", "category", "account", "amount", "note"]].style.format({
        "amount": "${:,.2f}",
        "date": lambda t: t.strftime("%Y-%m-%d")
    }),
    use_container_width=True,
    hide_index=True
)
