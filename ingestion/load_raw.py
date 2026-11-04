"""
load_raw.py — Extract every FRED series listed in dbt/seeds/indicators.csv
and load it as-is into raw.fred_observations (upsert, idempotent).

Usage:
    python -m ingestion.load_raw
"""

import csv
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from psycopg2.extras import execute_values

from ingestion.db import get_connection, log_run
from ingestion.fred_client import fetch_observations

START_DATE = "2000-01-01"
END_DATE = date.today().isoformat()
INDICATORS_CSV = Path(__file__).resolve().parent.parent / "dbt" / "seeds" / "indicators.csv"


def init_raw_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS raw;
            CREATE TABLE IF NOT EXISTS raw.fred_observations (
                series_id   TEXT NOT NULL,
                date        DATE NOT NULL,
                value       NUMERIC,
                loaded_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (series_id, date)
            );
        """)
    conn.commit()


def upsert_observations(conn, series_id: str, rows: list[tuple]):
    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO raw.fred_observations (series_id, date, value)
            VALUES %s
            ON CONFLICT (series_id, date) DO UPDATE
                SET value     = EXCLUDED.value,
                    loaded_at = NOW();
        """, [(series_id, d, v) for d, v in rows])
    conn.commit()


def main():
    started_at = datetime.now(timezone.utc)
    with open(INDICATORS_CSV, newline="") as f:
        series_ids = [row["series_id"] for row in csv.DictReader(f)]

    print(f"Loading {len(series_ids)} series from {START_DATE} to {END_DATE}\n")
    failed, rows_loaded = [], 0
    with get_connection() as conn:
        init_raw_table(conn)
        for series_id in series_ids:
            try:
                rows = fetch_observations(series_id, START_DATE, END_DATE)
            except Exception as e:
                print(f"  FAIL  {series_id} - {e}")
                failed.append(series_id)
                continue
            upsert_observations(conn, series_id, rows)
            rows_loaded += len(rows)
            print(f"  OK    {series_id} - {len(rows)} rows")

        log_run(conn, "fred", started_at, rows_loaded,
                len(series_ids) - len(failed), len(failed))

    print(f"\nDone. {len(series_ids) - len(failed)} loaded, {len(failed)} failed.")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
