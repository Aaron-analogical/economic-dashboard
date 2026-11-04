"""Loader orchestration: failures are logged, other series still load, and the job exits 1."""

from unittest.mock import MagicMock

import pytest

from ingestion import load_raw, load_worldbank
from ingestion.db import run_status


@pytest.mark.parametrize("ok, failed, expected", [
    (7, 0, "success"),
    (6, 1, "partial"),
    (0, 7, "failed"),
])
def test_run_status(ok, failed, expected):
    assert run_status(ok, failed) == expected


@pytest.fixture
def fake_db(monkeypatch):
    """Replace every database call of both loaders; return the recorded calls."""
    calls = {"upserts": [], "runs": []}
    for module in (load_raw, load_worldbank):
        monkeypatch.setattr(module, "get_connection", MagicMock())
        monkeypatch.setattr(module, "init_raw_table", lambda conn: None)
        monkeypatch.setattr(module, "upsert_observations",
                            lambda conn, key, rows: calls["upserts"].append((key, rows)))
        monkeypatch.setattr(module, "log_run",
                            lambda conn, source, started_at, rows, ok, failed:
                            calls["runs"].append((source, rows, ok, failed)))
    return calls


def test_worldbank_one_failing_indicator(monkeypatch, fake_db):
    monkeypatch.setattr(load_worldbank, "read_column",
                        lambda csv_name, column: {"countries.csv": ["USA", "FRA"],
                                                  "wb_indicators.csv": ["GOOD", "BAD"]}[csv_name])

    def fetch(code, countries, start, end):
        if code == "BAD":
            raise ValueError("API error")
        return [("USA", 2024, 1.0), ("FRA", 2024, 2.0)]

    monkeypatch.setattr(load_worldbank, "fetch_indicator", fetch)

    with pytest.raises(SystemExit) as exit_info:
        load_worldbank.main()

    assert exit_info.value.code == 1
    assert [key for key, _ in fake_db["upserts"]] == ["GOOD"]
    assert fake_db["runs"] == [("worldbank", 2, 1, 1)]


def test_worldbank_all_ok_exits_cleanly(monkeypatch, fake_db):
    monkeypatch.setattr(load_worldbank, "read_column",
                        lambda csv_name, column: ["USA"] if csv_name == "countries.csv" else ["A", "B"])
    monkeypatch.setattr(load_worldbank, "fetch_indicator", lambda *args: [("USA", 2024, 1.0)])

    load_worldbank.main()

    assert fake_db["runs"] == [("worldbank", 2, 2, 0)]


def test_fred_reads_series_from_seed_and_logs_run(monkeypatch, fake_db):
    seen = []

    def fetch(series_id, start, end):
        seen.append(series_id)
        return [("2026-10-01", 1.0)]

    monkeypatch.setattr(load_raw, "fetch_observations", fetch)

    load_raw.main()

    # every series in dbt/seeds/indicators.csv is requested once
    assert len(seen) == len(set(seen)) > 0
    source, rows, ok, failed = fake_db["runs"][0]
    assert (source, rows, ok, failed) == ("fred", len(seen), len(seen), 0)
