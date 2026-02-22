"""
dashboard.py
------------
Lightweight analytics dashboard from serving-layer CSVs.
Answers:
  1. Which apps perform best/worst by user reviews?
  2. Are ratings improving or declining over time?
  3. Are there noticeable differences in review volume between apps?
"""

import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
APP_KPIS      = PROCESSED_DIR / "serving_app_kpis.csv"
DAILY         = PROCESSED_DIR / "serving_daily_metrics.csv"
OUT_HTML      = PROCESSED_DIR / "dashboard.html"

TITLE_STYLE = dict(font_size=16, font_color="#2c3e50")


def load_data():
    app  = pd.read_csv(APP_KPIS)
    daily = pd.read_csv(DAILY)
    for col in ["avg_rating", "n_reviews", "pct_low_rating_reviews"]:
        if col in app.columns:
            app[col] = pd.to_numeric(app[col], errors="coerce")
    daily["date"]                 = pd.to_datetime(daily["date"], errors="coerce")
    daily["daily_average_rating"] = pd.to_numeric(daily["daily_average_rating"], errors="coerce")
    daily["daily_number_of_reviews"] = pd.to_numeric(daily["daily_number_of_reviews"], errors="coerce")
    return app, daily


def chart_best_worst(app: pd.DataFrame) -> str:
    """Horizontal bar chart: top 10 & bottom 5 apps by avg rating (min 5 reviews)."""
    df = app.dropna(subset=["app_name", "avg_rating", "n_reviews"])
    df = df[df["n_reviews"] >= 5].sort_values("avg_rating", ascending=False)
    top    = df.head(10)
    bottom = df.tail(5)
    combined = pd.concat([top, bottom]).drop_duplicates("app_name")
    combined["label"] = combined["app_name"].str[:30]

    fig = px.bar(
        combined.sort_values("avg_rating"),
        x="avg_rating",
        y="label",
        orientation="h",
        color="avg_rating",
        color_continuous_scale="RdYlGn",
        range_color=[1, 5],
        text=combined.sort_values("avg_rating")["avg_rating"].round(2),
        title="App Performance: Average Rating (apps with ≥5 reviews)",
        labels={"avg_rating": "Average Rating", "label": ""},
        hover_data={"n_reviews": True, "pct_low_rating_reviews": True},
    )
    fig.update_layout(coloraxis_showscale=False, height=500)
    fig.update_traces(textposition="outside")
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def chart_rating_trend(daily: pd.DataFrame) -> str:
    """Line chart of 7-day rolling average rating over time."""
    df = daily.dropna(subset=["date", "daily_average_rating"]).sort_values("date").copy()
    df["rolling_avg"] = df["daily_average_rating"].rolling(7, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["daily_average_rating"],
        mode="markers", name="Daily avg", opacity=0.3,
        marker=dict(size=3, color="#95a5a6")
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["rolling_avg"],
        mode="lines", name="7-day rolling avg",
        line=dict(color="#2980b9", width=2)
    ))
    fig.add_hline(y=3, line_dash="dash", line_color="orange",
                  annotation_text="Neutral (3.0)", annotation_position="bottom right")
    fig.update_layout(
        title="Rating Trend Over Time (7-day rolling average)",
        xaxis_title="Date", yaxis_title="Average Rating",
        yaxis=dict(range=[1, 5.2]), height=400
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def chart_review_volume(app: pd.DataFrame) -> str:
    """Bubble chart: review volume vs avg rating, sized by % low ratings."""
    df = app.dropna(subset=["app_name", "avg_rating", "n_reviews"]).copy()
    df = df[df["n_reviews"] >= 5]
    df["label"] = df["app_name"].str[:25]

    fig = px.scatter(
        df,
        x="n_reviews",
        y="avg_rating",
        size="pct_low_rating_reviews",
        size_max=40,
        hover_name="app_name",
        color="avg_rating",
        color_continuous_scale="RdYlGn",
        range_color=[1, 5],
        text="label",
        title="Review Volume vs Rating (bubble size = % low ratings ≤2★)",
        labels={"n_reviews": "Number of Reviews", "avg_rating": "Avg Rating",
                "pct_low_rating_reviews": "% Low Ratings"},
    )
    fig.update_traces(textposition="top center", textfont_size=9)
    fig.update_layout(height=520, coloraxis_showscale=False)
    return fig.to_html(full_html=False, include_plotlyjs=False)


def chart_weekly_volume(daily: pd.DataFrame) -> str:
    """Bar chart of weekly review volume."""
    df = daily.dropna(subset=["date", "daily_number_of_reviews"]).sort_values("date").copy()
    df["week"] = df["date"].dt.to_period("W").dt.start_time
    weekly = df.groupby("week", as_index=False)["daily_number_of_reviews"].sum()

    fig = px.bar(
        weekly, x="week", y="daily_number_of_reviews",
        title="Weekly Review Volume",
        labels={"week": "Week", "daily_number_of_reviews": "Total Reviews"},
        color="daily_number_of_reviews",
        color_continuous_scale="Blues",
    )
    fig.update_layout(coloraxis_showscale=False, height=380)
    fig.update_xaxes(rangeslider_visible=True)
    return fig.to_html(full_html=False, include_plotlyjs=False)


DESCRIPTION = """
<div style="max-width:900px;margin:0 auto 32px;padding:16px;background:#f8f9fa;border-left:4px solid #2980b9;border-radius:4px;font-family:sans-serif;color:#2c3e50">
  <h3 style="margin:0 0 8px">📌 Dashboard Summary</h3>
  <p style="margin:0">
    This dashboard analyses user reviews scraped from Google Play for <strong>AI note-taking apps</strong>.
    The <em>App Performance</em> chart reveals which apps users rate highest and lowest (minimum 5 reviews).
    The <em>Rating Trend</em> chart shows whether overall sentiment is improving or declining over time using
    a 7-day rolling average. The <em>Review Volume</em> bubble chart highlights which apps attract the most
    engagement and how low-rating share correlates with average score.
  </p>
</div>
"""

HEADER = """
<div style="background:#2c3e50;color:white;padding:24px 32px;margin-bottom:24px;font-family:sans-serif">
  <h1 style="margin:0;font-size:26px">🗒️ AI Note-Taking Apps — Market Research Dashboard</h1>
  <p style="margin:6px 0 0;opacity:0.7;font-size:13px">Data Engineering Lab 1 · Pipeline Output</p>
</div>
"""


def main():
    app, daily = load_data()

    html_parts = [
        "<html><head><meta charset='utf-8'><title>AI Apps Dashboard</title></head><body style='margin:0;background:#fff'>",
        HEADER,
        DESCRIPTION,
        "<div style='max-width:960px;margin:0 auto;padding:0 16px'>",
        chart_best_worst(app),
        "<br/>",
        chart_review_volume(app),
        "<br/>",
        chart_rating_trend(daily),
        "<br/>",
        chart_weekly_volume(daily),
        "</div></body></html>",
    ]

    OUT_HTML.write_text("\n".join(html_parts), encoding="utf-8")
    print(f"✅ Dashboard written → {OUT_HTML}")


if __name__ == "__main__":
    main()