
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select developer_fk
from "playstore"."main_marts"."fact_reviews"
where developer_fk is null



  
  
      
    ) dbt_internal_test