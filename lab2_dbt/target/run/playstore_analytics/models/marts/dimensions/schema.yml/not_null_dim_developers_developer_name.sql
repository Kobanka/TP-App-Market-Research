
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select developer_name
from "playstore"."main_marts"."dim_developers"
where developer_name is null



  
  
      
    ) dbt_internal_test