# 💳 WalletAnalyze

**WalletAnalyze** is an interactive, analytical frontend dashboard and financial intelligence platform built in Python. It provides automated cash flow metrics, category breakdowns, machine learning anomaly detection, and predictive spending forecasting for personal financial data—designed to connect with or ingest data from your JavaScript/Expo personal wallet app (**`mywallet`**).

---

## 🚀 Key Features

* **📊 Executive Financial Dashboard:** Instant calculation of Total Income, Total Outflow, Net Savings, Savings Rate, and Daily Burn Rate.
* **💸 Deep Category Drilldowns:** Proportional donut distribution and hierarchical treemap visualizations powered by **Plotly**.
* **📈 Predictive Trend Forecasting:** 7-day moving averages and **Scikit-Learn** linear regression models projecting spending trajectories 14–90 days out.
* **🚨 Machine Learning Anomaly Detection:** Category-conditioned **Isolation Forest** to automatically flag irregular expenses, unexpected charges, and budget spikes.
* **🔄 Seamless JS / Data Integration:** Drag-and-drop JSON/CSV uploader, data schema validation using **Pydantic**, and fast in-memory analytical SQL via **DuckDB**.

---

## 🛠️ Tech Stack

* **Environment & Package Manager:** [`uv`](https://docs.astral.sh/uv/) (blazing fast Python packaging)
* **Frontend UI & Dashboard:** [Streamlit](https://streamlit.io/)
* **Data Processing & Analytics:** [Pandas](https://pandas.pydata.org/) & [DuckDB](https://duckdb.org/)
* **Interactive Visualizations:** [Plotly](https://plotly.com/python/)
* **Machine Learning & Models:** [Scikit-Learn](https://scikit-learn.org/)
* **Data Validation & Schemas:** [Pydantic v2](https://docs.pydantic.dev/)
* **Testing:** [pytest](https://docs.pytest.org/)

---

## 📁 Project Architecture

```
wallet-analyze/
├── pyproject.toml              # Dependencies and project metadata (managed by uv)
├── .python-version             # Python version (3.12)
├── README.md                   # Project documentation
├── config/
│   ├── __init__.py
│   └── settings.py             # Global configurations, currency, color schemes
├── src/
│   ├── app.py                  # Main Streamlit entrypoint & overview dashboard
│   ├── data/
│   │   ├── schema.py           # Pydantic data models (Transaction, TransactionType)
│   │   ├── generator.py        # Realistic synthetic transaction generator
│   │   └── loader.py           # Ingestion from JSON/CSV & DuckDB querying
│   ├── analytics/
│   │   ├── metrics.py          # KPIs, category summaries, monthly cash flow
│   │   ├── anomaly.py          # Isolation Forest ML anomaly detector
│   │   └── forecasting.py      # Linear Regression trend forecasting
│   ├── components/
│   │   ├── charts.py           # Interactive Plotly chart builders
│   │   └── ui.py               # Sidebar filters and metric display cards
│   └── pages/
│       ├── 1_💸_Expenses.py    # Category breakdowns & treemap
│       ├── 2_📈_Trends_&_Forecast.py # Spending trajectories & projections
│       ├── 3_🚨_Anomaly_Detection.py # ML outlier detection & explanation
│       └── 4_🔄_Data_Sync.py   # Upload & JS integration hub
└── tests/
    └── test_analytics.py       # Automated unit tests
```

---

## ⚡ Quick Start

### 1. Prerequisites
Ensure you have [`uv`](https://docs.astral.sh/uv/) installed:
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Launch the Application
Run the Streamlit app using `uv`:
```bash
uv run streamlit run src/app.py
```
The application will launch in your browser at `http://localhost:8501`.

### 3. Run Automated Tests
```bash
uv run pytest
```

---

## 🔌 Integrating with `mywallet` (JS / React Native)

### Option A: JSON Export & File Upload (Zero-Config)
In `mywallet`, export transactions formatted as:
```json
{
  "transactions": [
    {
      "id": "tx_001",
      "date": "2026-11-15",
      "amount": 45.50,
      "type": "expense",
      "category": "Groceries",
      "account": "Credit Card",
      "note": "Supermarket essentials",
      "tags": ["food"]
    }
  ]
}
```
Navigate to the **🔄 Data Sync** tab in the dashboard and drag-and-drop the JSON file.

### Option B: Shared Database (Supabase / PostgreSQL)
Both apps can connect to a shared PostgreSQL / Supabase instance:
- `mywallet` writes daily transactions using `@supabase/supabase-js`.
- `wallet-analyze` reads data using `SQLAlchemy` or `supabase-py` for live analytical reporting.
