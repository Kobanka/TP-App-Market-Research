import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path("App Market Research") / "data" / "processed"

REVIEWS_IN = PROCESSED_DIR / "apps_reviews.csv"
APPS_IN = PROCESSED_DIR / "apps_metadata.csv"  # optional, for app names if needed

APP_KPIS_OUT = PROCESSED_DIR / "serving_app_kpis.csv"
DAILY_OUT = PROCESSED_DIR / "serving_daily_metrics.csv"


def build_app_kpis(reviews_df: pd.DataFrame) -> pd.DataFrame:
    df = reviews_df.copy()

    # Ensure types
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["at"] = pd.to_datetime(df["at"], errors="coerce")

    # Keep only rows usable for metrics
    df = df.dropna(subset=["app_id", "score", "at"])

    agg = df.groupby(["app_id", "app_name"], dropna=False).agg(
        n_reviews=("score", "size"),
        avg_rating=("score", "mean"),
        first_review_date=("at", "min"),
        most_recent_review_date=("at", "max"),
        low_reviews=("score", lambda s: (s <= 2).sum()),
    ).reset_index()

    agg["pct_low_rating_reviews"] = (agg["low_reviews"] / agg["n_reviews"]) * 100.0
    agg = agg.drop(columns=["low_reviews"])

    # Friendly formatting
    agg["avg_rating"] = agg["avg_rating"].round(3)
    agg["pct_low_rating_reviews"] = agg["pct_low_rating_reviews"].round(2)
    agg["first_review_date"] = agg["first_review_date"].dt.date.astype(str)
    agg["most_recent_review_date"] = agg["most_recent_review_date"].dt.date.astype(str)

    return agg.sort_values(["n_reviews", "avg_rating"], ascending=[False, False])


def build_daily_metrics(reviews_df: pd.DataFrame) -> pd.DataFrame:
    df = reviews_df.copy()
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["at"] = pd.to_datetime(df["at"], errors="coerce")
    df = df.dropna(subset=["score", "at"])

    df["date"] = df["at"].dt.date

    daily = df.groupby("date").agg(
        daily_number_of_reviews=("score", "size"),
        daily_average_rating=("score", "mean"),
    ).reset_index()

    daily["daily_average_rating"] = daily["daily_average_rating"].round(3)
    daily["date"] = daily["date"].astype(str)

    return daily.sort_values("date")


def main():
    reviews_df = pd.read_csv(REVIEWS_IN)

    app_kpis = build_app_kpis(reviews_df)
    daily = build_daily_metrics(reviews_df)

    app_kpis.to_csv(APP_KPIS_OUT, index=False)
    daily.to_csv(DAILY_OUT, index=False)

    print(f"✅ Wrote {APP_KPIS_OUT} ({app_kpis.shape})")
    print(f"✅ Wrote {DAILY_OUT} ({daily.shape})")


if __name__ == "__main__":
    main()
