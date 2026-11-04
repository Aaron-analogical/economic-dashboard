from unittest.mock import patch

import pytest
import requests

from ingestion.fred_client import fetch_observations
from tests.conftest import fake_response


@pytest.fixture(autouse=True)
def api_key(monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "test-key")


def test_parses_values_and_missing_dot():
    payload = {"observations": [{"date": "2026-09-01", "value": "4.2"},
                                {"date": "2026-10-01", "value": "."}]}
    with patch("ingestion.fred_client.requests.get", return_value=fake_response(payload)) as get:
        rows = fetch_observations("UNRATE", "2000-01-01", "2026-11-01")

    assert rows == [("2026-09-01", 4.2), ("2026-10-01", None)]
    params = get.call_args.kwargs["params"]
    assert params["series_id"] == "UNRATE"
    assert params["api_key"] == "test-key"
    assert params["observation_start"] == "2000-01-01"


def test_no_observations_key_returns_empty_list():
    with patch("ingestion.fred_client.requests.get", return_value=fake_response({})):
        assert fetch_observations("UNRATE", "2000-01-01", "2026-11-01") == []


def test_http_error_propagates():
    with patch("ingestion.fred_client.requests.get", return_value=fake_response({}, status_code=400)):
        with pytest.raises(requests.HTTPError):
            fetch_observations("BAD", "2000-01-01", "2026-11-01")


def test_missing_api_key_fails_fast(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY")
    with pytest.raises(KeyError):
        fetch_observations("UNRATE", "2000-01-01", "2026-11-01")
