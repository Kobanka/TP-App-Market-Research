-- models/staging/stg_playstore_apps.sql
-- -----------------------------------------------------------------------
-- Staging layer: Apps Catalog
-- Grain: one row per unique application (appId)
-- Actions: rename columns, cast types, clean nulls, create surrogate key
-- No business logic or aggregations applied here.
-- -----------------------------------------------------------------------

WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_apps') }}
),

cleaned AS (
    SELECT
        -- Surrogate key: hash of the natural key
        md5(CAST(appId AS VARCHAR))                         AS app_sk,

        -- Natural key
        CAST(appId AS VARCHAR)                              AS app_id,

        -- Descriptive attributes
        TRIM(CAST(title AS VARCHAR))                        AS app_name,
        TRIM(CAST(developer AS VARCHAR))                    AS developer_name,
        TRIM(CAST(genre AS VARCHAR))                        AS category_name,

        -- Numeric fields
        TRY_CAST(score AS DOUBLE)                           AS avg_rating,
        TRY_CAST(ratings AS BIGINT)                         AS total_ratings,

        -- Install count: strip commas and '+' sign, cast to BIGINT
        TRY_CAST(
            REGEXP_REPLACE(
                REGEXP_REPLACE(CAST(installs AS VARCHAR), ',', ''),
                '\+', ''
            ) AS BIGINT
        )                                                   AS install_count,

        -- Price: 0.0 = free
        COALESCE(TRY_CAST(price AS DOUBLE), 0.0)            AS price,

        -- Derived flag
        CASE WHEN COALESCE(TRY_CAST(price AS DOUBLE), 0.0) = 0.0
             THEN TRUE ELSE FALSE END                       AS is_free

    FROM source
    WHERE appId IS NOT NULL
      AND TRIM(CAST(appId AS VARCHAR)) != ''
),

-- Deduplicate: keep first occurrence of each app_id
deduplicated AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY app_id ORDER BY app_name) AS rn
    FROM cleaned
)

SELECT
    app_sk,
    app_id,
    app_name,
    developer_name,
    category_name,
    avg_rating,
    total_ratings,
    install_count,
    price,
    is_free
FROM deduplicated
WHERE rn = 1
