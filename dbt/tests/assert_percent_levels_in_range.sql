-- Rates and percentages reported as levels should stay within a plausible range.

select
    o.series_id,
    o.observation_date,
    o.value
from {{ ref('fct_observations') }} as o
inner join {{ ref('dim_indicator') }} as i using (series_id)
where i.unit = 'Percent'
  and (o.value < -5 or o.value > 100)
