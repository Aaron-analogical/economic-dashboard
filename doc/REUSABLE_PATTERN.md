# API → PostgreSQL → Power BI Pipeline

Portable pattern for building data pipelines that fetch from an external API, persist to PostgreSQL, and expose to Power BI. Extracted from `economic-dashboard` for reuse across projects.

---

## Architecture

```
External API  →  Python (fetch)  →  PostgreSQL  →  Power BI
                       ↑
              GitHub Actions (scheduled)
```

## Project Structure

```
project/
├── .env                        # credentials — never commit
├── .gitignore
├── requirements.txt
├── seed_db.py                  # pipeline entrypoint
├── .github/workflows/seed.yml  # scheduled trigger
└── utils/
    ├── db.py                   # connection + upsert
    └── helpers.py              # API client + series definitions
```

---

## Environment

`.env` schema:

```dotenv
API_KEY=your_key_here

DB_HOST=your_host
DB_PORT=5432
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_SSLMODE=require        # required for cloud databases (Neon, Supabase, etc.)
```

Always add `.env` to `.gitignore`.

---

## Database — utils/db.py

```python
import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE", "prefer"),
    )

def init_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS your_table (
                    id         SERIAL PRIMARY KEY,
                    series_id  TEXT NOT NULL,
                    date       DATE NOT NULL,
                    value      NUMERIC,
                    fetched_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE (series_id, date)
                );
            """)
        conn.commit()

def upsert_series(series_id: str, df):
    if df.empty:
        return
    rows = [(series_id, row["date"], row["value"]) for _, row in df.iterrows()]
    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO your_table (series_id, date, value)
                VALUES %s
                ON CONFLICT (series_id, date) DO UPDATE
                    SET value = EXCLUDED.value, fetched_at = NOW();
            """, rows)
        conn.commit()
```

**Design notes:**
- `UNIQUE (series_id, date)` is the conflict key — adjust to your natural key
- `execute_values` sends all rows in a single query — required for cloud-hosted databases that timeout on row-by-row inserts
- `ON CONFLICT ... DO UPDATE` makes the pipeline fully idempotent

---

## API Client — utils/helpers.py

Return a DataFrame with at minimum the columns consumed by `upsert_series`.

```python
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY", "")

def fetch_data(series_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    response = requests.get(
        "https://your-api.com/observations",
        params={
            "series_id": series_id,
            "observation_start": start_date,
            "observation_end": end_date,
            "api_key": API_KEY,
            "file_type": "json",
        },
        timeout=30,
    )
    response.raise_for_status()
    records = response.json().get("observations", [])
    df = pd.DataFrame(records)
    df = df[df["value"] != "."]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"])
    return df[["date", "value"]].sort_values("date").reset_index(drop=True)
```

---

## Pipeline Script — seed_db.py

```python
from datetime import date
from utils.helpers import fetch_data
from utils.db import init_tables, upsert_series

SERIES = {
    "Indicator Name": "API_SERIES_ID",
}

def main():
    init_tables()
    for name, sid in SERIES.items():
        df = fetch_data(sid, "2000-01-01", date.today().isoformat())
        if df.empty:
            print(f"  SKIP  {name}")
            continue
        upsert_series(sid, df)
        print(f"  OK    {name} — {len(df)} rows")

if __name__ == "__main__":
    main()
```

---

## Scheduling

### GitHub Actions (cloud DB — recommended)

`.github/workflows/seed.yml`:

```yaml
name: Seed Data

on:
  schedule:
    - cron: "0 7 * * *"   # daily 07:00 UTC
  workflow_dispatch:

jobs:
  seed:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python seed_db.py
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DB_HOST: ${{ secrets.DB_HOST }}
          DB_PORT: ${{ secrets.DB_PORT }}
          DB_NAME: ${{ secrets.DB_NAME }}
          DB_USER: ${{ secrets.DB_USER }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
          DB_SSLMODE: require
```

> For local PostgreSQL (`localhost`), use a **self-hosted runner** — cloud runners cannot reach localhost.

### Windows Task Scheduler (local DB)

- Program: `path\to\venv\Scripts\python.exe`  
- Arguments: `seed_db.py`  
- Start in: project root directory

### Apache Airflow (multiple pipelines)

```python
from airflow.decorators import dag, task
from datetime import datetime
import subprocess

@dag(schedule="0 7 * * *", start_date=datetime(2026, 1, 1), catchup=False)
def seed_pipeline():
    @task
    def run():
        subprocess.run(["python", "seed_db.py"], cwd="/path/to/project", check=True)
    run()

seed_pipeline()
```

---

## Power BI Connection

**Get Data → PostgreSQL database**

| Field | Value |
|---|---|
| Server | your DB host (use `127.0.0.1` for local if `localhost` fails) |
| Database | your database name |
| Authentication | Database |

For cloud databases (Neon, Supabase): SSL is handled automatically by the connector.  
For local PostgreSQL: install the [npgsql driver](https://github.com/npgsql/npgsql/releases) if Power BI shows a connector error.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `psycopg2` import error | `pip install psycopg2-binary` (not `psycopg2`) |
| Connection drops mid-insert | Use `execute_values` for batch inserts — not row-by-row |
| `InsufficientPrivilege` | `GRANT ALL ON SCHEMA public TO <user>;` |
| GitHub Actions can't reach DB | Use a cloud DB or a self-hosted runner for localhost |
| Power BI connector error | Install npgsql `.msi`, restart Power BI |
| Scheduled workflow disabled | GitHub disables schedules on repos inactive for 60 days — re-enable in Actions tab |
