"""
load_raw.py — Extract every FRED series listed in dbt/seeds/indicators.csv
and load it as-is into raw.fred_observations (upsert, idempotent).

Usage:
    python -m ingestion.load_raw
"""

import csv
import os
import sys
from datetime import date
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

from ingestion.fred_client import fetch_observations

load_dotenv()

START_DATE = "2000-01-01"
END_DATE = date.today().isoformat()
INDICATORS_CSV = Path(__file__).resolve().parent.parent / "dbt" / "seeds" / "indicators.csv"


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME", "neondb"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD", ""),
        sslmode=os.getenv("DB_SSLMODE", "prefer"),
    )


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
    with open(INDICATORS_CSV, newline="") as f:
        series_ids = [row["series_id"] for row in csv.DictReader(f)]

    print(f"Loading {len(series_ids)} series from {START_DATE} to {END_DATE}\n")
    failed = []
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
            print(f"  OK    {series_id} - {len(rows)} rows")

    print(f"\nDone. {len(series_ids) - len(failed)} loaded, {len(failed)} failed.")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
