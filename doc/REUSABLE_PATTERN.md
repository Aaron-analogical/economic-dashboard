# Reusable Pattern: API → PostgreSQL → Power BI

This document explains how to replicate the end-to-end analytics pipeline built in `economic-dashboard` on any new Python + PostgreSQL + Power BI project.

---

## Overview

```
External API  →  Python (fetch + transform)  →  PostgreSQL  →  Power BI
```

The pipeline has three responsibilities:
1. **Fetch** data from an external API into a pandas DataFrame
2. **Persist** it into PostgreSQL via an upsert (safe to re-run without duplicates)
3. **Visualise** it in Power BI by connecting directly to the database

---

## Prerequisites

### Software
| Tool | Version | Notes |
|---|---|---|
| Python | 3.10+ | With `venv` |
| PostgreSQL | 17 | Windows service `postgresql-x64-17`, port 5432 |
| pgAdmin 4 | Any | For DB admin / SQL queries |
| Power BI Desktop | Latest | Requires npgsql driver (see below) |

### Python packages
```
psycopg2-binary
python-dotenv
pandas
requests
```
Install with:
```bash
pip install psycopg2-binary python-dotenv pandas requests
```

### Power BI — npgsql driver
Power BI requires the npgsql driver to connect to PostgreSQL.
Download the `.msi` from https://github.com/npgsql/npgsql/releases and install it, then restart Power BI Desktop.

---

## Step 1 — PostgreSQL setup

### 1a. Create the database
Open pgAdmin or run in a terminal (with `psql` in PATH):
```sql
CREATE DATABASE <your_project_db>;
```

### 1b. Grant permissions to your user
```sql
GRANT ALL ON SCHEMA public TO <your_user>;
GRANT CREATE ON DATABASE <your_project_db> TO <your_user>;
```

> In this project: database = `test`, user = `aaron`.

### 1c. Add psql to PATH (Windows, one-time)
If `psql` is not found in terminal:
```powershell
setx PATH "$env:PATH;C:\Program Files\PostgreSQL\17\bin"
```
Restart the terminal after running this.

---

## Step 2 — Environment file

Create a `.env` file at the project root. **Never commit this file.**

```dotenv
# API credentials
MY_API_KEY=your_key_here

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=<your_project_db>
DB_USER=<your_user>
DB_PASSWORD=<your_password>
```

Add `.env` to `.gitignore`:
```
.env
```

---

## Step 3 — Database utility (utils/db.py)

This file provides three functions used by the seeding script.
Copy it as-is and adjust the `CREATE TABLE` schema to match your data shape.

```python
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def init_tables():
    """Create tables if they don't exist yet."""
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
                    UNIQUE (series_id, date)          -- prevents duplicate rows on re-run
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
```

**Key design decisions:**
- `UNIQUE (series_id, date)` — the conflict key. Adjust to match your natural key.
- `ON CONFLICT ... DO UPDATE` — safe idempotent upsert. Re-running the seed script updates values and timestamps without creating duplicates.
- All DB credentials come from `.env` via `python-dotenv`.

---

## Step 4 — Data fetch function (utils/helpers.py)

Your fetch function should return a pandas DataFrame with at minimum the columns your upsert function expects (`date`, `value` in this example).

```python
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("MY_API_KEY", "")

def fetch_data(series_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch time-series data from your API. Returns DataFrame with [date, value]."""
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
    observations = response.json().get("observations", [])

    df = pd.DataFrame(observations)
    df = df[df["value"] != "."]  # drop missing values (FRED convention)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"])
    return df[["date", "value"]].sort_values("date").reset_index(drop=True)
```

> For the FRED API specifically: base URL is `https://api.stlouisfed.org/fred/series/observations`. Get a free key at https://fred.stlouisfed.org/.

---

## Step 5 — Seeding script (seed_db.py)

Place at the project root. Run this manually (or on a schedule) to populate/refresh the DB.

```python
"""
seed_db.py — Fetch all indicators and store them in PostgreSQL.
Usage: python seed_db.py
"""
from datetime import date
from utils.helpers import fetch_data, MY_INDICATORS  # adapt to your module names
from utils.db import init_tables, upsert_series

START_DATE = "2000-01-01"
END_DATE = date.today().isoformat()

# Dict of { "Human Name": "API_SERIES_ID" }
MY_INDICATORS = {
    "GDP": "A191RL1Q225SBEA",
    "Unemployment Rate": "UNRATE",
    # ... add all your series here
}


def main():
    print("Initialising database table...")
    init_tables()
    print(f"Seeding {len(MY_INDICATORS)} indicators from {START_DATE} to {END_DATE}\n")

    success, skipped = 0, 0
    for name, series_id in MY_INDICATORS.items():
        df = fetch_data(series_id, START_DATE, END_DATE)
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
```

Run it:
```bash
python seed_db.py
```

---

## Step 6 — Connect Power BI

1. Open Power BI Desktop
2. **Home → Get Data → PostgreSQL database**
3. Fill in:
   - **Server:** `localhost` (or `127.0.0.1` if localhost fails)
   - **Database:** `<your_project_db>` ← the database name, not the table
4. Click **OK**
5. When prompted for credentials:
   - Select **Database** authentication
   - Username: your DB user
   - Password: your DB password
6. In the Navigator, expand the database → select your table → **Load**

> If you get a driver error, install npgsql (see Prerequisites above).

---

## Folder Structure

```
my-project/
├── .env                  # credentials — never commit
├── .gitignore
├── requirements.txt
├── seed_db.py            # run to populate the DB
├── utils/
│   ├── __init__.py
│   ├── db.py             # get_connection, init_tables, upsert_series
│   └── helpers.py        # fetch_data, MY_INDICATORS dict
└── pages/                # Streamlit pages (if building a dashboard app)
```

---

## Checklist for a New Project

- [ ] Create new PostgreSQL database and grant permissions to user
- [ ] Copy `.env` template and fill in credentials
- [ ] Add `.env` to `.gitignore`
- [ ] Copy `utils/db.py` and adjust the `CREATE TABLE` schema
- [ ] Write `fetch_data()` in `utils/helpers.py` returning `[date, value]` DataFrame
- [ ] Build `MY_INDICATORS` dict mapping names to API series IDs
- [ ] Copy `seed_db.py` and update imports/indicator dict
- [ ] Run `pip install psycopg2-binary python-dotenv pandas requests`
- [ ] Run `python seed_db.py` — verify all indicators show `OK`
- [ ] Open pgAdmin → Query Tool → `SELECT COUNT(*) FROM your_table;` to confirm
- [ ] Connect Power BI Desktop to the database
- [ ] Install npgsql driver if Power BI shows a connector error

---

## Step 7 — Scheduling (automated refresh)

### Comparison

| | Option A: GitHub Actions | Option B: Task Scheduler | Option C: Airflow |
|---|---|---|---|
| Reaches `localhost` DB | Yes (self-hosted runner only) | Yes | Yes |
| Setup complexity | Medium | Low | High |
| Monitoring UI | GitHub Actions UI | None | Rich web UI |
| Retries on failure | Yes | No | Yes |
| Multi-pipeline support | Per-repo workflows | Multiple tasks | Single dashboard |
| Resource usage | Lightweight agent | None | ~500MB RAM (server) |
| Best for | Git-integrated projects | Single simple scripts | 3+ pipelines |

---

### Option A: GitHub Actions with a self-hosted runner

> Cloud-hosted GitHub runners cannot reach `localhost`. You must register your own machine as a self-hosted runner.

#### 1. Install the self-hosted runner (one-time)
1. Go to your GitHub repo → **Settings → Actions → Runners → New self-hosted runner**
2. Select **Windows / x64**
3. Follow the displayed PowerShell commands to download and register the agent
4. Install it as a Windows service so it survives reboots:
   ```powershell
   cd C:\actions-runner
   .\svc.ps1 install
   .\svc.ps1 start
   ```

#### 2. Add secrets to GitHub
Go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret name | Value |
|---|---|
| `FRED_API_KEY` | your FRED key |
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `DB_NAME` | your database name |
| `DB_USER` | your DB username |
| `DB_PASSWORD` | your DB password |

#### 3. The workflow file
Already created at `.github/workflows/seed.yml`. Default schedule: **every Sunday at 06:00 UTC**.

To change frequency, edit the `cron` expression:
```yaml
- cron: "0 6 * * 0"   # every Sunday 06:00 UTC
- cron: "0 6 * * *"   # every day 06:00 UTC
- cron: "0 6 1 * *"   # 1st of every month
```

Use https://crontab.guru to build cron expressions.

You can also trigger manually anytime: **GitHub → Actions → Seed Economic Data → Run workflow**.

#### 4. Updated folder structure
```
my-project/
├── .github/
│   └── workflows/
│       └── seed.yml      # scheduled GitHub Actions workflow
├── .env                  # local only — never commit
...
```

---

### Option B: Windows Task Scheduler

The simplest option — no extra software, no GitHub integration needed.

1. Open **Task Scheduler** → **Create Basic Task**
2. **Name:** `Seed Economic Data`
3. **Trigger:** Weekly (or Daily / Monthly)
4. **Action:** Start a program
   - Program: `C:\Users\Admin\OneDrive\Documents\Github\economic-dashboard\venv\Scripts\python.exe`
   - Arguments: `seed_db.py`
   - Start in: `C:\Users\Admin\OneDrive\Documents\Github\economic-dashboard`
5. Click **Finish**

The script will run automatically on schedule with no monitoring UI. Check the PostgreSQL table row counts or add logging to a file inside `seed_db.py` if you want an audit trail.

---

### Option C: Apache Airflow

Best choice when managing **multiple pipelines** across projects. Airflow runs as a local server, so it can reach `localhost` without any special configuration.

#### 1. Install Airflow
```bash
pip install apache-airflow
airflow db init
airflow standalone   # starts webserver + scheduler, visit http://localhost:8080
```

#### 2. Create a DAG
Save this file as `dags/seed_economic_data.py` inside your Airflow home (default: `~/airflow/dags/`):

```python
from airflow.decorators import dag, task
from datetime import datetime
import subprocess

PROJECT_DIR = r"C:\Users\Admin\OneDrive\Documents\Github\economic-dashboard"
PYTHON_EXE = rf"{PROJECT_DIR}\venv\Scripts\python.exe"

@dag(
    schedule="0 6 * * 0",        # every Sunday at 06:00
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["economic-dashboard"],
)
def seed_economic_data():

    @task
    def run_seed():
        result = subprocess.run(
            [PYTHON_EXE, "seed_db.py"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)

    run_seed()

seed_economic_data()
```

#### 3. Start Airflow as a Windows service (optional, for auto-start on reboot)
```powershell
pip install pywin32
python -m airflow webserver --daemon
python -m airflow scheduler --daemon
```

Or run `airflow standalone` manually before each session.

#### 4. Monitor runs
Open http://localhost:8080 → find `seed_economic_data` → toggle it ON → view logs, run history, and manual triggers from the UI.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `psql` not found in terminal | `setx PATH "$env:PATH;C:\Program Files\PostgreSQL\17\bin"` then restart terminal |
| `InsufficientPrivilege` on seed | `GRANT ALL ON SCHEMA public TO <user>;` in pgAdmin |
| Power BI driver error | Install npgsql `.msi` from GitHub, restart Power BI |
| Power BI can't resolve `localhost` | Use `127.0.0.1` instead |
| Duplicate rows on re-seed | Check `UNIQUE` constraint and `ON CONFLICT` clause in `db.py` |
| `psycopg2` import error | `pip install psycopg2-binary` (not `psycopg2`) on Windows |
| GitHub Actions can't connect to DB | Runner must be self-hosted — cloud runners can't reach localhost |
| Self-hosted runner offline | Run `.\svc.ps1 start` in `C:\actions-runner` or check Windows Services |
| Airflow DAG not appearing in UI | Check `~/airflow/dags/` path; run `airflow dags list` to diagnose |
| Airflow import error on Windows | Use `airflow standalone` instead of separate webserver/scheduler commands |
