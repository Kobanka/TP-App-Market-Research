-- snapshots/snap_dim_apps.sql
-- -----------------------------------------------------------------------
-- Section E2 — Slowly Changing Dimension Type 2
-- -----------------------------------------------------------------------
-- This snapshot tracks historical changes in app attributes (e.g., category,
-- install tier) using dbt's CHECK strategy.
--
-- On first run: captures the full current state of stg_playstore_apps.
-- On subsequent runs: if any column in `check_cols` has changed for an app,
--   dbt will:
--     1. Close the old record: set dbt_valid_to = current_timestamp
--     2. Insert a new record: dbt_valid_from = current_timestamp, dbt_valid_to = NULL
--
-- To test SCD2:
--   1. Modify a category_name value in apps_metadata.json
--   2. Re-run ingest_to_duckdb.py
--   3. Run: dbt snapshot
--   4. Query the snapshot table and observe TWO rows for the modified app:
--      one closed (dbt_valid_to IS NOT NULL) and one current (dbt_valid_to IS NULL)
-- -----------------------------------------------------------------------

{% snapshot snap_dim_apps %}

{{
    config(
        target_schema='snapshots',
        unique_key='app_id',
        strategy='check',
        check_cols=[
            'app_name',
            'developer_name',
            'category_name',
            'avg_rating',
            'install_count',
            'price',
            'is_free'
        ]
    )
}}

SELECT
    app_id,
    app_sk,
    app_name,
    developer_name,
    category_name,
    avg_rating,
    total_ratings,
    install_count,
    price,
    is_free
FROM {{ ref('stg_playstore_apps') }}

{% endsnapshot %}
