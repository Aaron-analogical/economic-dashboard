with spine as (

    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="'2000-01-01'::date",
        end_date="(date_trunc('year', current_date) + interval '1 year')::date"
    ) }}

)

select
    date_day::date                              as date,
    extract(year from date_day)::int            as year,
    extract(quarter from date_day)::int         as quarter,
    'Q' || extract(quarter from date_day)::int  as quarter_label,
    extract(month from date_day)::int           as month,
    to_char(date_day, 'Mon')                    as month_short,
    to_char(date_day, 'YYYY-MM')                as year_month,
    date_trunc('month', date_day)::date         as month_start,
    extract(isodow from date_day)::int          as day_of_week,
    extract(isodow from date_day) in (6, 7)     as is_weekend
from spine
