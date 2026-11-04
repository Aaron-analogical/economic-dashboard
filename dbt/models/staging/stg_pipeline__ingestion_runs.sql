-- Timestamps are converted to UTC without time zone so BI tools do not
-- shift them to the viewer's local time.

select
    run_id,
    source,
    started_at at time zone 'UTC'  as started_at,
    finished_at at time zone 'UTC' as finished_at,
    extract(epoch from finished_at - started_at)::numeric(10, 1) as duration_seconds,
    status,
    rows_loaded,
    series_ok,
    series_failed
from {{ source('pipeline', 'ingestion_runs') }}
