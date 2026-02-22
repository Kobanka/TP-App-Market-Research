
    
    

select
    developer_name as unique_field,
    count(*) as n_records

from "playstore"."main_marts"."dim_developers"
where developer_name is not null
group by developer_name
having count(*) > 1


