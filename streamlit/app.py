"""
Macroeconomic Dashboard with FRED Data
========================================

This Streamlit app demonstrates key concepts:
- Page configuration and layout
- Session state for caching data
- Multiple columns and tabs for organization
- Real-time data fetching from APIs
- Interactive filtering and date ranges
- Charts for data visualization
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================================
# Must be the first Streamlit command in the app
st.set_page_config(
    page_title="Macro Dashboard",
    page_icon="📊",
    layout="wide",  # Use full width
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Key economic indicators and their FRED series IDs
ECONOMIC_INDICATORS = {
    "GDP": "A191RL1Q225SBEA",
    "Unemployment Rate": "UNRATE",
    "Inflation (CPI)": "CPIAUCSL",
    "Federal Funds Rate": "FEDFUNDS",
    "10-Year Treasury Yield": "DGS10",
    "S&P 500": "SP500",
    "USD Index": "DTWEXBGS",
    "Initial Jobless Claims": "ICSA"
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_fred_data(series_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch data from FRED API.
    
    Streamlit's @st.cache_data decorator improves performance by:
    - Caching function results
    - Reusing cached results on reruns (when user interacts)
    - ttl parameter specifies cache expiration (in seconds)
    
    Args:
        series_id: FRED series identifier
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        DataFrame with date and value columns
    """
    if not FRED_API_KEY:
        st.error("⚠️ FRED API Key not found. Please add it to your .env file.")
        return pd.DataFrame()
    
    try:
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date
        }
        
        response = requests.get(FRED_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        observations = data.get("observations", [])
        
        df = pd.DataFrame(observations)
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])
        
        return df[["date", "value"]].sort_values("date")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data for {series_id}: {e}")
        return pd.DataFrame()

def compute_yoy_change(df: pd.DataFrame) -> pd.DataFrame:
    """Compute year-over-year % change for monthly data (e.g. CPI → inflation rate)."""
    df = df.copy()
    df["value"] = df["value"].pct_change(12) * 100
    return df.dropna(subset=["value"])

def create_time_series_chart(df: pd.DataFrame, title: str, yaxis_title: str) -> go.Figure:
    """
    Create an interactive time series chart using Plotly.
    
    Plotly features demonstrated:
    - Interactive hover/zoom
    - Responsive design
    - Clean styling
    
    Args:
        df: DataFrame with 'date' and 'value' columns
        title: Chart title
        yaxis_title: Y-axis label
    
    Returns:
        Plotly Figure object
    """
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
    """
    Create a comparison chart with multiple series (normalized).
    
    Args:
        data_dict: Dictionary of {series_name: DataFrame}
        title: Chart title
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    for name, df in data_dict.items():
        if df.empty:
            continue
        
        # Normalize to base 100 for comparison
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

# ============================================================================
# SIDEBAR - USER INPUTS
# ============================================================================
# Streamlit's sidebar provides a clean way to organize user inputs

st.sidebar.title("⚙️ Dashboard Settings")

# Date range picker
end_date = st.sidebar.date_input("End Date", datetime.now(), min_value=datetime(1950, 1, 1))
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=365*30), min_value=datetime(1950, 1, 1))

# Validate dates
if start_date > end_date:
    st.error("Start date must be before end date")
    st.stop()

# Convert dates to string format for API
start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### Dashboard Info
- Data Source: **Federal Reserve Economic Data (FRED)**
- Update Frequency: Varies by series
- Last Update: Cached for 1 hour
""")

# ============================================================================
# MAIN CONTENT - TITLE & DESCRIPTION
# ============================================================================
st.title("📊 Macroeconomic Dashboard")
st.markdown("""
Track key U.S. economic indicators in real-time using data from the 
**Federal Reserve Economic Data (FRED)** API.
""")

# ============================================================================
# TAB-BASED LAYOUT
# ============================================================================
# Tabs are a great way to organize related content
tab1, tab2, tab3 = st.tabs(["📈 Key Indicators", "🔄 Comparisons", "📋 Data"])

# ============================================================================
# TAB 1: KEY INDICATORS
# ============================================================================
with tab1:
    st.subheader("Essential Economic Indicators")
    
    # Create columns for a grid layout
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch key metrics for display in metric cards
    indicators_to_show = ["Unemployment Rate", "Inflation (CPI)", 
                          "Federal Funds Rate", "10-Year Treasury Yield"]
    
    fetch_series = {
        "Unemployment Rate": "UNRATE",
        "Inflation (CPI)": "CPIAUCSL",
        "Federal Funds Rate": "FEDFUNDS",
        "10-Year Treasury Yield": "DGS10"
    }
    
    cols = [col1, col2, col3, col4]
    
    # Indicators that should be shown as year-over-year % change
    YOY_INDICATORS = {"Inflation (CPI)"}

    for i, (indicator, series_id) in enumerate(fetch_series.items()):
        df = fetch_fred_data(series_id, start_str, end_str)
        if indicator in YOY_INDICATORS:
            df = compute_yoy_change(df)
        if not df.empty:
            latest_value = df["value"].iloc[-1]
            latest_date = df["date"].iloc[-1].strftime("%Y-%m-%d")

            label = "Inflation Rate (YoY %)" if indicator in YOY_INDICATORS else indicator
            formatted_value = f"{latest_value:.2f}%" if indicator in YOY_INDICATORS else f"{latest_value:.2f}"

            # Use st.metric to display KPIs
            cols[i].metric(
                label=label,
                value=formatted_value,
                help=f"As of {latest_date}"
            )
    
    st.markdown("---")
    
    # Individual charts for main indicators
    st.subheader("Detailed Trends")
    
    chart_col1, chart_col2 = st.columns(2)
    
    # Unemployment Rate
    with chart_col1:
        df_unemployment = fetch_fred_data("UNRATE", start_str, end_str)
        fig = create_time_series_chart(df_unemployment, "Unemployment Rate (%)", "Rate (%)")
        st.plotly_chart(fig, width='stretch')
    
    # Federal Funds Rate
    with chart_col2:
        df_fed_rate = fetch_fred_data("FEDFUNDS", start_str, end_str)
        fig = create_time_series_chart(df_fed_rate, "Federal Funds Rate (%)", "Rate (%)")
        st.plotly_chart(fig, width='stretch')
    
    # CPI (Inflation)
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        df_cpi = fetch_fred_data("CPIAUCSL", start_str, end_str)
        df_cpi = compute_yoy_change(df_cpi)
        fig = create_time_series_chart(df_cpi, "CPI Inflation Rate (YoY %)", "% Change (YoY)")
        st.plotly_chart(fig, width='stretch')
    
    # 10-Year Treasury Yield
    with chart_col4:
        df_treasury = fetch_fred_data("DGS10", start_str, end_str)
        fig = create_time_series_chart(df_treasury, "10-Year Treasury Yield (%)", "Rate (%)")
        st.plotly_chart(fig, width='stretch')

# ============================================================================
# TAB 2: COMPARISONS
# ============================================================================
with tab2:
    st.subheader("Compare Economic Indicators")
    
    # Multi-select for indicator comparison
    selected_indicators = st.multiselect(
        "Select indicators to compare (normalized to base 100):",
        options=list(ECONOMIC_INDICATORS.keys()),
        default=["GDP", "S&P 500"]
    )
    
    if selected_indicators:
        # Fetch data for all selected indicators
        comparison_data = {}
        for indicator in selected_indicators:
            series_id = ECONOMIC_INDICATORS[indicator]
            df = fetch_fred_data(series_id, start_str, end_str)
            if not df.empty:
                comparison_data[indicator] = df
        
        if comparison_data:
            # Create and display comparison chart
            fig = create_comparison_chart(comparison_data, 
                                         "Normalized Comparison (Base = 100)")
            st.plotly_chart(fig, width='stretch')
            
            st.info("""
            **Note:** Values are normalized to a base of 100 at the start date 
            to allow meaningful comparison between indicators with different scales.
            """)
        else:
            st.warning("No data available for selected indicators")

# ============================================================================
# TAB 3: DATA TABLE
# ============================================================================
with tab3:
    st.subheader("Raw Data Export")
    
    # Select indicator for data export
    selected_indicator = st.selectbox(
        "Select an indicator to view/export data:",
        options=list(ECONOMIC_INDICATORS.keys())
    )
    
    series_id = ECONOMIC_INDICATORS[selected_indicator]
    df_data = fetch_fred_data(series_id, start_str, end_str)
    
    if not df_data.empty:
        st.write(f"**{selected_indicator}** - {len(df_data)} observations")
        st.dataframe(df_data, width='stretch')
        
        # CSV download button
        csv = df_data.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"{selected_indicator}_{start_str}_to_{end_str}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data available for this indicator")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
Data sourced from Federal Reserve Economic Data (FRED) • 
<a href="https://fred.stlouisfed.org/">fred.stlouisfed.org</a>
</div>
""", unsafe_allow_html=True)
