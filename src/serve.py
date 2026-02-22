"""
serve.py
--------
Produces serving-layer outputs from processed data:
  - serving_app_kpis.csv   : one row per app with aggregate KPIs
  - serving_daily_metrics.csv : daily time-series of review volume & rating
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REVIEWS_IN   = PROCESSED_DIR / "apps_reviews.csv"
APP_KPIS_OUT = PROCESSED_DIR / "serving_app_kpis.csv"
DAILY_OUT    = PROCESSED_DIR / "serving_daily_metrics.csv"


def build_app_kpis(reviews_df: pd.DataFrame) -> pd.DataFrame:
    df = reviews_df.copy()
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["at"]    = pd.to_datetime(df["at"], errors="coerce")
    df = df.dropna(subset=["app_id", "score", "at"])

    agg = df.groupby(["app_id", "app_name"], dropna=False).agg(
        n_reviews            = ("score", "size"),
        avg_rating           = ("score", "mean"),
        first_review_date    = ("at", "min"),
        most_recent_review_date = ("at", "max"),
        low_reviews          = ("score", lambda s: (s <= 2).sum()),
    ).reset_index()

    agg["pct_low_rating_reviews"] = (agg["low_reviews"] / agg["n_reviews"] * 100).round(2)
    agg["avg_rating"] = agg["avg_rating"].round(3)
    agg["first_review_date"]       = agg["first_review_date"].dt.date.astype(str)
    agg["most_recent_review_date"] = agg["most_recent_review_date"].dt.date.astype(str)

    return agg.drop(columns=["low_reviews"]).sort_values(
        ["n_reviews", "avg_rating"], ascending=[False, False]
    ).reset_index(drop=True)


def build_daily_metrics(reviews_df: pd.DataFrame) -> pd.DataFrame:
    df = reviews_df.copy()
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["at"]    = pd.to_datetime(df["at"], errors="coerce")
    df = df.dropna(subset=["score", "at"])
    df["date"] = df["at"].dt.date

    daily = df.groupby("date").agg(
        daily_number_of_reviews = ("score", "size"),
        daily_average_rating    = ("score", "mean"),
    ).reset_index()
    daily["daily_average_rating"] = daily["daily_average_rating"].round(3)
    daily["date"] = daily["date"].astype(str)
    return daily.sort_values("date").reset_index(drop=True)


def main():
    print("\n📊 Building serving layer...")
    reviews_df = pd.read_csv(REVIEWS_IN)
    app_kpis   = build_app_kpis(reviews_df)
    daily      = build_daily_metrics(reviews_df)

    app_kpis.to_csv(APP_KPIS_OUT, index=False)
    daily.to_csv(DAILY_OUT, index=False)

    print(f"  ✅ App KPIs → {APP_KPIS_OUT}  {app_kpis.shape}")
    print(f"  ✅ Daily metrics → {DAILY_OUT}  {daily.shape}")
    return app_kpis, daily


if __name__ == "__main__":
    main()