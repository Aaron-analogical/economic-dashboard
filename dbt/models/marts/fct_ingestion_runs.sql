select
    run_id,
    source,
    started_at,
    finished_at,
    started_at::date as run_date,
    duration_seconds,
    status,
    rows_loaded,
    series_ok,
    series_failed
from {{ ref('stg_pipeline__ingestion_runs') }}
