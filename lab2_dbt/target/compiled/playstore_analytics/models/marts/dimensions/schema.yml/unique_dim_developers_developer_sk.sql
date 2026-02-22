
    
    

select
    developer_sk as unique_field,
    count(*) as n_records

from "playstore"."main_marts"."dim_developers"
where developer_sk is not null
group by developer_sk
having count(*) > 1


