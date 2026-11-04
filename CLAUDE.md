# CLAUDE.md

Portfolio project for data analytics / analytics engineering roles: FRED + World Bank APIs → Python EL (`ingestion/`) → Neon Postgres (`raw`) → dbt (`dbt/`) → Power BI PBIP (`powerbi/`). Daily run on GitHub Actions; dbt docs on GitHub Pages. The audience is recruiters and hiring managers: favour clean, readable output over economic depth.

The author keeps local-only notes and generator scripts in `.local/` (excluded from Git). If it exists, read `.local/STATUS.md` first when resuming: it holds the current status and next steps.

## Commands

```bash
.venv-pipeline/Scripts/python.exe -m pytest                  # unit tests, no key or DB needed
.venv-pipeline/Scripts/python.exe -m ingestion.load_raw      # FRED → raw.fred_observations
.venv-pipeline/Scripts/python.exe -m ingestion.load_worldbank

cd dbt && set -a && source ../.env && set +a                 # dbt reads credentials from env vars
../.venv-pipeline/Scripts/dbt.exe build --profiles-dir .                # dev → dbt_dev_*
../.venv-pipeline/Scripts/dbt.exe build --profiles-dir . --target prod  # prod → staging / analytics
```

Run Python modules from the repo root (`python -m ingestion.…`), not from `dbt/`.

## Rules

- **Never commit the real Neon host.** `powerbi/EconomicDashboard.SemanticModel/definition/expressions.tmdl` is `skip-worktree`; in Git `PgHost` stays `your-endpoint.neon.tech`.
- **Power BI Desktop must be closed** before editing PBIP files, or its next save overwrites the edits. Check with `Get-Process PBIDesktop`.
- The report is also edited by hand in Desktop. Prefer patching the saved files directly. With the local generator, regenerate only the affected pages (`python .local/gen_pages.py powerbi/EconomicDashboard.Report "<Page name>"`): a full regeneration overwrites manual edits.
- The local model generator (`.local/gen_model_v2.py`) has already been applied: do not rerun it (it would duplicate tables and measures).
- Changes go through a branch and a PR to `main`. Commit only when asked.
- Dropping the old `economic_data` table in Neon needs explicit confirmation (irreversible).

## PBIP / TMDL pitfalls (learned the hard way)

- TMDL: `formatStringDefinition` is a child object; it must come **after** the measure's properties (`displayFolder`, `lineageTag`), or Desktop fails with "Invalid indentation".
- Format strings scale by 1,000 per comma placed **before** the decimal point: `$#,0,,,,.0"T"` → $30.8T. Commas after the decimals are printed literally. Set display units to None (`labelDisplayUnits` = 1) on visuals that use these formats.
- Action buttons: put `show` for `text` / `fill` / `outline` in an entry **without** a state selector; Desktop ignores it inside per-state entries.
- The custom theme pads every visual by 8 px; small visuals (nav buttons) need `padding` 0.
- Report-page tooltip on a visual: `visualTooltip.type` = `'Canvas'` (not `'ReportPage'`) plus `section` = tooltip page id.
- PBIP files are CRLF. Preserve line endings when editing with scripts (`sed -i` on Git Bash converts to LF).
- Power BI shifts `timestamptz` to local time: dbt exposes timestamps as UTC without time zone.
