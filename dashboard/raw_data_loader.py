"""
raw_data_loader.py
Loads raw CSV files with no cleaning applied.
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

crm_raw = pd.read_csv(os.path.join(RAW_DIR, "crm_customers.csv"))
billing_raw = pd.read_csv(os.path.join(RAW_DIR, "billing_transactions.csv"))
churn_raw = pd.read_csv(os.path.join(RAW_DIR, "churn_data.csv"))

# Minimal parse so charts can render — no cleaning, just type coercion
billing_raw["transaction_date"] = pd.to_datetime(
    billing_raw["transaction_date"], errors="coerce"
)
billing_raw["month"] = billing_raw["transaction_date"].dt.to_period("M").astype(str)
