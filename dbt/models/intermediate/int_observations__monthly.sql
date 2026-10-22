-- Resample every series to a monthly grain: daily and weekly series are
-- averaged over the month; monthly and quarterly series pass through.

with observations as (

    select * from {{ ref('stg_fred__observations') }}

)

select
    series_id,
    date_trunc('month', observation_date)::date as month_date,
    avg(value)                                  as value,
    count(*)                                    as n_observations,
    max(observation_date)                       as last_observation_date
from observations
group by 1, 2
