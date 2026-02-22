
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select app_name
from "playstore"."main_marts"."dim_apps"
where app_name is null



  
  
      
    ) dbt_internal_test