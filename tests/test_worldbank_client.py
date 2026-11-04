from unittest.mock import patch

import pytest
import requests

from ingestion.worldbank_client import fetch_indicator
from tests.conftest import fake_response


def obs(iso3, year, value):
    return {"countryiso3code": iso3, "date": str(year), "value": value}


def page(page_no, pages, data):
    return [{"page": page_no, "pages": pages}, data]


def test_parses_rows_and_keeps_missing_values():
    payload = page(1, 1, [obs("USA", 2024, 2.8), obs("FRA", 2024, None)])
    with patch("ingestion.worldbank_client.requests.get", return_value=fake_response(payload)) as get:
        rows = fetch_indicator("NY.GDP.MKTP.KD.ZG", ["USA", "FRA"], 2000, 2025)

    assert rows == [("USA", 2024, 2.8), ("FRA", 2024, None)]
    url = get.call_args.args[0]
    assert url.endswith("/country/USA;FRA/indicator/NY.GDP.MKTP.KD.ZG")
    assert get.call_args.kwargs["params"]["date"] == "2000:2025"


def test_follows_pagination():
    responses = [fake_response(page(1, 2, [obs("USA", 2024, 1.0)])),
                 fake_response(page(2, 2, [obs("USA", 2023, 2.0)]))]
    with patch("ingestion.worldbank_client.requests.get", side_effect=responses) as get:
        rows = fetch_indicator("X", ["USA"], 2000, 2025)

    assert rows == [("USA", 2024, 1.0), ("USA", 2023, 2.0)]
    assert get.call_count == 2


def test_empty_data_page_returns_no_rows():
    with patch("ingestion.worldbank_client.requests.get", return_value=fake_response(page(1, 1, None))):
        assert fetch_indicator("X", ["USA"], 2000, 2025) == []


def test_retries_transient_error_then_succeeds(no_sleep):
    responses = [requests.ConnectionError("reset"), fake_response(page(1, 1, [obs("JPN", 2024, 0.1)]))]
    with patch("ingestion.worldbank_client.requests.get", side_effect=responses) as get:
        rows = fetch_indicator("X", ["JPN"], 2000, 2025)

    assert rows == [("JPN", 2024, 0.1)]
    assert get.call_count == 2


def test_api_error_message_raises_after_retries(no_sleep):
    # The World Bank API reports errors as HTTP 200 with a single message element.
    error = [{"message": [{"id": "120", "value": "Invalid value"}]}]
    with patch("ingestion.worldbank_client.requests.get", return_value=fake_response(error)) as get:
        with pytest.raises(ValueError):
            fetch_indicator("BAD.CODE", ["USA"], 2000, 2025)
    assert get.call_count == 3


def test_http_error_raises_after_retries(no_sleep):
    with patch("ingestion.worldbank_client.requests.get", return_value=fake_response([], status_code=503)):
        with pytest.raises(requests.HTTPError):
            fetch_indicator("X", ["USA"], 2000, 2025)
