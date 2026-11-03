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


def clean_sales(raw_sales):
    cleaned_sales = raw_sales.copy()
    cleaned_sales["region"] = (
        cleaned_sales["region"]
        .fillna("Unknown")
        .str.strip()
        .str.title()
    )
    cleaned_sales["category"] = (
        cleaned_sales["category"].str.strip().str.title()
    )
    cleaned_sales = cleaned_sales.drop_duplicates(
        subset=["order_id"], keep="first"
    )
    cleaned_sales = cleaned_sales.dropna(subset=CRITICAL_COLUMNS)
    cleaned_sales = cleaned_sales[
        (cleaned_sales["units"] > 0)
        & (cleaned_sales["unit_price"] > 0)
    ].copy()
    cleaned_sales["revenue"] = (
        cleaned_sales["units"] * cleaned_sales["unit_price"]
    )

    assert cleaned_sales["order_id"].is_unique
    assert cleaned_sales[CRITICAL_COLUMNS].notna().all().all()
    return cleaned_sales


def export_parquet(cleaned_sales):
    OUTPUT_DIR.mkdir(exist_ok=True)
    duckdb.sql(
        f"COPY (SELECT * FROM cleaned_sales) "
        f"TO '{PARQUET_FILE}' (FORMAT parquet)"
    )


def main():
    raw_sales = load_sales()
    inspect_data(raw_sales)

    naive_total = naive_report(raw_sales)
    print(f"Naive revenue total: ${naive_total:,.2f}")

    cleaned_sales = clean_sales(raw_sales)
    clean_total = cleaned_sales["revenue"].sum()
    print(f"Clean rows: {len(cleaned_sales)}")
    print(f"Clean revenue total: ${clean_total:,.2f}")

    export_parquet(cleaned_sales)
    print(f"\nSaved {PARQUET_FILE}")


if __name__ == "__main__":
    main()
