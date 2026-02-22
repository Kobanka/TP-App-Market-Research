
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select category_sk
from "playstore"."main_marts"."dim_categories"
where category_sk is null



  
  
      
    ) dbt_internal_test