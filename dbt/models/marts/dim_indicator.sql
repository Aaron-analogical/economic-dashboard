with indicators as (

    select * from {{ ref('indicators') }}

),

coverage as (

    select
        series_id,
        min(observation_date) as first_observation_date,
        max(observation_date) as last_observation_date,
        count(*)              as n_observations
    from {{ ref('stg_fred__observations') }}
    group by 1

)

select
    i.series_id,
    i.indicator_name,
    i.category,
    i.unit,
    i.display_unit,
    i.frequency,
    case i.frequency
        when 'D' then 'Daily'
        when 'W' then 'Weekly'
        when 'M' then 'Monthly'
        when 'Q' then 'Quarterly'
    end                                                  as frequency_name,
    i.transform,
    'https://fred.stlouisfed.org/series/' || i.series_id as fred_url,
    c.first_observation_date,
    c.last_observation_date,
    coalesce(c.n_observations, 0)                        as n_observations
from indicators as i
left join coverage as c using (series_id)
