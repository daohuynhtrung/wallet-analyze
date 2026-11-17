"""Data Synchronization & JS Integration Page."""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import streamlit as st
import pandas as pd
from src.data.loader import load_dataset, load_from_json, load_from_csv
from src.data.generator import generate_mock_transactions
from src.data.schema import transactions_to_df

st.set_page_config(page_title="Data Sync - WalletAnalyze", page_icon="🔄", layout="wide")

st.title("🔄 Data Synchronization & JS Integration")
st.markdown("Import data from your **`mywallet`** JS/Expo application or connect an external data pipeline.")

tab_upload, tab_schema, tab_api = st.tabs(["📤 Upload File", "📑 JSON Contract & Schema", "🔌 Direct API / DB Sync"])

with tab_upload:
    st.subheader("Upload Transactions Export (JSON or CSV)")
    uploaded_file = st.file_uploader(
        "Choose a JSON or CSV file exported from your wallet app",
        type=["json", "csv"]
    )

    if uploaded_file is not None:
        try:
            new_df = load_dataset(uploaded_file)
            st.success(f"✅ Successfully parsed {len(new_df):,} transactions from `{uploaded_file.name}`!")

            st.write("Preview of parsed data:")
            st.dataframe(
                new_df.head(5)[["id", "date", "category", "account", "type", "amount", "note"]],
                use_container_width=True,
                hide_index=True
            )

            if st.button("🚀 Load into Active Dashboard", type="primary"):
                st.session_state["transactions_df"] = new_df
                st.session_state["data_source"] = f"Uploaded File: {uploaded_file.name}"
                st.success("Dashboard data updated! Navigate to Overview or Expenses to view.")
        except Exception as e:
            st.error(f"❌ Failed to parse file: {str(e)}")

    st.markdown("---")
    st.subheader("🔁 Reset to Demo Data")
    if st.button("Restore Default Synthetic Dataset (180 days)"):
        st.session_state["transactions_df"] = transactions_to_df(generate_mock_transactions(180))
        st.session_state["data_source"] = "Synthetic Mock Dataset (180 days)"
        st.info("Reset to default mock transactions.")

with tab_schema:
    st.subheader("Expected JSON Format for `mywallet` Export")
    st.markdown("""
To integrate seamlessly with `wallet-analyze`, format your `mywallet` JavaScript export as follows:
    """)

    sample_contract = {
        "transactions": [
            {
                "id": "tx_001",
                "date": "2026-11-15",
                "amount": 45.50,
                "type": "expense",
                "category": "Groceries",
                "account": "Credit Card",
                "note": "Supermarket essentials",
                "tags": ["groceries", "food"]
            },
            {
                "id": "tx_002",
                "date": "2026-11-15",
                "amount": 2850.00,
                "type": "income",
                "category": "Salary",
                "account": "Main Checking",
                "note": "Bi-weekly paycheck",
                "tags": ["payroll"]
            }
        ]
    }
    st.json(sample_contract)

    # Provide download button for template
    st.download_button(
        label="📥 Download Sample JSON Template",
        data=json.dumps(sample_contract, indent=2),
        file_name="wallet_export_template.json",
        mime="application/json"
    )

with tab_api:
    st.subheader("🔌 Connecting `mywallet` (Expo / React Native) Directly")
    st.markdown("""
### Integration Patterns:
1. **Option 1: Shared Cloud Database (Supabase / PostgreSQL)**
   * In `mywallet`: Save transactions using `@supabase/supabase-js`.
   * In `wallet-analyze`: Query Supabase tables using Python's `supabase-py` or `SQLAlchemy` connector.
2. **Option 2: Direct Local File Export**
   * In `mywallet`: Use `expo-file-system` / `expo-sharing` to generate a `.json` backup file.
   * In `wallet-analyze`: Upload the file using the tab above.
3. **Option 3: Local REST API Server**
   * Run a lightweight **FastAPI** daemon in `wallet-analyze` (`/api/transactions`) that `mywallet` can send POST requests to directly over local WiFi or localhost.
    """)
