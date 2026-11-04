select
    iso3,
    iso2,
    country_name,
    region,
    country_group,
    'https://data.worldbank.org/country/' || lower(iso2) as worldbank_url
from {{ ref('countries') }}
