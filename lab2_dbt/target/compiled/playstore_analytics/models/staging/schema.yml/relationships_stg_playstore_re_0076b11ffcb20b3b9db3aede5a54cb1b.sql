
    
    

with child as (
    select app_id as from_field
    from "playstore"."main_staging"."stg_playstore_reviews"
    where app_id is not null
),

parent as (
    select app_id as to_field
    from "playstore"."main_staging"."stg_playstore_apps"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


