"""Minimal World Bank Indicators API client (v2, no key required)."""

import time

import requests

WB_BASE_URL = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"


def _get(url: str, params: dict, retries: int = 3) -> list:
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            payload = response.json()
            # Errors come back as HTTP 200 with a single message element.
            if len(payload) < 2:
                raise ValueError(payload[0].get("message", payload))
            return payload
        except (requests.RequestException, ValueError):
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)


def fetch_indicator(indicator_code: str, countries: list[str],
                    start_year: int, end_year: int) -> list[tuple]:
    """Return [(iso3, year, value)] for one indicator across countries. Missing values are None."""
    url = WB_BASE_URL.format(countries=";".join(countries), indicator=indicator_code)
    params = {"format": "json", "date": f"{start_year}:{end_year}", "per_page": 1000, "page": 1}
    rows = []
    while True:
        meta, data = _get(url, params)
        rows += [
            (obs["countryiso3code"], int(obs["date"]), obs["value"])
            for obs in data or []
        ]
        if params["page"] >= meta["pages"]:
            return rows
        params["page"] += 1
