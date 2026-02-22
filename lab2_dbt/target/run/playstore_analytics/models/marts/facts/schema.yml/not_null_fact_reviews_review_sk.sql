
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select review_sk
from "playstore"."main_marts"."fact_reviews"
where review_sk is null



  
  
      
    ) dbt_internal_test