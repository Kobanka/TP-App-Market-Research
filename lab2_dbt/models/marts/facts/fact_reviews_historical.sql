-- models/marts/facts/fact_reviews_historical.sql
-- -----------------------------------------------------------------------
-- Section E2 — Historical Fact Table (links to SCD2 app dimension)
-- -----------------------------------------------------------------------
-- This model extends fact_reviews_incremental by joining each review to
-- the version of dim_apps_scd that was VALID AT THE TIME OF THE REVIEW.
-- This enables true historical analysis such as:
--   "What was the category of this app when the review was written?"
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

    {% if is_incremental() %}
    WHERE reviewed_at > (SELECT MAX(reviewed_at) FROM {{ this }})
    {% endif %}
),

-- Use the SCD2 dimension — join on app_id AND validity window
apps_scd AS (
    SELECT
        app_id,
        app_version_sk,
        developer_sk,
        category_sk,
        app_name,
        category_name,
        developer_name,
        dbt_valid_from,
        dbt_valid_to
    FROM {{ ref('dim_apps_scd') }}
),

dates AS (
    SELECT date_key FROM {{ ref('dim_date') }}
)

SELECT
    rev.review_sk,

    -- FK to the historically-accurate version of the app dimension
    scd.app_version_sk      AS app_version_fk,
    scd.developer_sk        AS developer_fk,
    scd.category_sk         AS category_fk,
    rev.date_key            AS date_fk,

    rev.review_id,
    rev.app_id,

    -- Include the app attributes that were valid at review time
    scd.app_name,
    scd.category_name,
    scd.developer_name,

    rev.review_score,
    rev.thumbs_up_count,
    CASE WHEN rev.review_score <= 2 THEN 1 ELSE 0 END   AS is_low_rating,
    CASE WHEN rev.review_score >= 4 THEN 1 ELSE 0 END   AS is_high_rating,
    CASE WHEN rev.review_score = 3  THEN 1 ELSE 0 END   AS is_neutral_rating,
    rev.reviewed_at,
    rev.review_date

FROM reviews AS rev

-- Join to the SCD2 version valid at the time of the review
INNER JOIN apps_scd AS scd
    ON  rev.app_id      = scd.app_id
    AND rev.reviewed_at >= scd.dbt_valid_from
    AND (rev.reviewed_at < scd.dbt_valid_to OR scd.dbt_valid_to IS NULL)

-- Only keep reviews that have a valid date dimension row
INNER JOIN dates AS d ON rev.date_key = d.date_key
