
# Trusted Sales Data Pipeline

This Python-based data pipeline transforms messy transactional sales records into validated, high-quality data. It ensures absolute data consistency and automatically outputs structured analysis reports and regional visualizations.

## Pipeline Architecture & Process
1. **Load Raw Data**: Imports messy transaction records from a local CSV.
2. **Data Cleaning & Validation**:
   - Handles missing region and category values by standardizing text format to Title Case.
   - Filters out duplicate orders by `order_id` (retaining the first occurrence).
   - Drops rows with missing critical values (e.g., date, units, price).
   - Validates that `units` and `unit_price` are greater than zero.
   - Computes a calculated `revenue` column.
   - Runs automated data assertions to guarantee data integrity before exporting.
3. **Optimized Export**: Saves the trusted dataset to the highly optimized, columnar Parquet format.
4. **Analytical Queries**: Uses **DuckDB** and SQL to query the Parquet data and generate a regional revenue summary.
5. **Visualization**: Generates a bar chart using **Matplotlib** to display regional performance.

## Tech Stack
- **Language**: Python 3.11+
- **Data Processing**: pandas
- **SQL Query Engine**: DuckDB
- **Visualization**: Matplotlib
- **Source Control**: Git & GitHub

## Project Structure
```text
├── data/                  # Raw input datasets (ignored by Git)
├── output/                # Cleaned datasets, CSV reports, and charts (ignored by Git)
├── .gitignore             # Version control exclusions
├── pipeline.py            # Main pipeline source code
├── requirements.txt       # Pinned library dependencies
└── README.md              # Project documentation
```

## Setup Instructions

### Prerequisites
Make sure you have Python 3.11 or higher installed on your computer.

### 1. Clone the Repository
```bash
git clone 
cd messy-sales-pipeline
```

### 2. Create and Activate Virtual Environment
For Windows (PowerShell):
```powershell
py -3 -m venv .venv
```

### 3. Install Pinned Dependencies
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Run the Pipeline
Execute the pipeline script to clean the source data, export the database, and generate the regional revenue reports and charts:
```powershell
.\.venv\Scripts\python.exe pipeline.py
```

## Outputs Generated
Upon a successful run, the following files are populated in your local `output/` directory:
- `clean_sales.parquet`: The validated, cleaned columnar master dataset.
- `regional_revenue.csv`: Summary of revenue sorted from highest to lowest by region.
- `regional_revenue.png`: A clean bar chart visual representing regional revenue performance.
