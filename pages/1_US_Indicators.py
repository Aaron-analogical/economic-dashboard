"""US Economic Indicators — Detailed charts for all FRED indicators."""

import streamlit as st
from utils.helpers import (
    ECONOMIC_INDICATORS, YOY_INDICATORS, QOQ_INDICATORS, UNITS, render_metric,
    fetch_fred_data, compute_yoy_change,
    create_time_series_chart, render_sidebar_dates, FOOTER
)

st.set_page_config(page_title="US Indicators", page_icon="📈", layout="wide")

start_str, end_str = render_sidebar_dates()

st.title("📈 US Economic Indicators")
st.markdown("Detailed charts and trends across 7 categories of economic data.")
st.markdown("---")

INDICATOR_CATEGORIES = {
    "🏛️ Macroeconomic": ["GDP"],
    "👷 Labor Market": [
        "Unemployment Rate", "Labor Force Participation",
        "Initial Jobless Claims", "Non-Farm Payroll", "Unemployment (25+ years)",
    ],
    "📈 Inflation & Prices": ["Inflation (CPI)", "Core CPI", "Producer Price Index"],
    "🏦 Interest Rates": [
        "Federal Funds Rate", "10-Year Treasury Yield",
        "2-Year Treasury Yield", "30-Year Mortgage Rate",
    ],
    "🏠 Housing": ["Housing Starts", "Building Permits", "Home Prices (Case-Shiller)"],
    "🏭 Production & Business": [
        "Industrial Production", "ISM Manufacturing PMI",
        "Retail Sales", "Consumer Disposable Income",
    ],
    "📊 Markets": ["S&P 500", "VIX Volatility Index", "USD Index"],
}


cat_tabs = st.tabs(list(INDICATOR_CATEGORIES.keys()))
for tab, (category, names) in zip(cat_tabs, INDICATOR_CATEGORIES.items()):
    with tab:
        # Pre-fetch all data for this category
        category_data = {}
        for name in names:
            series_id = ECONOMIC_INDICATORS[name]
            df = fetch_fred_data(series_id, start_str, end_str)
            display_df = compute_yoy_change(df) if name in YOY_INDICATORS else df
            if name in QOQ_INDICATORS:
                label = f"{name} (QoQ %)"
            elif name in YOY_INDICATORS:
                label = f"{name} (YoY %)"
            else:
                label = name
            category_data[name] = {"df": display_df, "label": label}

        # All KPI metric cards in one row at the top
        kpi_cols = st.columns(len(names))
        for col, name in zip(kpi_cols, names):
            data = category_data[name]
            with col:
                render_metric(name, data["label"], data["df"])

        st.markdown("---")

        # All charts below, in the same order
        for name in names:
            data = category_data[name]
            st.plotly_chart(
                create_time_series_chart(data["df"], data["label"], UNITS.get(name, "Value")),
                use_container_width=True,
            )
            st.markdown("---")

st.markdown(FOOTER, unsafe_allow_html=True)
