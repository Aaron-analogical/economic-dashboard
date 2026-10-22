-- Native-grain observations (daily, weekly, monthly or quarterly per series).

select
    series_id,
    observation_date,
    value,
    loaded_at
from {{ ref('stg_fred__observations') }}
