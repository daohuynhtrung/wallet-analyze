"""Configuration settings for wallet-analyze."""
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

class Settings(BaseModel):
    app_name: str = "WalletAnalyze"
    app_subtitle: str = "Personal Financial Analytics & Intelligence"
    currency_symbol: str = "$"
    date_format: str = "%Y-%m-%d"
    default_lookback_days: int = 180
    
    # Category color palette for consistent Plotly styling
    category_colors: dict[str, str] = {
        "Salary": "#2ecc71",
        "Freelance": "#27ae60",
        "Investments": "#1abc9c",
        "Housing": "#e74c3c",
        "Groceries": "#f39c12",
        "Dining Out": "#e67e22",
        "Transportation": "#3498db",
        "Utilities": "#9b59b6",
        "Entertainment": "#16a085",
        "Subscriptions": "#d35400",
        "Healthcare": "#c0392b",
        "Shopping": "#8e44ad",
        "Other": "#7f8c8d"
    }

settings = Settings()
