-- Each tracked country must have at least one value for each indicator,
-- otherwise the country comparison page shows blanks.

select
    c.iso3,
    i.indicator_code
from {{ ref('dim_country') }} as c
cross join {{ ref('dim_wb_indicator') }} as i
left join {{ ref('fct_country_indicator_annual') }} as f
    on f.country_iso3 = c.iso3
   and f.indicator_code = i.indicator_code
group by 1, 2
having count(f.year) = 0
