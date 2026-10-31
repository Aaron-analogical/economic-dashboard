-- One row per source: last load, data coverage and a freshness status for
-- the pipeline health page. A source is stale after 2 days without a
-- successful run (the pipeline is scheduled daily).

with runs as (

    select
        source,
        max(finished_at) filter (where status = 'success') as last_success_at,
        max(finished_at)                                     as last_run_at,
        count(*)                                             as n_runs,
        count(*) filter (where status <> 'success')          as n_failed_runs
    from {{ ref('stg_pipeline__ingestion_runs') }}
    group by 1

),

data as (

    select
        'fred'                    as source,
        'FRED (US indicators)'    as source_name,
        count(distinct series_id) as n_series,
        count(*)                  as n_rows,
        max(observation_date)     as latest_data_date
    from {{ ref('stg_fred__observations') }}

    union all

    select
        'worldbank',
        'World Bank (country comparison)',
        count(distinct indicator_code),
        count(*),
        make_date(max(year), 12, 31)
    from {{ ref('stg_worldbank__observations') }}

)

select
    d.source,
    d.source_name,
    d.n_series,
    d.n_rows,
    d.latest_data_date,
    r.last_success_at,
    r.last_run_at,
    coalesce(r.n_runs, 0)        as n_runs,
    coalesce(r.n_failed_runs, 0) as n_failed_runs,
    round(extract(epoch from now() - r.last_success_at) / 3600, 1) as hours_since_success,
    case
        when r.last_success_at is null                     then 'never run'
        when r.last_success_at < now() - interval '2 days' then 'stale'
        else 'fresh'
    end                          as freshness_status
from data as d
left join runs as r using (source)
