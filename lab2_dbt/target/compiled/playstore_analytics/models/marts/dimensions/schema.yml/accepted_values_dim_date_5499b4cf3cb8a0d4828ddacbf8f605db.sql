
    
    

with all_values as (

    select
        month as value_field,
        count(*) as n_records

    from "playstore"."main_marts"."dim_date"
    group by month

)

select *
from all_values
where value_field not in (
    '1','2','3','4','5','6','7','8','9','10','11','12'
)


