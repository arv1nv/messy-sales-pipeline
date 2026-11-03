from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd

DATA_FILE = "data/sales.csv"
OUTPUT_DIR = Path("output")
PARQUET_FILE = "output/clean_sales.parquet"
SUMMARY_FILE = "output/regional_revenue.csv"
CHART_FILE = "output/regional_revenue.png"
CRITICAL_COLUMNS = [
    "order_id",
    "order_date",
    "category",
    "units",
    "unit_price",
]


def load_sales():
    raw_sales = pd.read_csv(DATA_FILE)
    raw_sales["order_date"] = pd.to_datetime(
        raw_sales["order_date"], errors="coerce"
    )
    return raw_sales


def inspect_data(raw_sales):
    print("\nFirst five rows:")
    print(raw_sales.head())
    print("\nMissing values by column:")
    print(raw_sales.isna().sum())
    duplicate_count = raw_sales.duplicated(
        subset=["order_id"], keep="first"
    ).sum()
    incomplete_count = raw_sales[CRITICAL_COLUMNS].isna().any(axis=1).sum()
    print(f"\nRaw rows: {len(raw_sales)}")
    print(f"Duplicate order IDs: {duplicate_count}")
    print(f"Rows missing critical values: {incomplete_count}")


def naive_report(raw_sales):
    naive_sales = raw_sales.copy()
    naive_sales["revenue"] = (
        naive_sales["units"] * naive_sales["unit_price"]
    )
    return naive_sales["revenue"].sum()


def main():
    raw_sales = load_sales()
    inspect_data(raw_sales)

    naive_total = naive_report(raw_sales)
    print(f"Naive revenue total: ${naive_total:,.2f}")


if __name__ == "__main__":
    main()