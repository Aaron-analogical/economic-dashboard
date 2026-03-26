import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME", "test"),
        user=os.getenv("DB_USER", "aaron"),
        password=os.getenv("DB_PASSWORD", ""),
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
    with get_connection() as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                cur.execute("""
                    INSERT INTO economic_data (indicator, series_id, date, value)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (series_id, date) DO UPDATE
                        SET value      = EXCLUDED.value,
                            fetched_at = NOW();
                """, (indicator, series_id, row["date"], row["value"]))
        conn.commit()
