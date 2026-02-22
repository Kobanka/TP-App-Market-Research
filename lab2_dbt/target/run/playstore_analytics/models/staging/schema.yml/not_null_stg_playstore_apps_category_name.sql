
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select category_name
from "playstore"."main_staging"."stg_playstore_apps"
where category_name is null



  
  
      
    ) dbt_internal_test