import pandas as pd
from pathlib import Path
import plotly.express as px

PROCESSED_DIR = Path("App Market Research") / "data" / "processed"
APP_KPIS = PROCESSED_DIR / "serving_app_kpis.csv"
DAILY = PROCESSED_DIR / "serving_daily_metrics.csv"
OUT_HTML = PROCESSED_DIR / "dashboard.html"


def main():
    app = pd.read_csv(APP_KPIS)
    daily = pd.read_csv(DAILY)


    # Basic cleaning/typing for plotting
    if "avg_rating" in app.columns:
        app["avg_rating"] = pd.to_numeric(app["avg_rating"], errors="coerce")
    if "n_reviews" in app.columns:
        app["n_reviews"] = pd.to_numeric(app["n_reviews"], errors="coerce")

    if "date" in daily.columns:
        daily["date"] = pd.to_datetime(daily["date"], errors="coerce")
    if "daily_average_rating" in daily.columns:
        daily["daily_average_rating"] = pd.to_numeric(daily["daily_average_rating"], errors="coerce")
    if "daily_number_of_reviews" in daily.columns:
        daily["daily_number_of_reviews"] = pd.to_numeric(daily["daily_number_of_reviews"], errors="coerce")

    # Chart 1: Best/Worst apps (filter tiny apps so ranking is meaningful)
    app_rank = app.dropna(subset=["app_name", "avg_rating", "n_reviews"]).copy()
    app_rank = app_rank[app_rank["n_reviews"] >= 5]  # adjust threshold if you want

    fig_apps = px.scatter(
        app_rank,
        x="n_reviews",
        y="avg_rating",
        hover_name="app_name",
        title="Apps: average rating vs review volume",
        labels={"n_reviews": "Number of reviews", "avg_rating": "Average rating"},
    )

    # Chart 2: Rating trend over time (daily average)
    daily_ts = daily.dropna(subset=["date", "daily_average_rating"]).sort_values("date")

    fig_trend = px.line(
        daily_ts,
        x="date",
        y="daily_average_rating",
        title="Daily average rating over time",
        labels={"daily_average_rating": "Daily average rating", "date": "Date"},
    )

    # Chart 3: Daily review volume
    daily_vol = daily.dropna(subset=["date", "daily_number_of_reviews"]).sort_values("date").copy()
    daily_vol["week"] = daily_vol["date"].dt.to_period("W").dt.start_time

    weekly = daily_vol.groupby("week", as_index=False)["daily_number_of_reviews"].sum()

    fig_volume = px.bar(
        weekly,
        x="week",
        y="daily_number_of_reviews",
        title="Weekly number of reviews",
        labels={"week": "Week", "daily_number_of_reviews": "Reviews (weekly)"},
    )

    fig_volume.update_xaxes(rangeslider_visible=True)


    # Write one simple HTML dashboard
    html = ""
    html += fig_apps.to_html(full_html=False, include_plotlyjs="cdn")
    html += fig_trend.to_html(full_html=False, include_plotlyjs=False)
    html += fig_volume.to_html(full_html=False, include_plotlyjs=False)

    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"✅ Dashboard written to: {OUT_HTML}")


if __name__ == "__main__":
    main()
