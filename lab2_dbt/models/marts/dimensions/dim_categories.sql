-- models/marts/dimensions/dim_categories.sql
-- -----------------------------------------------------------------------
-- Dimension: Categories (Genre)
-- Grain: one row per unique category/genre
-- Source: stg_playstore_apps
-- Part of the Apps hierarchy: dim_apps > dim_categories (snowflake level)
-- -----------------------------------------------------------------------

WITH stg AS (
    SELECT DISTINCT category_name
    FROM {{ ref('stg_playstore_apps') }}
    WHERE category_name IS NOT NULL
)

SELECT
    -- Surrogate key
    md5(category_name)      AS category_sk,

    -- Natural key
    category_name,

    -- Normalized label
    LOWER(category_name)    AS category_name_normalized

FROM stg
ORDER BY category_name
