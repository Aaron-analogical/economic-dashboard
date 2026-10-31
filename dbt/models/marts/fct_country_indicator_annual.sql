-- One row per country, indicator and year, with the change vs the previous
-- year and each country's rank among the tracked countries.

with observations as (

    select * from {{ ref('stg_worldbank__observations') }}

),

indicators as (

    select indicator_code, better_direction from {{ ref('wb_indicators') }}

),

enriched as (

    select
        o.country_iso3,
        o.indicator_code,
        o.year,
        o.value,
        lag(o.value) over w as value_prev_year,
        i.better_direction,
        max(o.year) over (partition by o.country_iso3, o.indicator_code) as latest_year
    from observations as o
    inner join indicators as i using (indicator_code)
    window w as (partition by o.country_iso3, o.indicator_code order by o.year)

)

select
    country_iso3,
    indicator_code,
    year,
    value,
    value_prev_year,
    value - value_prev_year as change_vs_prev_year,
    -- Rank 1 = best performer; without a better direction, 1 = largest value.
    rank() over (
        partition by indicator_code, year
        order by case when better_direction = 'down' then value else -value end
    )                       as rank_in_year,
    year = latest_year      as is_latest_year
from enriched
