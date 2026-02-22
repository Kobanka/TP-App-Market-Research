-- models/marts/dimensions/dim_apps_scd.sql
-- -----------------------------------------------------------------------
-- Section E2 — SCD Type 2 App Dimension
-- -----------------------------------------------------------------------
-- Reads from the snap_dim_apps snapshot to produce a historized version
-- of dim_apps where each row represents one VERSION of an app's attributes.
--
-- Key columns added:
--   - dbt_valid_from : when this version became effective
--   - dbt_valid_to   : when this version was superseded (NULL = current)
--   - is_current     : TRUE for the active version (dbt_valid_to IS NULL)
--
-- Usage for historical fact joins:
--   JOIN dim_apps_scd scd
--     ON fact.app_id = scd.app_id
--    AND fact.reviewed_at >= scd.dbt_valid_from
--    AND (fact.reviewed_at < scd.dbt_valid_to OR scd.dbt_valid_to IS NULL)
-- -----------------------------------------------------------------------

WITH snapshot_data AS (
    SELECT * FROM "playstore"."snapshots"."snap_dim_apps"
),

devs AS (
    SELECT developer_name, developer_sk FROM "playstore"."main_marts"."dim_developers"
),

cats AS (
    SELECT category_name, category_sk FROM "playstore"."main_marts"."dim_categories"
)

SELECT
    -- Row-level surrogate key: combines app_id + valid_from to be unique per version
    md5(app_id || '|' || CAST(dbt_valid_from AS VARCHAR))   AS app_version_sk,

    -- Natural key
    app_id,

    -- Descriptive attributes (version-specific)
    app_name,
    snapshot_data.developer_name,
    snapshot_data.category_name,
    avg_rating,
    total_ratings,
    install_count,
    price,
    is_free,

    -- Related dimension keys
    devs.developer_sk,
    cats.category_sk,

    -- SCD Type 2 metadata columns (added by dbt snapshot)
    dbt_valid_from,
    dbt_valid_to,

    -- Convenience flag: is this the current (active) version?
    CASE WHEN dbt_valid_to IS NULL THEN TRUE ELSE FALSE END  AS is_current,

    -- Human-readable period label
    CAST(dbt_valid_from AS DATE) || ' → ' ||
        COALESCE(CAST(dbt_valid_to AS DATE)::VARCHAR, 'present') AS validity_period

FROM snapshot_data
LEFT JOIN devs ON snapshot_data.developer_name = devs.developer_name
LEFT JOIN cats ON snapshot_data.category_name  = cats.category_name
ORDER BY app_id, dbt_valid_from