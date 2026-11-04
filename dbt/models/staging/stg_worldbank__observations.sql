with source as (

    select * from {{ source('worldbank', 'worldbank_observations') }}

)

select
    country_iso3,
    indicator_code,
    year,
    value::numeric  as value,
    loaded_at
from source
where value is not null
