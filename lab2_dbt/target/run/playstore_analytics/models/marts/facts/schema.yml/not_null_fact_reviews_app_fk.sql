
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select app_fk
from "playstore"."main_marts"."fact_reviews"
where app_fk is null



  
  
      
    ) dbt_internal_test