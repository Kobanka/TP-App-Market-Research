-- models/marts/facts/fact_reviews.sql
-- -----------------------------------------------------------------------
-- Fact Table: Reviews
-- Grain: one row per unique user review event for one app at a point in time
-- Bus Matrix:
--   Fact: Review event
--   Dimensions: dim_apps ✓ | dim_developers ✓ | dim_categories ✓ | dim_date ✓
--
-- Measures (additive / semi-additive):
--   - review_score     → AVG, COUNT
--   - thumbs_up_count  → SUM, AVG
--   - is_low_rating    → COUNT (score ≤ 2)
--   - is_high_rating   → COUNT (score ≥ 4)
-- -----------------------------------------------------------------------

WITH reviews AS (
    SELECT * FROM "playstore"."main_staging"."stg_playstore_reviews"
),

apps AS (
    SELECT app_id, app_sk, developer_sk, category_sk
    FROM "playstore"."main_marts"."dim_apps"
),

dates AS (
    SELECT date_key
    FROM "playstore"."main_marts"."dim_date"
)

SELECT
    -- Surrogate key of the fact row
    rev.review_sk,

    -- Foreign keys to dimensions (joined on natural keys, stored as surrogate keys)
    app.app_sk          AS app_fk,
    app.developer_sk    AS developer_fk,
    app.category_sk     AS category_fk,
    rev.date_key        AS date_fk,   -- YYYYMMDD integer, joins dim_date.date_key

    -- Degenerate dimension (kept on fact for traceability without its own dim table)
    rev.review_id,
    rev.app_id,         -- natural key for debugging / incremental logic

    -- Measures
    rev.review_score,
    rev.thumbs_up_count,

    -- Derived boolean measures (useful in BI tools for COUNT IF patterns)
    CASE WHEN rev.review_score <= 2 THEN 1 ELSE 0 END   AS is_low_rating,
    CASE WHEN rev.review_score >= 4 THEN 1 ELSE 0 END   AS is_high_rating,
    CASE WHEN rev.review_score = 3  THEN 1 ELSE 0 END   AS is_neutral_rating,

    -- Timestamps (kept for incremental logic and time-series queries)
    rev.reviewed_at,
    rev.review_date

FROM reviews AS rev

-- Only keep reviews that have a valid app dimension row
INNER JOIN apps AS app
    ON rev.app_id = app.app_id

-- Only keep reviews that have a valid date dimension row
INNER JOIN dates AS d
    ON rev.date_key = d.date_key