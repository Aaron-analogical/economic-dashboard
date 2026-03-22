"""
Macroeconomic Dashboard — Overview
Landing page with a snapshot of key indicators.
Navigate to detailed pages using the sidebar.
"""

import streamlit as st
from utils.helpers import (
    ECONOMIC_INDICATORS, YOY_INDICATORS, render_metric,
    fetch_fred_data, compute_yoy_change,
    create_time_series_chart, render_sidebar_dates, FOOTER
)

st.set_page_config(
    page_title="Macro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

start_str, end_str = render_sidebar_dates()

st.title("📊 Macroeconomic Dashboard")
st.markdown(
    "Track key U.S. economic indicators in one place. "
    "Use the sidebar to navigate to detailed pages."
)
st.markdown("---")
st.subheader("🔑 Key Indicators Snapshot")

overview_indicators = {
    "GDP": "A191RL1Q225SBEA",
    "Unemployment Rate": "UNRATE",
    "Inflation (CPI)": "CPIAUCSL",
    "Federal Funds Rate": "FEDFUNDS",
    "S&P 500": "SP500",
    "VIX Volatility Index": "VIXCLS",
}

cols = st.columns(6)
for i, (name, series_id) in enumerate(overview_indicators.items()):
    df = fetch_fred_data(series_id, start_str, end_str)
    if name in YOY_INDICATORS:
        df = compute_yoy_change(df)
    label = f"{name} (YoY %)" if name in YOY_INDICATORS else name
    with cols[i]:
        render_metric(name, label, df)

st.markdown("---")
st.subheader("📂 Pages")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.info("**📈 US Indicators**\n\nDetailed charts and trends for all 23 economic indicators across 7 categories.")
with c2:
    st.info("**🔄 Comparisons**\n\nNormalized multi-series charts to compare indicators side by side.")
with c3:
    st.info("**📋 Data Export**\n\nView raw data tables and download CSV files for any indicator.")
with c4:
    st.info("**📖 Data Dictionary**\n\nDefinitions, sources, units, and metadata for every indicator.")

st.markdown("---")
st.markdown(FOOTER, unsafe_allow_html=True)
