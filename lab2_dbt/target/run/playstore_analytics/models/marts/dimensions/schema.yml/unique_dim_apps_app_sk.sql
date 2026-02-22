
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    app_sk as unique_field,
    count(*) as n_records

from "playstore"."main_marts"."dim_apps"
where app_sk is not null
group by app_sk
having count(*) > 1



  
  
      
    ) dbt_internal_test