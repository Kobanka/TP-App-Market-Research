
      update "playstore"."snapshots"."snap_dim_apps" as DBT_INTERNAL_TARGET
    set dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to
    from "snap_dim_apps__dbt_tmp20260222164021387135" as DBT_INTERNAL_SOURCE
    where DBT_INTERNAL_SOURCE.dbt_scd_id::text = DBT_INTERNAL_TARGET.dbt_scd_id::text
      and DBT_INTERNAL_SOURCE.dbt_change_type::text in ('update'::text, 'delete'::text)
      
        and DBT_INTERNAL_TARGET.dbt_valid_to is null;
      

    insert into "playstore"."snapshots"."snap_dim_apps" ("app_id", "app_sk", "app_name", "developer_name", "category_name", "avg_rating", "total_ratings", "install_count", "price", "is_free", "dbt_updated_at", "dbt_valid_from", "dbt_valid_to", "dbt_scd_id")
    select DBT_INTERNAL_SOURCE."app_id",DBT_INTERNAL_SOURCE."app_sk",DBT_INTERNAL_SOURCE."app_name",DBT_INTERNAL_SOURCE."developer_name",DBT_INTERNAL_SOURCE."category_name",DBT_INTERNAL_SOURCE."avg_rating",DBT_INTERNAL_SOURCE."total_ratings",DBT_INTERNAL_SOURCE."install_count",DBT_INTERNAL_SOURCE."price",DBT_INTERNAL_SOURCE."is_free",DBT_INTERNAL_SOURCE."dbt_updated_at",DBT_INTERNAL_SOURCE."dbt_valid_from",DBT_INTERNAL_SOURCE."dbt_valid_to",DBT_INTERNAL_SOURCE."dbt_scd_id"
    from "snap_dim_apps__dbt_tmp20260222164021387135" as DBT_INTERNAL_SOURCE
    where DBT_INTERNAL_SOURCE.dbt_change_type::text = 'insert'::text;


  