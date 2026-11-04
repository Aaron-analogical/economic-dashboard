-- One row per series and month: harmonised grain for cross-indicator analysis.

select
    series_id,
    month_date,
    value,
    value_prev_period,
    value_year_ago,
    prev_period_pct,
    yoy_pct,
    yoy_change,
    display_value,
    n_observations,
    last_observation_date
from {{ ref('int_observations__transformed') }}
