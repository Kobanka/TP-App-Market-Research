# App Market Research - Data Engineering Pipeline

A complete data engineering pipeline for collecting, transforming, and analyzing Google Play Store app data. This project includes two labs:

- **Lab 1**: Python-based ETL pipeline with Pandas and Plotly
- **Lab 2**: dbt + DuckDB dimensional modeling and analytics

## 📋 Project Overview

### Lab 1: Python ETL Pipeline

1. **Data Generation**: Scrape Google Play Store for app metadata and reviews
2. **Data Transformation**: Clean and structure raw data into analytics-ready formats
3. **Data Serving**: Calculate KPIs and metrics for visualization
4. **Dashboard**: Generate interactive visualizations using Plotly

### Lab 2: dbt + DuckDB Analytics

1. **Staging Layer**: Normalized views with data quality tests
2. **Dimensional Modeling**: Kimball-style star schema (dims + fact tables)
3. **SCD Type 2**: Historical tracking of app attribute changes
4. **Incremental Loading**: Efficient fact table updates

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kobanka/TP-App-Market-Research.git
   cd "TP-App-Market-Research"
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv dataApps
   ```

3. **Activate the virtual environment**
   
   On Linux/Mac:
   ```bash
   source dataApps/bin/activate
   ```
   
   On Windows:
   ```bash
   dataApps\Scripts\activate
   ```

4. **Install Lab 1 dependencies**
   ```bash
   pip install google-play-scraper pandas plotly
   ```

5. **Install Lab 2 dependencies** (if running Lab 2)
   ```bash
   cd lab2_dbt
   pip install -r requirements.txt
   ```

---

## 📊 Lab 1: Python ETL Pipeline

Run each stage in order from the project root directory:

### Step 1: Generate Raw Data

Scrapes Google Play Store for AI note-taking apps and their reviews:

```bash
python src/data_generation.py
```

**Output**: 
- `data/raw/apps_metadata.json` - App details (title, developer, ratings, installs, etc.)
- `data/raw/apps_reviews.json` - User reviews with ratings and timestamps

### Step 2: Transform Data

Cleans and structures the raw data into CSV format:

```bash
python src/data_transformation.py
```

**Output**:
- `data/processed/apps_metadata.csv` - Cleaned app catalog
- `data/processed/apps_reviews.csv` - Structured review data

### Running the Full Pipeline

Execute all stages (Transform → Serve → Dashboard):

```bash
python src/run_pipeline.py
```

Add `--stress` flag to run chaos engineering stress tests:

```bash
python src/run_pipeline.py --stress
```

### View the Dashboard

Start a local web server to view the interactive dashboard:

```bash
cd data/processed
python -m http.server 8000
```

Then open your browser and navigate to:
```
http://localhost:8000/dashboard.html
```

Press `Ctrl+C` in the terminal to stop the server when done.

---

## 🗄️ Lab 2: dbt + DuckDB Analytics

### Architecture

**Section A — Configuration:**
- `dbt_project.yml` — Project config with materialization conventions (staging=view, marts=table)
- `profiles.yml` — DuckDB connection profile
- `ingest_to_duckdb.py` — Python bridge loading Lab 1 JSON files into DuckDB's raw schema
- `packages.yml` — dbt dependencies (dbt_utils)

**Section B+C — Data Modeling:**
- Kimball Bus Matrix with Star/Snowflake schema design
- `dim_apps` → `dim_categories` hierarchy
- `dim_developers`, `dim_date` (YYYYMMDD integer key)
- `fact_reviews` with 4 FK joins and derived measures

**Section D — Full dbt Pipeline:**
- **Staging**: `stg_playstore_apps.sql`, `stg_playstore_reviews.sql` with data quality tests
- **Dimensions**: `dim_developers`, `dim_categories`, `dim_apps`, `dim_date` with referential integrity tests
- **Facts**: `fact_reviews.sql` with foreign key joins
- `run_pipeline.sh` — One-command pipeline execution

**Section E — Chaos Engineering:**
- `fact_reviews_incremental.sql` — Incremental model with `unique_key=review_id`
- `snapshots/snap_dim_apps.sql` — SCD Type 2 snapshot using CHECK strategy
- `dim_apps_scd.sql` — Historized dimension with `is_current`, `dbt_valid_from/to`
- `fact_reviews_historical.sql` — Temporal join to SCD2 dimension
- `run_scd2.sh` — Helper script for snapshot + SCD2 workflow

### Running Lab 2

1. **Navigate to Lab 2 directory**
   ```bash
   cd lab2_dbt
   ```

2. **Copy raw data from Lab 1** (if not already present)
   ```bash
   cp -r ../data/raw ./data/
   ```

3. **Ingest data to DuckDB**
   ```bash
   python ingest_to_duckdb.py
   ```

4. **Run the full pipeline**
   ```bash
   bash run_pipeline.sh
   ```
   
   For incremental fact table updates:
   ```bash
   bash run_pipeline.sh --incremental
   ```

5. **Run SCD Type 2 workflow**
   ```bash
   bash run_scd2.sh
   ```

6. **Query the DuckDB database**
   ```bash
   duckdb data/db/playstore.duckdb
   ```

---

## 📁 Project Structure

```
App Market Research/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                  # Scraped JSON data (Lab 1 output)
│   └── processed/            # Transformed CSV + dashboard (Lab 1)
│       └── stress_test/      # Stress test outputs (Lab 1)
├── reference-data-prof/      # Stress test input files (Lab 1)
├── dataApps/                 # Virtual environment (after setup)
├── src/                      # Lab 1 Python ETL scripts
│   ├── data_generation.py
│   ├── data_transformation.py
│   ├── serve.py
│   ├── dashboard.py
│   ├── run_pipeline.py
│   └── stress_test.py
└── lab2_dbt/                 # Lab 2: dbt + DuckDB
    ├── dbt_project.yml
    ├── profiles.yml
    ├── packages.yml
    ├── requirements.txt
    ├── ingest_to_duckdb.py
    ├── run_pipeline.sh
    ├── run_scd2.sh
    ├── data/
    │   ├── raw/              # Raw JSON (copied from Lab 1 or generated)
    │   └── db/               # DuckDB database file
    ├── models/
    │   ├── staging/          # Normalized views with tests
    │   ├── marts/
    │   │   ├── dimensions/   # dim_* tables
    │   │   └── facts/        # fact_* tables
    │   └── sources.yml
    ├── snapshots/            # SCD Type 2 snapshots
    ├── macros/               # Custom dbt macros
    └── tests/                # Custom data tests
```

---

## 📈 Lab 1 Dashboard Features

The generated dashboard includes:

1. **App Performance Chart**: Top/bottom apps by average rating
2. **Rating Trend Over Time**: 7-day rolling average
3. **Review Volume vs Rating**: Bubble chart with low-rating percentage
4. **Weekly Review Volume**: Bar chart with time slider

---

## 🧪 Lab 1 Stress Tests

The pipeline includes 5 chaos engineering scenarios (Section C):

- **C1**: New reviews batch with duplicates
- **C2**: Schema drift (column name variations)
- **C3**: Dirty data (invalid scores, malformed timestamps)
- **C4**: Updated app metadata with duplicates
- **C5**: Sentiment contradiction detection (business logic)

Run with:
```bash
python src/run_pipeline.py --stress
```

---

## 🔧 Customization

### Lab 1
- **Change search query**: Edit the `query` variable in `data_generation.py`
- **Adjust review count**: Modify the `max_reviews` parameter in `fetch_app_reviews()`
- **Filter thresholds**: Update minimum review count in dashboard charts

### Lab 2
- **Modify dimensions**: Edit models in `models/marts/dimensions/`
- **Add custom tests**: Create SQL files in `tests/`
- **Adjust incremental logic**: Update `fact_reviews_incremental.sql`
- **Change SCD strategy**: Modify `snapshots/snap_dim_apps.sql`

---

## 🛠️ Troubleshooting

### Lab 1

**Import errors**: Make sure your virtual environment is activated and dependencies are installed:
```bash
pip install google-play-scraper pandas plotly
```

**Path errors**: Always run scripts from the `App Market Research` directory

**Empty data**: The scraper may return different results based on Google Play availability. Check that `data/raw/` contains JSON files with data.

### Lab 2

**dbt connection errors**: Verify `profiles.yml` is in the `lab2_dbt/` directory

**Missing dbt_utils**: Run `dbt deps --profiles-dir .` to install packages

**DuckDB file locked**: Close any open DuckDB connections before running the pipeline

**Snapshot errors**: Ensure staging models run successfully before creating snapshots

---

## 📝 Notes

### Lab 1
- The scraper uses the `google-play-scraper` library (unofficial API)
- Review data availability depends on Google Play Store's current state
- Stress tests validate pipeline robustness against schema drift and dirty data

### Lab 2
- DuckDB database file: `lab2_dbt/data/db/playstore.duckdb`
- Snapshots track changes over time using dbt's SCD Type 2 implementation
- Incremental models optimize performance for large fact tables
- All models include comprehensive data quality tests

---

## 📄 License

This project is for educational purposes as part of a Data Engineering workshop.
