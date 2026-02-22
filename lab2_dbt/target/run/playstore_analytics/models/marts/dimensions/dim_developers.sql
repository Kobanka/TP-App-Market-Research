
  
    
    

    create  table
      "playstore"."main_marts"."dim_developers__dbt_tmp"
  
    as (
      -- models/marts/dimensions/dim_developers.sql
-- -----------------------------------------------------------------------
-- Dimension: Developers
-- Grain: one row per unique developer name
-- Source: stg_playstore_apps
-- Conformed dimension reusable across future fact tables
-- -----------------------------------------------------------------------

WITH stg AS (
    SELECT DISTINCT developer_name
    FROM "playstore"."main_staging"."stg_playstore_apps"
    WHERE developer_name IS NOT NULL
)

SELECT
    -- Surrogate key
    md5(developer_name)     AS developer_sk,

    -- Natural key (business key)
    developer_name,

    -- Derived attributes
    LOWER(developer_name)   AS developer_name_normalized

FROM stg
ORDER BY developer_name
    );
  
  