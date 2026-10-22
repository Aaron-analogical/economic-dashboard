-- Period-over-period and year-over-year changes on the monthly grain.
-- Year-ago values are joined on the calendar (month - 12) rather than
-- lag(12), so gaps in a series never shift the comparison window.

with monthly as (

    select * from {{ ref('int_observations__monthly') }}

),

indicators as (

    select series_id, transform from {{ ref('indicators') }}

),

with_history as (

    select
        m.series_id,
        m.month_date,
        m.value,
        m.n_observations,
        m.last_observation_date,
        lag(m.value) over (partition by m.series_id order by m.month_date) as value_prev_period,
        year_ago.value                                                     as value_year_ago
    from monthly as m
    left join monthly as year_ago
        on  year_ago.series_id  = m.series_id
        and year_ago.month_date = (m.month_date - interval '12 months')::date

),

changes as (

    select
        *,
        (value / nullif(value_prev_period, 0) - 1) * 100 as prev_period_pct,
        (value / nullif(value_year_ago, 0) - 1) * 100    as yoy_pct,
        value - value_year_ago                           as yoy_change
    from with_history

)

select
    c.*,
    case i.transform
        when 'yoy' then c.yoy_pct
        else c.value
    end as display_value
from changes as c
inner join indicators as i using (series_id)
