
    
    

select
    app_id as unique_field,
    count(*) as n_records

from "playstore"."main_marts"."dim_apps"
where app_id is not null
group by app_id
having count(*) > 1


