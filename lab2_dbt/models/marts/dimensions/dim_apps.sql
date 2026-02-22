-- models/marts/dimensions/dim_apps.sql
-- -----------------------------------------------------------------------
-- Dimension: Apps
-- Grain: one row per unique application (current state)
-- Source: stg_playstore_apps
-- Hierarchy: dim_apps > dim_categories  (snowflake normalization)
-- FK references: dim_developers, dim_categories
-- Note: SCD Type 1 (overwrites). SCD Type 2 tracked via snapshot (see
--       snapshots/snap_dim_apps.sql and dim_apps_scd.sql)
-- -----------------------------------------------------------------------

WITH stg AS (
    SELECT * FROM {{ ref('stg_playstore_apps') }}
),

devs AS (
    SELECT developer_name, developer_sk
    FROM {{ ref('dim_developers') }}
),

cats AS (
    SELECT category_name, category_sk
    FROM {{ ref('dim_categories') }}
)

SELECT
    -- Surrogate key (from staging)
    stg.app_sk,

    -- Natural key
    stg.app_id,

    -- Descriptive attributes
    stg.app_name,
    stg.avg_rating,
    stg.total_ratings,
    stg.install_count,
    stg.price,
    stg.is_free,

    -- Foreign keys to related dimensions (snowflake hierarchy)
    devs.developer_sk,
    stg.developer_name,

    cats.category_sk,
    stg.category_name,

    -- Derived tier label for BI filtering
    CASE
        WHEN stg.install_count >= 10000000 THEN 'Tier 1 (10M+)'
        WHEN stg.install_count >= 1000000  THEN 'Tier 2 (1M+)'
        WHEN stg.install_count >= 100000   THEN 'Tier 3 (100K+)'
        ELSE                                    'Tier 4 (<100K)'
    END AS install_tier

FROM stg
LEFT JOIN devs ON stg.developer_name = devs.developer_name
LEFT JOIN cats ON stg.category_name  = cats.category_name
