"""Reusable interactive Plotly chart generators."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.config.settings import settings


def plot_monthly_cashflow(monthly_df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart for monthly income vs expense with net savings line."""
    if monthly_df.empty:
        return go.Figure()

    fig = go.Figure()

    # Format month labels as "Jan 2026", etc.
    x_labels = monthly_df["month"].dt.strftime("%b %Y")

    # Income Bars
    fig.add_trace(go.Bar(
        x=x_labels,
        y=monthly_df["income"],
        name="Income",
        marker_color="#2ecc71",
        hovertemplate="%{x}<br>Income: <b>$%{y:,.2f}</b><extra></extra>"
    ))

    # Expense Bars
    fig.add_trace(go.Bar(
        x=x_labels,
        y=monthly_df["expense"],
        name="Expenses",
        marker_color="#e74c3c",
        hovertemplate="%{x}<br>Expenses: <b>$%{y:,.2f}</b><extra></extra>"
    ))

    # Net Savings Line
    fig.add_trace(go.Scatter(
        x=x_labels,
        y=monthly_df["net_savings"],
        name="Net Savings",
        mode="lines+markers",
        line=dict(color="#3498db", width=3, dash="dash"),
        marker=dict(size=8),
        hovertemplate="%{x}<br>Net Savings: <b>$%{y:,.2f}</b><extra></extra>"
    ))

    fig.update_layout(
        barmode="group",
        title="<b>Monthly Cash Flow & Net Savings</b>",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def plot_category_donut(cat_df: pd.DataFrame, title: str = "Expenses by Category") -> go.Figure:
    """Donut chart for category distribution."""
    if cat_df.empty:
        return go.Figure()

    colors = [settings.category_colors.get(cat, "#95a5a6") for cat in cat_df["category"]]

    fig = go.Figure(data=[go.Pie(
        labels=cat_df["category"],
        values=cat_df["total_amount"],
        hole=0.55,
        marker=dict(colors=colors),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Total: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
    )])

    total_amount = cat_df["total_amount"].sum()

    fig.update_layout(
        title=f"<b>{title}</b>",
        template="plotly_white",
        annotations=[dict(
            text=f"Total<br><b>${total_amount:,.0f}</b>",
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False
        )],
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def plot_category_treemap(df: pd.DataFrame) -> go.Figure:
    """Treemap of expenses showing proportional weight of categories and notes."""
    expenses = df[df["type"] == "expense"].copy()
    if expenses.empty:
        return go.Figure()

    fig = px.treemap(
        expenses,
        path=["category", "account"],
        values="amount",
        title="<b>Expense Hierarchy Treemap</b>",
        color="category",
        color_discrete_map=settings.category_colors
    )
    fig.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=50, b=10))
    return fig


def plot_cumulative_balance(cum_df: pd.DataFrame) -> go.Figure:
    """Line/area chart showing cumulative net cash flow over time."""
    if cum_df.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cum_df["date"],
        y=cum_df["cumulative_balance"],
        mode="lines",
        name="Cumulative Cash Flow",
        line=dict(color="#1abc9c", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(26, 188, 156, 0.12)",
        hovertemplate="%{x|%Y-%m-%d}<br>Net Balance: <b>$%{y:,.2f}</b><extra></extra>"
    ))

    fig.update_layout(
        title="<b>Cumulative Cash Flow & Net Trajectory</b>",
        xaxis_title="Date",
        yaxis_title="Cumulative Net ($)",
        template="plotly_white",
        hovermode="x",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def plot_spending_forecast(historical_df: pd.DataFrame, forecast_df: pd.DataFrame) -> go.Figure:
    """Displays actual daily spending, rolling mean, and forecasted linear trend."""
    fig = go.Figure()

    if not historical_df.empty:
        # Raw Daily Spend Points
        fig.add_trace(go.Scatter(
            x=historical_df["date"],
            y=historical_df["amount"],
            mode="markers",
            name="Daily Spend",
            marker=dict(size=5, color="rgba(149, 165, 166, 0.5)"),
            hovertemplate="%{x|%Y-%m-%d}<br>Daily Spend: <b>$%{y:,.2f}</b><extra></extra>"
        ))

        # 7-day rolling average
        fig.add_trace(go.Scatter(
            x=historical_df["date"],
            y=historical_df["rolling_7d"],
            mode="lines",
            name="7-Day Moving Avg",
            line=dict(color="#2980b9", width=2.5),
            hovertemplate="%{x|%Y-%m-%d}<br>7-Day Avg: <b>$%{y:,.2f}</b><extra></extra>"
        ))

    if not forecast_df.empty:
        # Forecasted projection line
        fig.add_trace(go.Scatter(
            x=forecast_df["date"],
            y=forecast_df["predicted_daily_spend"],
            mode="lines+markers",
            name="ML Projected Trend",
            line=dict(color="#e67e22", width=3, dash="dot"),
            marker=dict(size=6),
            hovertemplate="%{x|%Y-%m-%d}<br>Projected: <b>$%{y:,.2f}</b><extra></extra>"
        ))

    fig.update_layout(
        title="<b>Daily Spending Trajectory & ML Forecast (Next 30 Days)</b>",
        xaxis_title="Date",
        yaxis_title="Daily Spend ($)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def plot_anomaly_scatter(anomaly_df: pd.DataFrame) -> go.Figure:
    """Scatter plot displaying normal transactions vs flagged outliers."""
    if anomaly_df.empty:
        return go.Figure()

    normal = anomaly_df[~anomaly_df["is_anomaly"]]
    anomalies = anomaly_df[anomaly_df["is_anomaly"]]

    fig = go.Figure()

    # Normal transactions
    fig.add_trace(go.Scatter(
        x=normal["date"],
        y=normal["amount"],
        mode="markers",
        name="Normal Expenses",
        marker=dict(size=6, color="#3498db", opacity=0.6),
        hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>Date: %{x|%Y-%m-%d}<br>Amount: $%{y:,.2f}<extra></extra>",
        customdata=normal[["category", "note"]].values
    ))

    # Flagged Anomalies
    if not anomalies.empty:
        fig.add_trace(go.Scatter(
            x=anomalies["date"],
            y=anomalies["amount"],
            mode="markers+text",
            name="Flagged Anomalies",
            marker=dict(size=13, color="#e74c3c", symbol="diamond-dot", line=dict(width=2, color="#c0392b")),
            text=anomalies["note"],
            textposition="top center",
            hovertemplate="<b>🚨 ANOMALY: %{customdata[0]}</b><br>Note: %{customdata[1]}<br>Date: %{x|%Y-%m-%d}<br>Amount: <b>$%{y:,.2f}</b><br>Reason: %{customdata[2]}<extra></extra>",
            customdata=anomalies[["category", "note", "reason"]].values
        ))

    fig.update_layout(
        title="<b>Expense Anomaly Detection (Isolation Forest)</b>",
        xaxis_title="Date",
        yaxis_title="Expense Amount ($)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig
