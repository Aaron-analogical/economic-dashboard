# US Economic Data Warehouse

End-to-end analytics engineering project on 23 US macroeconomic indicators from the Federal Reserve [FRED API](https://fred.stlouisfed.org/): a Python extractor loads raw data into PostgreSQL (Neon), dbt models it into a tested star schema, and a Power BI report (PBIP, version-controlled) sits on top. Runs daily on GitHub Actions.

## Architecture

```
FRED API ──► ingestion/ (Python EL) ──► raw.fred_observations
                                              │
                                    dbt  ┌────┴─────────────────────────────┐
                                         │ staging       stg_fred__observations
                                         │ intermediate  monthly resampling, YoY / period changes
                                         │ analytics     dim_indicator, dim_date,
                                         │               fct_observations, fct_indicator_monthly
                                         └────┬─────────────────────────────┘
                                              │
                                   Power BI PBIP (Import, star schema, DAX measures)

GitHub Actions: daily 07:00 UTC  →  load_raw  →  dbt source freshness  →  dbt build
                push to main     →  dbt docs generate  →  GitHub Pages
```

## Stack

| Layer | Technology |
|---|---|
| Source | FRED API (Federal Reserve Bank of St. Louis) |
| Extract & load | Python, `requests`, `psycopg2` (batch upsert) |
| Warehouse | PostgreSQL on Neon (serverless) |
| Transformation | dbt Core 1.12 + `dbt_utils` |
| Data quality | dbt tests (unique, not_null, relationships, accepted_values, range) and source freshness |
| BI | Power BI Desktop, PBIP format (TMDL semantic model + PBIR report) |
| Orchestration | GitHub Actions |
| Documentation | dbt docs on GitHub Pages |

## Data model

| Model | Grain | Description |
|---|---|---|
| `dim_indicator` | series | Name, category, units, frequency, transform, FRED link, data coverage |
| `dim_date` | day | Calendar 2000 → end of current year (Power BI date table) |
| `fct_observations` | series × native date | Raw-frequency values (daily markets, weekly claims, …) |
| `fct_indicator_monthly` | series × month | Harmonised monthly values with period-over-period and YoY changes |

Modelling choices:

- **One monthly grain for comparisons.** Daily and weekly series are averaged per month in dbt, so every indicator can be compared on the same axis without DAX workarounds.
- **YoY computed in the warehouse, not in DAX.** Year-ago values are joined on the calendar (`month - 12 months`), not with `lag(12)`, so a missing month never shifts the comparison window.
- **`display_value`.** Price indices and volumes are reported as YoY %, rates and levels as-is. The rule is held in the `transform` column of the `indicators` seed.
- **The seed is the single source of truth.** `dbt/seeds/indicators.csv` drives both the extractor (which series to load) and `dim_indicator`.
- **Separate dev and prod schemas.** The `prod` target writes to `staging` and `analytics`. Any other target writes to `<schema>_staging` and `<schema>_analytics`, so development never touches what Power BI reads.

## Repository layout

```
ingestion/          FRED client + raw loader (python -m ingestion.load_raw)
dbt/                dbt project: seeds, models (staging / intermediate / marts), tests, macros
powerbi/            EconomicDashboard.pbip (TMDL semantic model + report)
.github/workflows/  pipeline.yml (daily EL + dbt build), docs.yml (dbt docs → Pages)
Home.py, pages/     Streamlit app (reads FRED directly, independent of the warehouse)
```

## Setup

### Prerequisites

- Python 3.10+
- A FRED API key ([free registration](https://fred.stlouisfed.org/docs/api/api_key.html))
- A PostgreSQL database reachable from the internet (e.g. a free [Neon](https://neon.tech) project)
- Power BI Desktop (for the report)

### Install

```powershell
git clone https://github.com/Aaron-analogical/economic-dashboard.git
cd economic-dashboard
python -m venv .venv-pipeline
.venv-pipeline\Scripts\activate
pip install -r requirements-pipeline.txt
copy .env.example .env   # then fill in FRED_API_KEY and DB_* values
```

The pipeline runs in its own virtual environment because dbt and Streamlit need conflicting `protobuf` versions.

### Run the pipeline locally

```bash
python -m ingestion.load_raw          # extract & load raw.fred_observations

cd dbt
set -a; source ../.env; set +a        # dbt reads credentials from env vars (Git Bash)
dbt deps --profiles-dir .
dbt build --profiles-dir .            # dev target → dbt_dev_staging / dbt_dev_analytics
dbt build --profiles-dir . --target prod
dbt docs generate --profiles-dir . && dbt docs serve --profiles-dir .
```

In PowerShell, load the variables with `Get-Content ..\.env | ForEach-Object { if ($_ -match '^([^#=]+)=(.*)$') { Set-Item "env:$($matches[1])" $matches[2] } }`.

### GitHub Actions

1. Add the repository secrets `FRED_API_KEY`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.
2. *Settings → Pages → Source: GitHub Actions* to publish the dbt docs.
3. `Data Pipeline` runs daily at 07:00 UTC and can be triggered manually. `dbt Docs` runs on every push to `main` that touches `dbt/`.

### Power BI

1. Open `powerbi/EconomicDashboard.pbip` in Power BI Desktop.
2. *Transform data → Edit parameters*: set `PgHost` (Neon host) and `PgDatabase`.
3. *Refresh*. When prompted, choose **Database** authentication with your Neon user and password. Credentials are stored locally and never written to the project files.

The semantic model includes these measures:

- `Latest Value`, `Previous Value`, `Change vs Previous` and `Latest YoY %`, for KPI cards.
- `10Y-2Y Spread`, the slope of the yield curve. A negative value means the curve is inverted.
- `Real Fed Funds Rate`: the Fed Funds rate minus CPI inflation (YoY).
- `Display Value` and `Native Value`, for time-series charts. `Selected Unit` provides dynamic titles.

## Indicators

| Category | Indicators |
|---|---|
| Macroeconomic | Real GDP growth |
| Labor Market | Unemployment rate, labor force participation, initial jobless claims, nonfarm payrolls, unemployment rate (men 20+) |
| Inflation & Prices | CPI, core CPI, PCE price index, PPI (all commodities) |
| Interest Rates | Fed Funds rate, 2Y and 10Y Treasury yields, 30Y mortgage rate |
| Housing | Housing starts, building permits, Case-Shiller home prices |
| Production & Business | Industrial production, retail sales, disposable personal income |
| Markets | S&P 500, VIX, broad USD index |

The full list with FRED series IDs and units is in [dbt/seeds/indicators.csv](dbt/seeds/indicators.csv).

## Streamlit app

The original Streamlit app is still in the repository. It queries FRED directly and does not depend on the warehouse.

```bash
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```
