"""Data models and schemas for financial transactions."""
from datetime import date as DateType
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
import pandas as pd


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Transaction(BaseModel):
    id: str = Field(..., description="Unique identifier for the transaction")
    date: DateType = Field(..., description="Date of transaction (YYYY-MM-DD)")
    amount: float = Field(..., description="Transaction amount (positive value)")
    type: TransactionType = Field(default=TransactionType.EXPENSE, description="Transaction type")
    category: str = Field(default="Other", description="Spending or income category")
    account: str = Field(default="Checking", description="Source or destination account")
    note: Optional[str] = Field(default="", description="Description or note")
    tags: list[str] = Field(default_factory=list, description="Optional labels or tags")

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Amount must be positive; use 'type' to indicate income vs expense")
        return round(float(v), 2)


def transactions_to_df(transactions: list[Transaction]) -> pd.DataFrame:
    """Converts a list of Transaction models into an analytical Pandas DataFrame."""
    if not transactions:
        return pd.DataFrame(columns=["id", "date", "amount", "type", "category", "account", "note", "tags", "signed_amount"])

    records = [t.model_dump() for t in transactions]
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    # signed_amount: positive for income, negative for expense
    df["signed_amount"] = df.apply(
        lambda r: r["amount"] if r["type"] == TransactionType.INCOME.value else -r["amount"],
        axis=1
    )
    return df.sort_values(by="date", ascending=True).reset_index(drop=True)


def df_to_transactions(df: pd.DataFrame) -> list[Transaction]:
    """Validates and converts a pandas DataFrame into Transaction objects."""
    records = df.to_dict(orient="records")
    return [Transaction(**record) for record in records]
