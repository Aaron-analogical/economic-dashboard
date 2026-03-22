import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY", "")
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

ECONOMIC_INDICATORS = {
    # Macroeconomic
    "GDP": "A191RL1Q225SBEA",
    # Labor Market
    "Unemployment Rate": "UNRATE",
    "Labor Force Participation": "CIVPART",
    "Initial Jobless Claims": "ICSA",
    "Non-Farm Payroll": "PAYEMS",
    "Unemployment (25+ years)": "LNU04000025",
    # Inflation & Prices
    "Inflation (CPI)": "CPIAUCSL",
    "Core CPI": "CPILFESL",
    "Producer Price Index": "PCEPI",
    # Interest Rates
    "Federal Funds Rate": "FEDFUNDS",
    "10-Year Treasury Yield": "DGS10",
    "2-Year Treasury Yield": "DGS2",
    "30-Year Mortgage Rate": "MORTGAGE30US",
    # Housing
    "Housing Starts": "HOUST",
    "Building Permits": "PERMIT",
    "Home Prices (Case-Shiller)": "CSUSHPISA",
    # Production & Business Activity
    "Industrial Production": "INDPRO",
    "ISM Manufacturing PMI": "MMNRNJ",
    "Retail Sales": "RSXFS",
    "Consumer Disposable Income": "DSPI",
    # Markets
    "S&P 500": "SP500",
    "VIX Volatility Index": "VIXCLS",
    "USD Index": "DTWEXBGS",
}

YOY_INDICATORS = {
    "Inflation (CPI)", "Core CPI", "Producer Price Index",
    "Industrial Production", "Retail Sales"
}

UNITS = {
    "GDP": "% Change (SAAR)",
    "Unemployment Rate": "Percent",
    "Labor Force Participation": "Percent",
    "Initial Jobless Claims": "Thousands",
    "Non-Farm Payroll": "Thousands of Persons",
    "Unemployment (25+ years)": "Percent",
    "Inflation (CPI)": "YoY %",
    "Core CPI": "YoY %",
    "Producer Price Index": "YoY %",
    "Federal Funds Rate": "Percent",
    "10-Year Treasury Yield": "Percent",
    "2-Year Treasury Yield": "Percent",
    "30-Year Mortgage Rate": "Percent",
    "Housing Starts": "Thousands of Units",
    "Building Permits": "Thousands of Units",
    "Home Prices (Case-Shiller)": "Index",
    "Industrial Production": "YoY %",
    "ISM Manufacturing PMI": "Index",
    "Retail Sales": "YoY %",
    "Consumer Disposable Income": "Billions of $",
    "S&P 500": "Index",
    "VIX Volatility Index": "Index",
    "USD Index": "Index",
}

_PCT_UNITS = {"Percent", "YoY %", "% Change (SAAR)"}

# Indicators where a positive value is unambiguously good (show green ▲ / red ▼)
POSITIVE_GREEN_INDICATORS = {"GDP", "Industrial Production", "Retail Sales"}


def fmt_value(val: float, indicator_name: str) -> str:
    """Format a metric value, appending '%' for percent-based indicators."""
    suffix = "%" if UNITS.get(indicator_name, "") in _PCT_UNITS else ""
    return f"{val:.2f}{suffix}"


def render_metric(name: str, label: str, df: pd.DataFrame) -> None:
    """Render a metric card.

    Indicators in POSITIVE_GREEN_INDICATORS show the value in green with ▲
    when positive, or red with ▼ when negative.
    All other indicators use a plain st.metric card.
    """
    if df.empty:
        st.metric(label=label, value="N/A")
        return
    val = df["value"].iloc[-1]
    date_str = df["date"].iloc[-1].strftime("%b %Y")
    formatted = fmt_value(val, name)
    if name in POSITIVE_GREEN_INDICATORS:
        color = "#09ab3b" if val >= 0 else "#ff2b2b"
        arrow = "▲" if val >= 0 else "▼"
        st.markdown(
            f"""<div style="padding:4px 0 8px 0;">
  <p style="margin:0 0 2px 0; font-size:0.875rem;">{label}</p>
  <p style="margin:0; font-size:2rem; font-weight:700; color:{color};">{arrow}&nbsp;{formatted}</p>
  <p style="margin:2px 0 0 0; font-size:0.75rem; opacity:0.6;">As of {date_str}</p>
</div>""",
            unsafe_allow_html=True,
        )
    else:
        st.metric(label=label, value=formatted, help=f"As of {date_str}")

FOOTER = """
<div style="text-align: center; color: gray; font-size: 12px;">
Data sourced from Federal Reserve Economic Data (FRED) •
<a href="https://fred.stlouisfed.org/">fred.stlouisfed.org</a>
</div>
"""


@st.cache_data(ttl=3600)
def fetch_fred_data(series_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    if not FRED_API_KEY:
        st.error("⚠️ FRED API Key not found. Please add it to your .env file.")
        return pd.DataFrame()
    try:
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date,
        }
        response = requests.get(FRED_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        observations = data.get("observations", [])
        df = pd.DataFrame(observations)
        if df.empty:
            return pd.DataFrame()
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])
        return df[["date", "value"]].sort_values("date")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data for {series_id}: {e}")
        return pd.DataFrame()


def compute_yoy_change(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["value"] = df["value"].pct_change(12) * 100
    return df.dropna(subset=["value"])


def create_time_series_chart(df: pd.DataFrame, title: str, yaxis_title: str) -> go.Figure:
    if df.empty:
        return go.Figure().add_annotation(text="No data available")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["value"],
        mode="lines",
        line=dict(color="#1f77b4", width=2),
        fill="tozeroy",
        fillcolor="rgba(31, 119, 180, 0.2)",
        name="Value",
        hovertemplate="%{x|%Y-%m-%d}<br>%{y:.2f}<extra></extra>"
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=yaxis_title,
        hovermode="x unified",
        template="plotly_white",
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig


def create_comparison_chart(data_dict: dict, title: str) -> go.Figure:
    fig = go.Figure()
    for name, df in data_dict.items():
        if df.empty:
            continue
        normalized_values = (df["value"] / df["value"].iloc[0]) * 100
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=normalized_values,
            mode="lines",
            name=name,
            hovertemplate=f"{name}<br>%{{x|%Y-%m-%d}}<br>%{{y:.2f}}<extra></extra>"
        ))
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Indexed (Base = 100)",
        hovermode="x unified",
        template="plotly_white",
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig


def render_sidebar_dates():
    """Render date pickers in the sidebar. Returns (start_str, end_str)."""
    st.sidebar.title("⚙️ Dashboard Settings")
    end_date = st.sidebar.date_input(
        "End Date", datetime.now(),
        min_value=datetime(1950, 1, 1), max_value=datetime.now()
    )
    start_date = st.sidebar.date_input(
        "Start Date", datetime.now() - timedelta(days=365 * 21),
        min_value=datetime(1950, 1, 1), max_value=end_date
    )
    if start_date > end_date:
        st.error("Start date must be before end date")
        st.stop()
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
### Dashboard Info
- Data Source: **Federal Reserve Economic Data (FRED)**
- Update Frequency: Varies by series
- Last Update: Cached for 1 hour
""")
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
