"""Shared fixtures. Tests never call the real APIs or the database."""

from unittest.mock import MagicMock

import pytest


def fake_response(payload, status_code=200):
    """Stand-in for requests.Response with .json() and .raise_for_status()."""
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    if status_code >= 400:
        import requests
        response.raise_for_status.side_effect = requests.HTTPError(f"{status_code} error")
    return response


@pytest.fixture
def no_sleep(monkeypatch):
    """Skip the retry back-off in the World Bank client."""
    monkeypatch.setattr("ingestion.worldbank_client.time.sleep", lambda _: None)
