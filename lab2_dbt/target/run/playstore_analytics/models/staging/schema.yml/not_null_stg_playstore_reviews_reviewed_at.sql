
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select reviewed_at
from "playstore"."main_staging"."stg_playstore_reviews"
where reviewed_at is null



  
  
      
    ) dbt_internal_test