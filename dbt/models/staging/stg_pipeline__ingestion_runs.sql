select
    run_id,
    source,
    started_at,
    finished_at,
    extract(epoch from finished_at - started_at)::numeric(10, 1) as duration_seconds,
    status,
    rows_loaded,
    series_ok,
    series_failed
from {{ source('pipeline', 'ingestion_runs') }}
