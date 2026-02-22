
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select date_fk
from "playstore"."main_marts"."fact_reviews"
where date_fk is null



  
  
      
    ) dbt_internal_test