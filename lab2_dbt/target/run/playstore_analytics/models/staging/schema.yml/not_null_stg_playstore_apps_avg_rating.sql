
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select avg_rating
from "playstore"."main_staging"."stg_playstore_apps"
where avg_rating is null



  
  
      
    ) dbt_internal_test