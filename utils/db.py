import os
import psycopg2
from psycopg2.extras import execute_values
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


def init_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS economic_data (
                    id          SERIAL PRIMARY KEY,
                    indicator   TEXT NOT NULL,
                    series_id   TEXT NOT NULL,
                    date        DATE NOT NULL,
                    value       NUMERIC,
                    fetched_at  TIMESTAMP DEFAULT NOW(),
                    UNIQUE (series_id, date)
                );
            """)
        conn.commit()


def upsert_series(indicator: str, series_id: str, df):
    """Insert or update rows from a DataFrame with columns: date, value."""
    if df.empty:
        return
    rows = [
        (indicator, series_id, row["date"], row["value"])
        for _, row in df.iterrows()
    ]
    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO economic_data (indicator, series_id, date, value)
                VALUES %s
                ON CONFLICT (series_id, date) DO UPDATE
                    SET value      = EXCLUDED.value,
                        fetched_at = NOW();
            """, rows)
        conn.commit()
