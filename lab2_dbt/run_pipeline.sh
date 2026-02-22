#!/usr/bin/env bash
# =============================================================================
# run_pipeline.sh — Full pipeline execution script for Lab 2
# =============================================================================
# Usage:
#   bash run_pipeline.sh              # full refresh
#   bash run_pipeline.sh --incremental  # incremental fact run
# =============================================================================

set -e  # Exit immediately on error

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "========================================"
echo " Lab 2 — dbt + DuckDB Pipeline"
echo "========================================"

# --- Step 0: Install dbt packages (dependencies) ----
echo ""
echo "[0/5] Installing dbt dependencies..."
dbt deps --profiles-dir .

# --- Step 1: Python ingestion (Lab 1 code reuse) ---------------------------
echo ""
echo "[1/5] Running Python ingestion to DuckDB..."
python ingest_to_duckdb.py

# --- Step 2: dbt debug (connection check) ----------------------------------
echo ""
echo "[2/5] Verifying dbt connection..."
dbt debug --profiles-dir .

# --- Step 3: Run staging models --------------------------------------------
echo ""
echo "[3/5] Building staging layer..."
dbt run --select staging --profiles-dir .

# --- Step 3.5: Run snapshots (SCD Type 2 source) ---------------------------
echo ""
echo "[3.5/5] Creating snapshots..."
dbt snapshot --profiles-dir .

# --- Step 4: Run dimensional models ----------------------------------------
echo ""
echo "[4/5] Building dimension tables..."
dbt run --select marts.dimensions --profiles-dir .

# --- Step 5: Run fact table ------------------------------------------------
echo ""
if [ "$1" == "--incremental" ]; then
    echo "[5/5] Building fact table (INCREMENTAL)..."
    dbt run --select fact_reviews_incremental --profiles-dir .
else
    echo "[5/5] Building fact table (FULL REFRESH)..."
    dbt run --select fact_reviews --profiles-dir .
fi

# --- Step 6: Run all dbt tests ---------------------------------------------
echo ""
echo "[6/5] Running dbt tests..."
dbt test --profiles-dir .

echo ""
echo "========================================"
echo " ✅  Pipeline completed successfully!"
echo "========================================"
echo " DuckDB file: data/db/playstore.duckdb"
echo " Connect with: duckdb data/db/playstore.duckdb"
echo "========================================"
