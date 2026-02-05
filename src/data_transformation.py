import json
import pandas as pd
import os
from pathlib import Path


RAW_DIR = Path("App Market Research") / "data" / "raw"
PROCESSED_DIR = Path("App Market Research") / "data" / "processed"

def load_raw_apps():
    with open(RAW_DIR / "apps_metadata.json", encoding="utf-8") as f:
        return json.load(f)


def load_raw_reviews():
    with open(RAW_DIR / "apps_reviews.json", encoding="utf-8") as f:
        return json.load(f)


# Transform app metadata

def parse_installs(installs_str):
    if installs_str is None:
        return None
    return int(
        installs_str.replace(",", "")
                    .replace("+", "")
                    .strip()
    )


def transform_apps_catalog(raw_apps):
    records = []

    for app in raw_apps:
        records.append({
            "appId": app.get("appId"),
            "title": app.get("title"),
            "developer": app.get("developer"),
            "score": round(app.get("score", 0), 2) if app.get("score") else None,
            "ratings": app.get("ratings"),
            "installs": parse_installs(app.get("installs")),
            "genre": app.get("genre"),
            "price": app.get("price")
        })

    df = pd.DataFrame(records)

    return df


# Transform app reviews

def transform_reviews(raw_reviews, apps_df):
    app_id_to_name = dict(
        zip(apps_df["appId"], apps_df["title"])
    )

    rows = []

    for app_id, reviews in raw_reviews.items():
        for r in reviews:
            rows.append({
                "app_id": app_id,
                "app_name": app_id_to_name.get(app_id),
                "reviewId": r.get("reviewId"),
                "userName": r.get("userName"),
                "score": r.get("score"),
                "content": r.get("content"),
                "thumbsUpCount": r.get("thumbsUpCount"),
                "at": pd.to_datetime(r.get("at"), errors="coerce")
            })

    df = pd.DataFrame(rows)

    return df


if __name__ == "__main__":

    # Load raw data
    raw_apps = load_raw_apps()
    raw_reviews = load_raw_reviews()

    # Transform
    apps_df = transform_apps_catalog(raw_apps)
    reviews_df = transform_reviews(raw_reviews, apps_df)

    # Save processed datasets
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    apps_df.to_csv(PROCESSED_DIR / "apps_metadata.csv", index=False)
    reviews_df.to_csv(PROCESSED_DIR / "apps_reviews.csv", index=False)

    print("✅ Transformation stage completed")
    print(f"Apps catalog: {apps_df.shape}")
    print(f"Apps reviews: {reviews_df.shape}")
