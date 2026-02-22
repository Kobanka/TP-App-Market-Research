
    
    

select
    app_sk as unique_field,
    count(*) as n_records

from "playstore"."main_staging"."stg_playstore_apps"
where app_sk is not null
group by app_sk
having count(*) > 1


