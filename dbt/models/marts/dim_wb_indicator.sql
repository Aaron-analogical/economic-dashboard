with indicators as (

    select * from {{ ref('wb_indicators') }}

),

coverage as (

    select
        indicator_code,
        min(year)                    as first_year,
        max(year)                    as last_year,
        count(distinct country_iso3) as n_countries,
        count(*)                     as n_observations
    from {{ ref('stg_worldbank__observations') }}
    group by 1

)

select
    i.indicator_code,
    i.indicator_name,
    i.category,
    i.unit,
    i.better_direction,
    i.sort_order,
    'https://data.worldbank.org/indicator/' || i.indicator_code as worldbank_url,
    c.first_year,
    c.last_year,
    coalesce(c.n_countries, 0)    as n_countries,
    coalesce(c.n_observations, 0) as n_observations
from indicators as i
left join coverage as c using (indicator_code)
