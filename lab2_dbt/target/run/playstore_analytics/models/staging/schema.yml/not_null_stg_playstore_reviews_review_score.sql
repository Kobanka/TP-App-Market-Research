
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select review_score
from "playstore"."main_staging"."stg_playstore_reviews"
where review_score is null



  
  
      
    ) dbt_internal_test