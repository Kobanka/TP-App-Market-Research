"""
data_transformation.py
-----------------------
Transforms raw JSON data (or CSV fallback) into clean tabular CSVs.
Handles schema drift, dirty data, and duplicate records robustly.
"""

import json
import pandas as pd
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# ──────────────────────────────────────────────
# Schema normalization maps
# ──────────────────────────────────────────────

# Maps any known variant column name → canonical name
REVIEWS_SCHEMA_MAP = {
    # canonical
    "app_id": "app_id",
    "app_name": "app_name",
    "reviewId": "reviewId",
    "review_id": "reviewId",
    "id": "reviewId",
    "userName": "userName",
    "username": "userName",
    "user_name": "userName",
    "user": "userName",
    "score": "score",
    "rating": "score",
    "stars": "score",
    "content": "content",
    "review": "content",
    "text": "content",
    "review_text": "content",
    "body": "content",
    "thumbsUpCount": "thumbsUpCount",
    "thumbs_up": "thumbsUpCount",
    "thumbs_up_count": "thumbsUpCount",
    "likes": "thumbsUpCount",
    "at": "at",
    "date": "at",
    "timestamp": "at",
    "review_date": "at",
    "created_at": "at",
}

APPS_SCHEMA_MAP = {
    "appId": "appId",
    "app_id": "appId",
    "id": "appId",
    "title": "title",
    "name": "title",
    "app_name": "title",
    "developer": "developer",
    "dev": "developer",
    "score": "score",
    "rating": "score",
    "ratings": "ratings",
    "rating_count": "ratings",
    "installs": "installs",
    "downloads": "installs",
    "genre": "genre",
    "category": "genre",
    "price": "price",
}

REVIEWS_REQUIRED = ["app_id", "reviewId", "score", "at"]
APPS_REQUIRED = ["appId", "title"]


def normalize_columns(df: pd.DataFrame, schema_map: dict) -> pd.DataFrame:
    """Rename columns using schema map (case-insensitive)."""
    rename = {}
    for col in df.columns:
        canonical = schema_map.get(col) or schema_map.get(col.lower()) or schema_map.get(col.strip())
        if canonical:
            rename[col] = canonical
    df = df.rename(columns=rename)
    # Coalesce duplicate columns that collapse to the same canonical name.
    dup_names = df.columns[df.columns.duplicated()].unique()
    for name in dup_names:
        sub = df.loc[:, df.columns == name]
        combined = sub.bfill(axis=1).iloc[:, 0]
        df = df.drop(columns=sub.columns)
        df[name] = combined
    return df


# ──────────────────────────────────────────────
# Loaders
# ──────────────────────────────────────────────

def load_raw_apps(path: Path = None) -> pd.DataFrame:
    """
    Load apps metadata from JSON (original) or CSV (stress-test batches).
    Returns a DataFrame with normalized column names.
    """
    if path is None:
        json_path = RAW_DIR / "apps_metadata.json"
        csv_path = RAW_DIR / "apps_metadata.csv"

        if json_path.exists():
            path = json_path
        elif csv_path.exists():
            path = csv_path
        else:
            raise FileNotFoundError("No apps metadata file found in raw/")

    if str(path).endswith(".json"):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    else:
        df = pd.read_csv(path, dtype=str)

    df = normalize_columns(df, APPS_SCHEMA_MAP)
    return df


def load_raw_reviews(path: Path = None) -> pd.DataFrame:
    """
    Load reviews from JSON (original) or CSV (stress-test batches).
    Returns a flat DataFrame with normalized column names.
    """
    if path is None:
        json_path = RAW_DIR / "apps_reviews.json"
        csv_path = RAW_DIR / "apps_reviews.csv"

        if json_path.exists():
            path = json_path
        elif csv_path.exists():
            path = csv_path
        else:
            raise FileNotFoundError("No reviews file found in raw/")

    if str(path).endswith(".json"):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        # JSON structure: {app_id: [reviews]}
        rows = []
        for app_id, reviews in data.items():
            for r in reviews:
                r["app_id"] = app_id
                rows.append(r)
        df = pd.DataFrame(rows)
    else:
        df = pd.read_csv(path, dtype=str)

    df = normalize_columns(df, REVIEWS_SCHEMA_MAP)
    return df


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def parse_installs(val):
    if pd.isna(val) or val is None:
        return None
    val = str(val).replace(",", "").replace("+", "").strip()
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def parse_score_apps(val):
    try:
        s = float(val)
        if 0.0 <= s <= 5.0:
            return round(s, 2)
    except (ValueError, TypeError):
        pass
    return None


def parse_score_review(val):
    try:
        s = float(val)
        if 1.0 <= s <= 5.0:
            return s
    except (ValueError, TypeError):
        pass
    return None  # invalid → will be dropped downstream


def parse_timestamp(val):
    try:
        return pd.to_datetime(val, errors="coerce", utc=True).tz_localize(None)
    except Exception:
        return pd.NaT


# ──────────────────────────────────────────────
# Transformers
# ──────────────────────────────────────────────

def transform_apps_catalog(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize apps metadata.
    - Deduplicates on appId (keeps first)
    - Validates numeric fields
    - Reports missing required fields
    """
    df = raw_df.copy()

    # Ensure required columns exist
    for col in APPS_REQUIRED:
        if col not in df.columns:
            print(f"  ⚠️  Missing required column '{col}' in apps — filling with None")
            df[col] = None

    # Coerce numeric fields
    df["score"] = df["score"].apply(parse_score_apps) if "score" in df.columns else None
    df["ratings"] = pd.to_numeric(df.get("ratings"), errors="coerce") if "ratings" in df.columns else None
    df["installs"] = df["installs"].apply(parse_installs) if "installs" in df.columns else None
    df["price"] = pd.to_numeric(df.get("price"), errors="coerce") if "price" in df.columns else None

    # Deduplicate on appId
    before = len(df)
    df = df.drop_duplicates(subset=["appId"], keep="first")
    dropped = before - len(df)
    if dropped > 0:
        print(f"  ⚠️  Dropped {dropped} duplicate appId rows (kept first)")

    # Drop rows missing appId entirely
    df = df.dropna(subset=["appId"])

    # Select final columns (only those present)
    final_cols = ["appId", "title", "developer", "score", "ratings", "installs", "genre", "price"]
    df = df[[c for c in final_cols if c in df.columns]]

    return df.reset_index(drop=True)


def transform_reviews(raw_df: pd.DataFrame, apps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize reviews.
    - Maps app_id → app_name from apps catalog
    - Validates score (1–5) and timestamp
    - Removes duplicates on (app_id, reviewId)
    - Drops reviews for unknown app_ids (logs count)
    """
    df = raw_df.copy()

    # Ensure required columns
    for col in REVIEWS_REQUIRED:
        if col not in df.columns:
            print(f"  ⚠️  Missing required column '{col}' in reviews — filling with None")
            df[col] = None

    # Build lookup
    app_lookup = dict(zip(apps_df["appId"].astype(str), apps_df["title"]))

    # app_name
    if "app_name" not in df.columns or df["app_name"].isna().all():
        df["app_name"] = df["app_id"].astype(str).map(app_lookup)

    # Validate score
    df["score"] = df["score"].apply(parse_score_review)

    # Validate timestamp
    df["at"] = df["at"].apply(parse_timestamp)

    # Drop rows with invalid score or timestamp (they would corrupt aggregates)
    before = len(df)
    df = df.dropna(subset=["score", "at"])
    dropped_invalid = before - len(df)
    if dropped_invalid > 0:
        print(f"  ⚠️  Dropped {dropped_invalid} rows with invalid score or timestamp")

    # Drop reviews referencing unknown apps
    unknown_mask = df["app_id"].astype(str).map(lambda x: x not in app_lookup)
    unknown_count = unknown_mask.sum()
    if unknown_count > 0:
        print(f"  ⚠️  Dropped {unknown_count} reviews with unknown app_id (not in apps catalog)")
    df = df[~unknown_mask]

    # Deduplicate
    before = len(df)
    df = df.drop_duplicates(subset=["app_id", "reviewId"], keep="first")
    dup_dropped = before - len(df)
    if dup_dropped > 0:
        print(f"  ⚠️  Dropped {dup_dropped} duplicate (app_id, reviewId) rows")

    # Final column selection
    final_cols = ["app_id", "app_name", "reviewId", "userName", "score", "content", "thumbsUpCount", "at"]
    df = df[[c for c in final_cols if c in df.columns]]

    # Coerce thumbsUpCount to int-like
    if "thumbsUpCount" in df.columns:
        df["thumbsUpCount"] = pd.to_numeric(df["thumbsUpCount"], errors="coerce").fillna(0).astype(int)

    return df.reset_index(drop=True)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main(apps_path: Path = None, reviews_path: Path = None):
    print("\n📦 Loading raw data...")
    raw_apps = load_raw_apps(apps_path)
    raw_reviews = load_raw_reviews(reviews_path)
    print(f"  Raw apps: {len(raw_apps)} rows")
    print(f"  Raw reviews: {len(raw_reviews)} rows")

    print("\n🔧 Transforming apps catalog...")
    apps_df = transform_apps_catalog(raw_apps)
    print(f"  Clean apps: {apps_df.shape}")

    print("\n🔧 Transforming reviews...")
    reviews_df = transform_reviews(raw_reviews, apps_df)
    print(f"  Clean reviews: {reviews_df.shape}")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    apps_df.to_csv(PROCESSED_DIR / "apps_metadata.csv", index=False)
    reviews_df.to_csv(PROCESSED_DIR / "apps_reviews.csv", index=False)
    print(f"\n✅ Transformation complete → {PROCESSED_DIR}")
    return apps_df, reviews_df


if __name__ == "__main__":
    main()