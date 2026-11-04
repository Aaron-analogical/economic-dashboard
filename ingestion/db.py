"""Shared Postgres helpers: connection and ingestion run log."""

import os
from datetime import datetime, timezone

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME", "neondb"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD", ""),
        sslmode=os.getenv("DB_SSLMODE", "prefer"),
    )


def init_run_log(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS raw;
            CREATE TABLE IF NOT EXISTS raw.ingestion_runs (
                run_id         BIGSERIAL PRIMARY KEY,
                source         TEXT NOT NULL,
                started_at     TIMESTAMPTZ NOT NULL,
                finished_at    TIMESTAMPTZ NOT NULL,
                status         TEXT NOT NULL,
                rows_loaded    INTEGER NOT NULL,
                series_ok      INTEGER NOT NULL,
                series_failed  INTEGER NOT NULL
            );
        """)
    conn.commit()


def log_run(conn, source: str, started_at: datetime, rows_loaded: int,
            series_ok: int, series_failed: int):
    """Record one extractor run. Status is 'success', 'partial' or 'failed'."""
    if series_failed == 0:
        status = "success"
    elif series_ok > 0:
        status = "partial"
    else:
        status = "failed"
    init_run_log(conn)
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO raw.ingestion_runs
                (source, started_at, finished_at, status, rows_loaded, series_ok, series_failed)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (source, started_at, datetime.now(timezone.utc), status,
              rows_loaded, series_ok, series_failed))
    conn.commit()
