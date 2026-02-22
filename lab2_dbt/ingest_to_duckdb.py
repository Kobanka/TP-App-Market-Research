"""
ingest_to_duckdb.py
-------------------
Reads the raw JSON files produced by Lab 1 and loads them into DuckDB as
raw tables so that dbt can reference them via the source() macro.

Usage:
    python ingest_to_duckdb.py
"""

import json
import duckdb
import os

RAW_DIR  = os.path.join(os.path.dirname(__file__), "data", "raw")
DB_PATH  = os.path.join(os.path.dirname(__file__), "data", "db", "playstore.duckdb")
APPS_FILE    = os.path.join(RAW_DIR, "apps_metadata.json")
REVIEWS_FILE = os.path.join(RAW_DIR, "apps_reviews.json")   # dict keyed by appId


def load_apps(con: duckdb.DuckDBPyConnection) -> int:
    with open(APPS_FILE, "r", encoding="utf-8") as f:
        apps = json.load(f)

    con.execute("DROP TABLE IF EXISTS raw.raw_apps")
    con.execute("""
        CREATE TABLE raw.raw_apps AS
        SELECT * FROM read_json_auto(?)
    """, [APPS_FILE])

    return len(apps)


def load_reviews(con: duckdb.DuckDBPyConnection) -> int:
    with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
        reviews_by_app = json.load(f)

    # Flatten the dict { appId: [review, ...] } into a list of JSONL rows
    jsonl_path = os.path.join(RAW_DIR, "apps_reviews_flat.jsonl")
    count = 0
    with open(jsonl_path, "w", encoding="utf-8") as out:
        for app_id, reviews in reviews_by_app.items():
            for review in reviews:
                review["app_id"] = app_id   # ensure appId is tagged on each row
                out.write(json.dumps(review, ensure_ascii=False) + "\n")
                count += 1

    con.execute("DROP TABLE IF EXISTS raw.raw_reviews")
    con.execute("""
        CREATE TABLE raw.raw_reviews AS
        SELECT * FROM read_ndjson_auto(?)
    """, [jsonl_path])

    return count


def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = duckdb.connect(DB_PATH)

    # Create raw schema
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    n_apps    = load_apps(con)
    n_reviews = load_reviews(con)

    print(f"✅  Loaded {n_apps} apps and {n_reviews} reviews into DuckDB raw schema.")
    con.close()


if __name__ == "__main__":
    main()
