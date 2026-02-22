
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select category_fk
from "playstore"."main_marts"."fact_reviews"
where category_fk is null



  
  
      
    ) dbt_internal_test