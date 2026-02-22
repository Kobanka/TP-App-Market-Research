
    
    

select
    category_name as unique_field,
    count(*) as n_records

from "playstore"."main_marts"."dim_categories"
where category_name is not null
group by category_name
having count(*) > 1


