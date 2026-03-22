"""Comparisons — Normalized multi-series charts for side-by-side comparison."""

import streamlit as st
from utils.helpers import (
    ECONOMIC_INDICATORS,
    fetch_fred_data, create_comparison_chart,
    render_sidebar_dates, FOOTER
)

st.set_page_config(page_title="Comparisons", page_icon="🔄", layout="wide")

start_str, end_str = render_sidebar_dates()

st.title("🔄 Indicator Comparisons")
st.markdown(
    "Compare multiple indicators normalized to a common base "
    "(100 = start of selected period). Useful for spotting correlations and cycles."
)
st.markdown("---")

all_names = list(ECONOMIC_INDICATORS.keys())
selected = st.multiselect(
    "Select indicators to compare:",
    options=all_names,
    default=["GDP", "S&P 500"],
)

if len(selected) < 2:
    st.info("Please select at least 2 indicators to compare.")
else:
    with st.spinner("Fetching data..."):
        data_dict = {}
        for name in selected:
            df = fetch_fred_data(ECONOMIC_INDICATORS[name], start_str, end_str)
            if not df.empty:
                data_dict[name] = df

    if data_dict:
        title = f"Comparison: {', '.join(data_dict.keys())}"
        st.plotly_chart(create_comparison_chart(data_dict, title), use_container_width=True)
        st.caption(
            "Note: All series are indexed to 100 at the start of the selected date range. "
            "Series with different native units are therefore directly comparable."
        )
    else:
        st.warning("No data available for the selected indicators in the chosen date range.")

st.markdown("---")
st.markdown(FOOTER, unsafe_allow_html=True)
