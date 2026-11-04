with source as (

    select * from {{ source('fred', 'fred_observations') }}

)

select
    series_id,
    date            as observation_date,
    value::numeric  as value,
    loaded_at
from source
where value is not null
