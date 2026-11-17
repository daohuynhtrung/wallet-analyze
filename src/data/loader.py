"""Data loader and transformation module."""
import json
from pathlib import Path
from typing import BinaryIO, Union
import pandas as pd
import duckdb

from src.data.schema import Transaction, TransactionType, transactions_to_df
from src.data.generator import generate_mock_transactions


def load_from_json(file_or_path: Union[str, Path, BinaryIO]) -> pd.DataFrame:
    """Loads and validates transactions from a JSON file or buffer."""
    if isinstance(file_or_path, (str, Path)):
        with open(file_or_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(file_or_path)

    # Allow both a raw list of transactions or a wrapper object {"transactions": [...]}
    raw_list = data.get("transactions", data) if isinstance(data, dict) else data
    transactions = [Transaction(**item) for item in raw_list]
    return transactions_to_df(transactions)


def load_from_csv(file_or_path: Union[str, Path, BinaryIO]) -> pd.DataFrame:
    """Loads transactions from a CSV file or buffer, normalizing column names."""
    df = pd.read_csv(file_or_path)
    # Standardize column headers (lowercase, strip whitespace)
    df.columns = [c.strip().lower() for c in df.columns]

    # Required column mapping heuristics
    required_cols = {"date", "amount"}
    if not required_cols.issubset(set(df.columns)):
        raise ValueError(f"CSV must contain at least columns: {required_cols}. Found: {list(df.columns)}")

    if "id" not in df.columns:
        df["id"] = [f"csv-{i}" for i in range(len(df))]
    if "type" not in df.columns:
        df["type"] = "expense"
    if "category" not in df.columns:
        df["category"] = "Other"
    if "account" not in df.columns:
        df["account"] = "Default"
    if "note" not in df.columns:
        df["note"] = ""
    if "tags" not in df.columns:
        df["tags"] = [[] for _ in range(len(df))]

    transactions = [
        Transaction(
            id=str(row["id"]),
            date=pd.to_datetime(row["date"]).date(),
            amount=abs(float(row["amount"])),
            type=TransactionType(row["type"].lower()) if row["type"].lower() in [t.value for t in TransactionType] else TransactionType.EXPENSE,
            category=str(row["category"]),
            account=str(row["account"]),
            note=str(row.get("note", "")),
            tags=row["tags"] if isinstance(row["tags"], list) else []
        )
        for _, row in df.iterrows()
    ]
    return transactions_to_df(transactions)


def load_dataset(source: Union[str, Path, BinaryIO, None] = None) -> pd.DataFrame:
    """Unified loader: loads from file if provided, otherwise returns realistic mock dataset."""
    if source is None:
        mock_txs = generate_mock_transactions(days=180)
        return transactions_to_df(mock_txs)

    if isinstance(source, (str, Path)):
        ext = Path(source).suffix.lower()
        if ext == ".json":
            return load_from_json(source)
        elif ext == ".csv":
            return load_from_csv(source)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    else:
        # Buffer upload (Streamlit UploadedFile)
        name = getattr(source, "name", "").lower()
        if name.endswith(".json"):
            return load_from_json(source)
        elif name.endswith(".csv"):
            return load_from_csv(source)
        else:
            # Try JSON first, then CSV
            try:
                return load_from_json(source)
            except Exception:
                source.seek(0)
                return load_from_csv(source)


def run_sql_query(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """Executes an in-memory DuckDB analytical SQL query over the transactions DataFrame."""
    con = duckdb.connect(database=":memory:")
    con.register("transactions", df)
    result = con.execute(query).df()
    con.close()
    return result
