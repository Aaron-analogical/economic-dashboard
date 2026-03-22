"""Data Export — View raw data tables and download as CSV."""

import streamlit as st
from utils.helpers import (
    ECONOMIC_INDICATORS, YOY_INDICATORS,
    fetch_fred_data, compute_yoy_change,
    render_sidebar_dates, FOOTER
)

st.set_page_config(page_title="Data Export", page_icon="📋", layout="wide")

start_str, end_str = render_sidebar_dates()

st.title("📋 Data Export")
st.markdown("View raw data tables and download CSV files for any indicator.")
st.markdown("---")

selected = st.selectbox("Select an indicator:", list(ECONOMIC_INDICATORS.keys()))

series_id = ECONOMIC_INDICATORS[selected]
df = fetch_fred_data(series_id, start_str, end_str)

# YoY toggle for applicable series
if selected in YOY_INDICATORS:
    view_mode = st.radio(
        "Display mode:", ["Raw Values", "Year-over-Year %"], horizontal=True
    )
    if view_mode == "Year-over-Year %":
        df = compute_yoy_change(df)

st.markdown("---")

if df.empty:
    st.warning("No data available for the selected indicator and date range.")
else:
    display_df = df.rename(columns={"date": "Date", "value": selected})
    st.dataframe(display_df, use_container_width=True)

    csv = display_df.to_csv(index=False).encode("utf-8")
    filename = f"{selected.replace(' ', '_').lower()}_{start_str}_{end_str}.csv"
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
    )
    st.caption(f"FRED Series ID: `{series_id}` · {len(df):,} observations")

st.markdown("---")
st.markdown(FOOTER, unsafe_allow_html=True)
