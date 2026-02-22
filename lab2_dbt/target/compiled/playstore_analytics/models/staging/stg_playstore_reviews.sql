-- models/staging/stg_playstore_reviews.sql
-- -----------------------------------------------------------------------
-- Staging layer: User Reviews
-- Grain: one row per unique review (reviewId)
-- Actions: rename columns, cast types, parse timestamp, clean nulls,
--          create surrogate key
-- No business logic or aggregations applied here.
-- -----------------------------------------------------------------------

WITH source AS (
    SELECT * FROM "playstore"."raw"."raw_reviews"
),

cleaned AS (
    SELECT
        -- Surrogate key
        md5(CAST(reviewId AS VARCHAR))                          AS review_sk,

        -- Natural keys
        CAST(reviewId AS VARCHAR)                               AS review_id,
        CAST(app_id   AS VARCHAR)                               AS app_id,

        -- Reviewer info
        TRIM(CAST(userName AS VARCHAR))                         AS reviewer_name,

        -- Review body
        CAST(content AS VARCHAR)                                AS review_text,

        -- Numeric score: validated 1–5 range
        CASE
            WHEN TRY_CAST(score AS INTEGER) BETWEEN 1 AND 5
            THEN TRY_CAST(score AS INTEGER)
            ELSE NULL
        END                                                     AS review_score,

        -- Helpfulness votes
        COALESCE(TRY_CAST(thumbsUpCount AS INTEGER), 0)         AS thumbs_up_count,

        -- Timestamp: coerce to timezone-naive UTC DATE and TIMESTAMP
        TRY_CAST("at" AS TIMESTAMP)                             AS reviewed_at,
        CAST(TRY_CAST("at" AS TIMESTAMP) AS DATE)               AS review_date,

        -- Date key for joining dim_date (YYYYMMDD integer)
        CAST(
            STRFTIME(TRY_CAST("at" AS TIMESTAMP), '%Y%m%d')
        AS INTEGER)                                             AS date_key

    FROM source
    WHERE reviewId IS NOT NULL
      AND TRIM(CAST(reviewId AS VARCHAR)) != ''
      AND app_id IS NOT NULL
),

-- Deduplicate on reviewId
deduplicated AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY review_id ORDER BY reviewed_at DESC) AS rn
    FROM cleaned
    WHERE review_score IS NOT NULL   -- drop rows with invalid scores
      AND reviewed_at  IS NOT NULL   -- drop rows with unparseable timestamps
)

SELECT
    review_sk,
    review_id,
    app_id,
    reviewer_name,
    review_text,
    review_score,
    thumbs_up_count,
    reviewed_at,
    review_date,
    date_key
FROM deduplicated
WHERE rn = 1