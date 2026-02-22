#!/usr/bin/env bash
# =============================================================================
# run_scd2.sh — Section E2: SCD Type 2 snapshot execution
# =============================================================================
# Usage:
#   bash run_scd2.sh
#
# What it does:
#   1. Runs the snap_dim_apps dbt snapshot (creates/updates historical records)
#   2. Builds the dim_apps_scd dimension model from the snapshot
#   3. Builds the fact_reviews_historical fact table (joins to SCD2 dim)
#
# To test SCD2:
#   1. Modify a category_name in data/raw/apps_metadata.json
#   2. Re-run: python ingest_to_duckdb.py
#   3. Run: dbt run --select staging --profiles-dir .
#   4. Run: bash run_scd2.sh
#   5. In DuckDB CLI, query: SELECT * FROM snapshots.snap_dim_apps
#      WHERE dbt_valid_to IS NOT NULL;  -- shows closed (old) versions
# =============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "========================================"
echo " E2 — SCD Type 2 Snapshot Run"
echo "========================================"

echo ""
echo "[1/3] Running snapshot (snap_dim_apps)..."
dbt snapshot --profiles-dir .

echo ""
echo "[2/3] Building dim_apps_scd from snapshot..."
dbt run --select dim_apps_scd --profiles-dir .

echo ""
echo "[3/3] Building fact_reviews_historical..."
dbt run --select fact_reviews_historical --profiles-dir .

echo ""
echo "========================================"
echo " ✅  SCD2 pipeline completed!"
echo ""
echo " To inspect versions:"
echo "   duckdb data/db/playstore.duckdb"
echo "   SELECT app_id, category_name, dbt_valid_from, dbt_valid_to, is_current"
echo "   FROM marts.dim_apps_scd"
echo "   ORDER BY app_id, dbt_valid_from;"
echo "========================================"
