
    
    

with child as (
    select date_fk as from_field
    from "playstore"."main_marts"."fact_reviews"
    where date_fk is not null
),

parent as (
    select date_key as to_field
    from "playstore"."main_marts"."dim_date"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


