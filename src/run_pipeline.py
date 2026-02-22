"""
run_pipeline.py
---------------
Master orchestrator. Run this to execute the full pipeline:
  1. Transform raw data → processed CSVs
  2. Build serving-layer outputs
  3. Generate dashboard HTML

Usage:
  python run_pipeline.py            # full pipeline (transform + serve + dashboard)
  python run_pipeline.py --stress   # also run Section C stress tests
"""

import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import data_transformation as transform
import serve
import dashboard

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def main(run_stress: bool = False):
    print("🚀 Starting full data pipeline...\n")

    # Clean processed output for a true full refresh
    if PROCESSED_DIR.exists():
        shutil.rmtree(PROCESSED_DIR)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1 — Transform
    transform.main()

    # Step 2 — Serve
    serve.PROCESSED_DIR = PROCESSED_DIR
    serve.REVIEWS_IN    = PROCESSED_DIR / "apps_reviews.csv"
    serve.APP_KPIS_OUT  = PROCESSED_DIR / "serving_app_kpis.csv"
    serve.DAILY_OUT     = PROCESSED_DIR / "serving_daily_metrics.csv"
    serve.main()

    # Step 3 — Dashboard
    dashboard.main()

    print("\n✅ Pipeline complete!")
    print(f"   Processed data : {PROCESSED_DIR}")
    print(f"   Dashboard      : {PROCESSED_DIR / 'dashboard.html'}")

    if run_stress:
        print("\n" + "─" * 50)
        import stress_test
        stress_test.main()


if __name__ == "__main__":
    run_stress = "--stress" in sys.argv
    main(run_stress=run_stress)