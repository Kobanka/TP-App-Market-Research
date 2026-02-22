-- models/marts/facts/fact_reviews_incremental.sql
-- -----------------------------------------------------------------------
-- Section E1 — Incremental Loading
-- -----------------------------------------------------------------------
-- This model replaces fact_reviews with an INCREMENTAL materialization.
-- On the first run: full table build.
-- On subsequent runs: only rows WHERE reviewed_at > MAX(reviewed_at)
--   already in the table are processed and inserted, using review_id as
--   the unique_key to prevent duplicates on re-runs (idempotent).
--
-- To test: append new rows to apps_reviews.json, re-run ingest_to_duckdb.py,
--   then run: dbt run --select fact_reviews_incremental
-- -----------------------------------------------------------------------

{{
    config(
        materialized='incremental',
        unique_key='review_id',
        on_schema_change='sync_all_columns'
    )
}}

WITH reviews AS (
    SELECT * FROM {{ ref('stg_playstore_reviews') }}

    -- Incremental filter: only process new reviews not yet in the fact table
    {% if is_incremental() %}
    WHERE reviewed_at > (SELECT MAX(reviewed_at) FROM {{ this }})
    {% endif %}
),

apps AS (
    SELECT app_id, app_sk, developer_sk, category_sk
    FROM {{ ref('dim_apps') }}
),

dates AS (
    SELECT date_key
    FROM {{ ref('dim_date') }}
)

SELECT
    rev.review_sk,
    app.app_sk          AS app_fk,
    app.developer_sk    AS developer_fk,
    app.category_sk     AS category_fk,
    rev.date_key        AS date_fk,
    rev.review_id,
    rev.app_id,
    rev.review_score,
    rev.thumbs_up_count,
    CASE WHEN rev.review_score <= 2 THEN 1 ELSE 0 END   AS is_low_rating,
    CASE WHEN rev.review_score >= 4 THEN 1 ELSE 0 END   AS is_high_rating,
    CASE WHEN rev.review_score = 3  THEN 1 ELSE 0 END   AS is_neutral_rating,
    rev.reviewed_at,
    rev.review_date

FROM reviews AS rev
INNER JOIN apps AS app ON rev.app_id  = app.app_id
INNER JOIN dates AS d  ON rev.date_key = d.date_key
