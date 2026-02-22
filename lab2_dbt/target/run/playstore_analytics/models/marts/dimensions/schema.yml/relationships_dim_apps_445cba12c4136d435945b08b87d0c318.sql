
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select developer_sk as from_field
    from "playstore"."main_marts"."dim_apps"
    where developer_sk is not null
),

parent as (
    select developer_sk as to_field
    from "playstore"."main_marts"."dim_developers"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test