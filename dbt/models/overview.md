{% docs __overview__ %}
# Economic Data Warehouse

ELT pipeline with two sources:

- **FRED** (Federal Reserve Bank of St. Louis): 23 US macroeconomic indicators,
  daily to quarterly, for the US deep-dive pages.
- **World Bank**: 7 annual indicators for 10 countries (G7 + China, India,
  Brazil), for the country comparison.

**Flow:** Python extractors load each API into `raw` and log every run in
`raw.ingestion_runs`. dbt cleans the data (`staging`), resamples FRED to a
monthly grain (`intermediate`), then publishes star schemas and a pipeline
health report (`analytics`) consumed by a Power BI report.

| Layer | Schema | Materialization |
|---|---|---|
| Source | `raw` | tables loaded by `ingestion/load_raw.py` and `ingestion/load_worldbank.py` |
| Staging / intermediate | `staging` | view |
| Marts | `analytics` | table |

Indicator and country metadata live in the `indicators`, `wb_indicators` and
`countries` seeds, which are also the lists the extractors load.
{% enddocs %}
