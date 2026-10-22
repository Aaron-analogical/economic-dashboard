{% docs __overview__ %}
# US Economic Data Warehouse

ELT pipeline for 23 US macroeconomic indicators from the
[FRED API](https://fred.stlouisfed.org/) (Federal Reserve Bank of St. Louis).

**Flow:** Python extracts FRED observations into `raw.fred_observations`,
dbt cleans them (`staging`), resamples to a monthly grain and computes
period-over-period changes (`intermediate`), then publishes a star schema
(`analytics`) consumed by a Power BI report.

| Layer | Schema | Materialization |
|---|---|---|
| Source | `raw` | table loaded by `ingestion/load_raw.py` |
| Staging / intermediate | `staging` | view |
| Marts | `analytics` | table |

Indicator metadata (category, unit, transform) lives in the `indicators` seed,
which is also the list of series the extractor loads.
{% enddocs %}
