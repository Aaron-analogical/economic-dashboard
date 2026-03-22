"""
Macroeconomic Dashboard — Overview
Landing page with a snapshot of key indicators.
Navigate to detailed pages using the sidebar.
"""

import streamlit as st
from utils.helpers import FOOTER

st.set_page_config(
    page_title="Macro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.markdown("""
### Dashboard Info
- Data Source: **Federal Reserve Economic Data (FRED)**
- Update Frequency: Varies by series
- Last Update: Cached for 1 hour
""")

st.title("📊 Macroeconomic Dashboard")
st.markdown(
    "Track key U.S. economic indicators in one place. "
    "Use the sidebar to navigate to detailed pages."
)
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
    st.info("**📖 Data Dictionary**\n\nDefinitions, sources, frequency, units, and metadata for every indicator.")

st.markdown("---")
st.markdown(FOOTER, unsafe_allow_html=True)
