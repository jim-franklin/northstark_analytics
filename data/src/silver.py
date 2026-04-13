"""
silver.py

Function:
  Read from Bronze Parquet tables, apply all business logic and
  data quality fixes using PySpark SQL, and write cleaned,
  metrics-ready tables to data/silver/.
"""

import os
from pathlib import Path
from pyspark.sql import SparkSession

# Begin spark session
spark = SparkSession.builder.appName("NorthStack_Silver_Transformations").getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Define data paths

BASE_DIR = Path("__file__").resolve().parent
BRONZE_DIR = BASE_DIR / "data" / "bronze"
SILVER_DIR = BASE_DIR / "data" / "silver"

# Load bronze tables
spark.read.parquet(
    os.path.join(BRONZE_DIR, "bronze_crm_customers")
).createOrReplaceTempView("bronze_crm_customers")

spark.read.parquet(
    os.path.join(BRONZE_DIR, "bronze_billing_transactions")
).createOrReplaceTempView("bronze_billing_transactions")

spark.read.parquet(os.path.join(BRONZE_DIR, "bronze_churn")).createOrReplaceTempView(
    "bronze_churn"
)

print("\n\n\n...\n")
print("Bronze tables loaded.\n")


# Problem 1:
#   CRM uses customer_id format CUST-001.
#   Billing uses customer_id format C001.
#   These refer to the same customer but cannot be joined as-is.
#
# Fix:
#   Standardize billing customer_id by replacing 'C' with 'CUST-'
#   using REGEXP_REPLACE. Then LEFT JOIN CRM onto billing so we
#   capture all paying customers, including the 10 who exist in
#   billing but not in CRM.
#
# Assumption:
#   CUST-001 (CRM) and C001 (billing) are the same entity.
#   The numeric suffix is the shared natural key.
#
# Primary key: customer_id

print("Building silver_crm_customers...")

silver_customers = spark.sql("""
    WITH billing_ids_standardized AS (
        -- Standardize billing customer_id from C001 to CUST-001 format
        -- so it can be joined to the CRM on a common key
        SELECT DISTINCT
            REGEXP_REPLACE(customer_id, '^C', 'CUST-') AS customer_id,
            plan
        FROM bronze_billing_transactions
    ),

    crm_cleaned AS (
        -- Normalize pipeline stages using CASE WHEN
        -- Assumption: null stages treated as Lead (earliest funnel stage)
        SELECT
            customer_id,
            company_name,
            industry,
            city,
            plan,
            signup_date,
            account_manager,
            CASE
                WHEN LOWER(pipeline_stage) IN ('closed_won', 'won')  THEN 'Closed Won'
                WHEN LOWER(pipeline_stage) = 'closed_lost'           THEN 'Closed Lost'
                WHEN LOWER(pipeline_stage) = 'qualified'             THEN 'Qualified'
                WHEN LOWER(pipeline_stage) = 'proposal'              THEN 'Proposal'
                WHEN LOWER(pipeline_stage) = 'demo'                  THEN 'Demo'
                WHEN LOWER(pipeline_stage) = 'lead'                  THEN 'Lead'
                WHEN pipeline_stage IS NULL                          THEN 'Lead'
                ELSE pipeline_stage
            END AS pipeline_stage
        FROM bronze_crm_customers
    )

    -- LEFT JOIN from billing to CRM so we keep all paying customers.
    -- 10 customers exist in billing but not in CRM — they appear here
    -- with NULL for CRM fields and are flagged for client review.
    SELECT
        b.customer_id,
        c.company_name,
        c.industry,
        c.city,
        COALESCE(c.plan, b.plan)        AS plan,
        c.signup_date,
        c.account_manager,
        c.pipeline_stage,
        CASE
            WHEN c.customer_id IS NULL THEN TRUE
            ELSE FALSE
        END                             AS billing_only_flag
    FROM billing_ids_standardized b
    LEFT JOIN crm_cleaned c
        ON b.customer_id = c.customer_id
""")

silver_customers.write.mode("overwrite").parquet(
    os.path.join(SILVER_DIR, "silver_crm_customers")
)
silver_customers.createOrReplaceTempView("silver_crm_customers")
print(f"  Rows: {silver_customers.count()}")
print(
    f"  Billing-only customers (not in CRM): {silver_customers.filter('billing_only_flag = true').count()}"
)


# Problems 2:
#   a. Duplicate rows exist in billing (same transaction_id,
#      same amount, same date — system-level duplicates).
#   b. Refunds are stored as postive-amount rows with status='refunded'.
#      These must be excluded from revenue calculations.
#
# Fix:
#   Use ROW_NUMBER() window function partitioned by transaction_id
#   to tag duplicates. Keep only row_num = 1.
#   Then filter WHERE status = 'paid' to exclude refunds.
#
# Assumption:
#   Revenue = paid transactions only. Refunds represent money returned
#   to customers and should not count toward revenue.
#
# Foreign key: customer_id

print("\nBuilding silver_billing_transactions...")

silver_transactions = spark.sql("""
    WITH billing_ids_standardized AS (
        -- Standardize customer_id format to match silver_customers PK
        SELECT
            transaction_id,
            REGEXP_REPLACE(customer_id, '^C', 'CUST-') AS customer_id,
            amount,
            transaction_date,
            status,
            plan
        FROM bronze_billing_transactions
    ),

    deduped AS (
        -- Use ROW_NUMBER() to identify duplicates.
        -- Partition by transaction_id — a transaction_id should be unique.
        -- Any row_num > 1 is a duplicate and gets filtered out below.
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY transaction_id
                ORDER BY transaction_date
            ) AS row_num
        FROM billing_ids_standardized
    ),

    no_duplicates AS (
        SELECT
            transaction_id,
            customer_id,
            amount,
            transaction_date,
            status,
            plan
        FROM deduped
        WHERE row_num = 1
    )

    -- Final filter: paid transactions only.
    -- Excludes refunded rows (status = 'refunded').
    SELECT *
    FROM no_duplicates
    WHERE status = 'paid'
""")

silver_transactions.write.mode("overwrite").parquet(
    os.path.join(SILVER_DIR, "silver_billing_transactions")
)
silver_transactions.createOrReplaceTempView("silver_billing_transactions")
print(f"  Rows after dedup and refund exclusion: {silver_transactions.count()}")


print("\nBuilding silver_churn...")

silver_churn = spark.sql("""
    SELECT *
    FROM bronze_churn
""")

silver_churn.write.mode("overwrite").parquet(os.path.join(SILVER_DIR, "silver_churn"))

print(f"  Rows: {silver_churn.count()}")

print("\nSilver transformation complete...")
spark.stop()
