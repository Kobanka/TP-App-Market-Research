-- models/marts/dimensions/dim_date.sql
-- -----------------------------------------------------------------------
-- Dimension: Date (Conformed)
-- Grain: one row per calendar day
-- Source: generated using DuckDB's generate_series(), anchored to the
--         min/max review dates in stg_playstore_reviews.
--
-- Primary key: date_key (INTEGER, YYYYMMDD) — Kimball convention.
-- This intelligent key makes it human-readable directly in the fact table
-- and allows efficient range partitioning.
-- -----------------------------------------------------------------------

WITH date_bounds AS (
    SELECT
        MIN(review_date)::DATE AS start_date,
        MAX(review_date)::DATE AS end_date
    FROM {{ ref('stg_playstore_reviews') }}
),

date_series AS (
    SELECT
        UNNEST(
            generate_series(
                (SELECT start_date FROM date_bounds),
                (SELECT end_date   FROM date_bounds),
                INTERVAL '1 day'
            )
        )::DATE AS calendar_date
)

SELECT
    -- Integer primary key: YYYYMMDD (Kimball convention)
    CAST(STRFTIME(calendar_date, '%Y%m%d') AS INTEGER)  AS date_key,

    -- Raw date
    calendar_date,

    -- Calendar attributes
    YEAR(calendar_date)                                  AS year,
    QUARTER(calendar_date)                               AS quarter,
    MONTH(calendar_date)                                 AS month,
    CAST(STRFTIME(calendar_date, '%B') AS VARCHAR)       AS month_name,
    CAST(STRFTIME(calendar_date, '%b') AS VARCHAR)       AS month_name_short,
    WEEK(calendar_date)                                  AS week_of_year,
    DAYOFYEAR(calendar_date)                             AS day_of_year,
    DAYOFMONTH(calendar_date)                            AS day_of_month,
    DAYOFWEEK(calendar_date)                             AS day_of_week,  -- 0=Sun, 6=Sat
    CAST(STRFTIME(calendar_date, '%A') AS VARCHAR)       AS day_name,

    -- Flags
    CASE WHEN DAYOFWEEK(calendar_date) IN (0, 6)
         THEN TRUE ELSE FALSE END                        AS is_weekend,

    -- Period labels for BI grouping
    CAST(YEAR(calendar_date) AS VARCHAR)
        || '-Q' ||
    CAST(QUARTER(calendar_date) AS VARCHAR)             AS year_quarter_label,

    CAST(YEAR(calendar_date) AS VARCHAR)
        || '-'  ||
    LPAD(CAST(MONTH(calendar_date) AS VARCHAR), 2, '0') AS year_month_label

FROM date_series
ORDER BY calendar_date
