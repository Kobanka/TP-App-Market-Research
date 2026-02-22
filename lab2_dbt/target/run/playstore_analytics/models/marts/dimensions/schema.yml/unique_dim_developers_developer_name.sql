
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    developer_name as unique_field,
    count(*) as n_records

from "playstore"."main_marts"."dim_developers"
where developer_name is not null
group by developer_name
having count(*) > 1



  
  
      
    ) dbt_internal_test