"""
data_loader.py

Loads Silver Parquet tables once at startup.
All other dashboard modules import from here.
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SILVER_DIR = os.path.join(BASE_DIR, "data", "silver")
BRONZE_DIR = os.path.join(BASE_DIR, "data", "bronze")

customers = pd.read_parquet(os.path.join(SILVER_DIR, "silver_crm_customers"))
transactions = pd.read_parquet(os.path.join(SILVER_DIR, "silver_billing_transactions"))
churn = pd.read_parquet(os.path.join(BRONZE_DIR, "bronze_churn"))

# Shared derived columns used across components
transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"])
transactions["month"] = transactions["transaction_date"].dt.to_period("M").astype(str)

PLANS = sorted(transactions["plan"].unique().tolist())
DATE_MIN = transactions["transaction_date"].min()
DATE_MAX = transactions["transaction_date"].max()
INDUSTRIES = sorted(customers["industry"].dropna().unique().tolist())
