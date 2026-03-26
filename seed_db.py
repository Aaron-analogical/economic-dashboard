"""
seed_db.py — Fetch every FRED indicator and store it in PostgreSQL.

Usage:
    python seed_db.py
"""

import sys
from datetime import date
from utils.helpers import fetch_fred_data, ECONOMIC_INDICATORS
from utils.db import init_tables, upsert_series

START_DATE = "2000-01-01"
END_DATE = date.today().isoformat()


def main():
    print("Initialising database table...")
    init_tables()
    print(f"Seeding {len(ECONOMIC_INDICATORS)} indicators from {START_DATE} to {END_DATE}\n")

    success, skipped = 0, 0
    for name, series_id in ECONOMIC_INDICATORS.items():
        df = fetch_fred_data(series_id, START_DATE, END_DATE)
        if df.empty:
            print(f"  SKIP  {name} ({series_id}) — no data returned")
            skipped += 1
            continue
        upsert_series(name, series_id, df)
        print(f"  OK    {name} ({series_id}) — {len(df)} rows saved")
        success += 1

    print(f"\nDone. {success} saved, {skipped} skipped.")


if __name__ == "__main__":
    main()
