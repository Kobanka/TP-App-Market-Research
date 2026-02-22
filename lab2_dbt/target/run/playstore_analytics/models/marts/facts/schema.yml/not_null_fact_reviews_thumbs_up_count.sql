
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select thumbs_up_count
from "playstore"."main_marts"."fact_reviews"
where thumbs_up_count is null



  
  
      
    ) dbt_internal_test