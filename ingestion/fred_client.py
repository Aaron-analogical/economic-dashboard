"""Minimal FRED API client (no Streamlit dependency)."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


def fetch_observations(series_id: str, start_date: str, end_date: str) -> list[tuple]:
    """Return [(date, value)] for a series. Missing values ('.') become None."""
    params = {
        "series_id": series_id,
        "api_key": os.environ["FRED_API_KEY"],
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date,
    }
    response = requests.get(FRED_BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    return [
        (obs["date"], None if obs["value"] == "." else float(obs["value"]))
        for obs in response.json().get("observations", [])
    ]
