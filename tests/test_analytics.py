"""Automated tests for data schemas, metrics, ML models, and loader."""
import pytest
import pandas as pd
from datetime import date
from src.data.schema import Transaction, TransactionType, transactions_to_df
from src.data.generator import generate_mock_transactions
from src.data.loader import run_sql_query
from src.analytics.metrics import compute_kpis, compute_category_breakdown, compute_monthly_summary
from src.analytics.anomaly import detect_expense_anomalies
from src.analytics.forecasting import forecast_spending_trends


def test_transaction_schema_validation():
    tx = Transaction(
        id="t1",
        date=date(2026, 11, 1),
        amount=100.5,
        type=TransactionType.EXPENSE,
        category="Groceries",
        account="Checking",
        note="Groceries trip"
    )
    assert tx.amount == 100.5
    assert tx.type == TransactionType.EXPENSE

    # Test negative amount raises validation error
    with pytest.raises(ValueError):
        Transaction(
            id="t2",
            date=date(2026, 11, 1),
            amount=-50.0,
            type=TransactionType.EXPENSE
        )


def test_mock_generation_and_dataframe_conversion():
    txs = generate_mock_transactions(days=60, seed=123)
    assert len(txs) > 20

    df = transactions_to_df(txs)
    assert not df.empty
    assert "signed_amount" in df.columns
    assert "date" in df.columns
    assert len(df[df["signed_amount"] > 0]) > 0  # Has income
    assert len(df[df["signed_amount"] < 0]) > 0  # Has expenses


def test_kpi_computation():
    txs = [
        Transaction(id="1", date=date(2026, 1, 1), amount=2000.0, type=TransactionType.INCOME, category="Salary"),
        Transaction(id="2", date=date(2026, 1, 5), amount=500.0, type=TransactionType.EXPENSE, category="Housing"),
        Transaction(id="3", date=date(2026, 1, 10), amount=100.0, type=TransactionType.EXPENSE, category="Food"),
    ]
    df = transactions_to_df(txs)
    kpis = compute_kpis(df)

    assert kpis["total_income"] == 2000.0
    assert kpis["total_expenses"] == 600.0
    assert kpis["net_savings"] == 1400.0
    assert kpis["savings_rate_pct"] == 70.0
    assert kpis["top_expense_category"] == "Housing"


def test_duckdb_sql_query():
    txs = generate_mock_transactions(days=30)
    df = transactions_to_df(txs)

    query = """
    SELECT category, count(*) as count, sum(amount) as total
    FROM transactions
    WHERE type = 'expense'
    GROUP BY category
    ORDER BY total DESC
    LIMIT 3
    """
    result = run_sql_query(df, query)
    assert len(result) <= 3
    assert "category" in result.columns
    assert "total" in result.columns


def test_anomaly_detection():
    txs = generate_mock_transactions(days=90)
    df = transactions_to_df(txs)

    analyzed = detect_expense_anomalies(df, contamination=0.05, min_amount=50.0)
    assert "is_anomaly" in analyzed.columns
    assert "anomaly_score" in analyzed.columns
    assert "reason" in analyzed.columns
    # Verify flagged items exist
    flagged = analyzed[analyzed["is_anomaly"]]
    assert len(flagged) > 0


def test_spending_forecast():
    txs = generate_mock_transactions(days=60)
    df = transactions_to_df(txs)

    forecast_results = forecast_spending_trends(df, forecast_days=14)
    assert not forecast_results["historical"].empty
    assert len(forecast_results["forecast"]) == 14
    assert forecast_results["projected_monthly_spend"] > 0
