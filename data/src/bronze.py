"""
bronze.py

Function:
  Load raw CSV files from data/raw/, resolve date format inconsistencies
  using PySpark, and write the results as Parquet to data/bronze/.

  No business logic is applied here. Bronze is the audit trail.
  It reflects exactly what came in from each source system,
  with only the minimum parsing needed for Spark to work with the data.

Data sources:
  - crm_customers.csv
  - billing_transactions.csv
  - churn_data.csv

Primary keys:
  - crm_customers:        customer_id  (format: CUST-001)
  - billing_transactions: transaction_id
  - churn_data:           customer_id  (format: CUST-001)

Note:
  billing_transactions uses a different customer_id format (C001).
  This is a known issue documented here. Reconciliation happens in Silver.
"""

import os
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import coalesce, to_date, col, expr

# begin spark session
spark = SparkSession.builder.appName("NorthStack_Bronze_Ingestion").getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

BASE_DIR = Path("__file__").resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
BRONZE_DIR = BASE_DIR / "data" / "bronze"


# Ingest crm data
print("\n\n\n...\n")
print("Ingesting CRM customers...")

crm_raw = spark.read.csv(
    os.path.join(RAW_DIR, "crm_customers.csv"), header=True, inferSchema=True
)

# signup_date in crm data has two formats mixed in the same column:
#  - YYYY-MM-DD  (e.g. 2024-03-15)
#  - DD/MM/YYYY  (e.g. 15/03/2024)

print("Standardizing date format...")

crm_bronze = crm_raw.withColumn(
    "signup_date",
    coalesce(
        expr("try_to_date(signup_date, 'yyyy-MM-dd')"),
        expr("try_to_date(signup_date, 'dd/MM/yyyy')"),
    ),
)

crm_bronze.write.mode("overwrite").parquet(
    os.path.join(BRONZE_DIR, "bronze_crm_customers")
)

print(f"  Rows written: {crm_bronze.count()}")
print(
    f"  Null signup_dates after parse: {crm_bronze.filter(col('signup_date').isNull()).count()}"
)
crm_bronze.printSchema()

# Ingest billing data

print("\nIngesting billing transactions...")

billing_raw = spark.read.csv(
    os.path.join(RAW_DIR, "billing_transactions.csv"), header=True, inferSchema=True
)

billing_bronze = billing_raw.withColumn(
    "transaction_date", to_date(col("transaction_date"), "yyyy-MM-dd")
)

billing_bronze.write.mode("overwrite").parquet(
    os.path.join(BRONZE_DIR, "bronze_billing_transactions")
)

print(f"  Rows: {billing_bronze.count()}")
billing_bronze.printSchema()

# Ingest churn data
print("\nIngesting churn data...")

churn_raw = spark.read.csv(
    os.path.join(RAW_DIR, "churn_data.csv"), header=True, inferSchema=True
)

churn_bronze = churn_raw.withColumn(
    "churn_date", to_date(col("churn_date"), "yyyy-MM-dd")
)

churn_bronze.write.mode("overwrite").parquet(os.path.join(BRONZE_DIR, "bronze_churn"))

print(f"  Rows: {churn_bronze.count()}")
churn_bronze.printSchema()

# register as temp view for validation
crm_bronze.createOrReplaceTempView("bronze_crm_customers")
billing_bronze.createOrReplaceTempView("bronze_billing_transactions")
churn_bronze.createOrReplaceTempView("bronze_churn")

print("\nBronze layer validation...")
spark.sql("""
    SELECT
        COUNT(*)                                         AS total_rows,
        COUNT(DISTINCT customer_id)                      AS unique_customers,
        SUM(CASE WHEN signup_date IS NULL THEN 1 ELSE 0 END) AS null_dates,
        SUM(CASE WHEN pipeline_stage IS NULL THEN 1 ELSE 0 END) AS null_stages
    FROM bronze_crm_customers
""").show()

spark.sql("""
    SELECT
        COUNT(*)                        AS total_rows,
        COUNT(DISTINCT transaction_id)  AS unique_transactions,
        COUNT(DISTINCT customer_id)     AS unique_customers,
        SUM(amount)                     AS gross_amount_incl_refunds
    FROM bronze_billing_transactions
""").show()

print("Bronze ingestion complete...\n")
spark.stop()
