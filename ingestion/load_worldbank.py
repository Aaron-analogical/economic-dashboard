"""
load_worldbank.py — Extract every World Bank indicator listed in
dbt/seeds/wb_indicators.csv for the countries in dbt/seeds/countries.csv
and load it as-is into raw.worldbank_observations (upsert, idempotent).

Usage:
    python -m ingestion.load_worldbank
"""

import csv
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from psycopg2.extras import execute_values

from ingestion.db import get_connection, log_run
from ingestion.worldbank_client import fetch_indicator

START_YEAR = 2000
END_YEAR = date.today().year
SEEDS_DIR = Path(__file__).resolve().parent.parent / "dbt" / "seeds"


def read_column(csv_name: str, column: str) -> list[str]:
    with open(SEEDS_DIR / csv_name, newline="") as f:
        return [row[column] for row in csv.DictReader(f)]


def init_raw_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS raw;
            CREATE TABLE IF NOT EXISTS raw.worldbank_observations (
                country_iso3    TEXT NOT NULL,
                indicator_code  TEXT NOT NULL,
                year            INTEGER NOT NULL,
                value           NUMERIC,
                loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (country_iso3, indicator_code, year)
            );
        """)
    conn.commit()


def upsert_observations(conn, indicator_code: str, rows: list[tuple]):
    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO raw.worldbank_observations (country_iso3, indicator_code, year, value)
            VALUES %s
            ON CONFLICT (country_iso3, indicator_code, year) DO UPDATE
                SET value     = EXCLUDED.value,
                    loaded_at = NOW();
        """, [(iso3, indicator_code, year, value) for iso3, year, value in rows])
    conn.commit()


def main():
    started_at = datetime.now(timezone.utc)
    countries = read_column("countries.csv", "iso3")
    indicators = read_column("wb_indicators.csv", "indicator_code")

    print(f"Loading {len(indicators)} indicators x {len(countries)} countries "
          f"from {START_YEAR} to {END_YEAR}\n")
    failed, rows_loaded = [], 0
    with get_connection() as conn:
        init_raw_table(conn)
        for code in indicators:
            try:
                rows = fetch_indicator(code, countries, START_YEAR, END_YEAR)
            except Exception as e:
                print(f"  FAIL  {code} - {e}")
                failed.append(code)
                continue
            upsert_observations(conn, code, rows)
            rows_loaded += len(rows)
            print(f"  OK    {code} - {len(rows)} rows")

        log_run(conn, "worldbank", started_at, rows_loaded,
                len(indicators) - len(failed), len(failed))

    print(f"\nDone. {len(indicators) - len(failed)} loaded, {len(failed)} failed.")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
