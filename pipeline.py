from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd

DATA_FILE = "data/sales.csv"
OUTPUT_DIR = Path("output")
PARQUET_FILE = "output/clean_sales.parquet"
CRITICAL_COLUMNS = [
    "order_id",
    "order_date",
    "category",
    "units",
    "unit_price",
]
APPROVED_DIMENSIONS = {"region", "category"}


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


def query_revenue_by(dimension):
    if dimension not in APPROVED_DIMENSIONS:
        raise ValueError(f"Unsupported dimension: {dimension}")

    report = duckdb.sql(
        f"""
        SELECT {dimension}, ROUND(SUM(revenue), 2) AS revenue
        FROM '{PARQUET_FILE}'
        GROUP BY {dimension}
        ORDER BY revenue DESC
        """
    ).df()
    report_file = OUTPUT_DIR / f"{dimension}_revenue.csv"
    report.to_csv(report_file, index=False)
    return report, report_file


def save_bar_chart(report, dimension):
    chart_file = OUTPUT_DIR / f"{dimension}_revenue.png"
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(
        report[dimension],
        report["revenue"],
        color="#4C78A8",
    )
    ax.set(
        title=f"Trusted Revenue by {dimension.title()}",
        xlabel=dimension.title(),
        ylabel="Revenue ($)",
    )
    fig.savefig(chart_file, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return chart_file


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

    for dimension in ("region", "category"):
        report, report_file = query_revenue_by(dimension)
        chart_file = save_bar_chart(report, dimension)
        print(f"\nRevenue by {dimension}:")
        print(report.to_string(index=False))
        print(f"Saved {report_file}")
        print(f"Saved {chart_file}")

    print(f"\nSaved {PARQUET_FILE}")


if __name__ == "__main__":
    main()