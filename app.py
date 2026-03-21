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

# Key economic indicators and their FRED series IDs, organized by category
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

# Indicators that should be shown as year-over-year % change
YOY_INDICATORS = {"Inflation (CPI)", "Core CPI", "Producer Price Index", "Industrial Production", "Retail Sales", "Non-Farm Payroll"}

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
end_date = st.sidebar.date_input("End Date", datetime.now(), min_value=datetime(1950, 1, 1), max_value=datetime.now())
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=365*30), min_value=datetime(1950, 1, 1), max_value=end_date)

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
tab1, tab2, tab3, tab4 = st.tabs(["📈 Key Indicators", "🔄 Comparisons", "📋 Data", "📖 Data Dictionary"])

# ============================================================================
# TAB 1: KEY INDICATORS
# ============================================================================
with tab1:
    st.subheader("Essential Economic Indicators")
    
    # Organize indicators by category
    indicator_categories = {
        "🏢 Macroeconomic": ["GDP"],
        "👥 Labor Market": ["Unemployment Rate", "Labor Force Participation", "Initial Jobless Claims", "Non-Farm Payroll"],
        "💰 Inflation & Prices": ["Inflation (CPI)", "Core CPI", "Producer Price Index"],
        "📊 Interest Rates": ["Federal Funds Rate", "10-Year Treasury Yield", "2-Year Treasury Yield", "30-Year Mortgage Rate"],
        "🏠 Housing": ["Housing Starts", "Building Permits", "Home Prices (Case-Shiller)"],
        "🏭 Production & Business": ["Industrial Production", "ISM Manufacturing PMI", "Retail Sales", "Consumer Disposable Income"],
        "📈 Markets": ["S&P 500", "VIX Volatility Index", "USD Index"]
    }
    
    # Create tabs for each category
    category_tabs = st.tabs(list(indicator_categories.keys()))
    
    for tab, (category, indicators) in zip(category_tabs, indicator_categories.items()):
        with tab:
            # Create columns for metrics grid
            cols = st.columns(min(4, len(indicators)))
            
            for i, indicator in enumerate(indicators):
                series_id = ECONOMIC_INDICATORS[indicator]
                df = fetch_fred_data(series_id, start_str, end_str)
                
                if indicator in YOY_INDICATORS:
                    df = compute_yoy_change(df)
                
                with cols[i % len(cols)]:
                    if not df.empty:
                        latest_value = df["value"].iloc[-1]
                        latest_date = df["date"].iloc[-1].strftime("%Y-%m-%d")
                        
                        label = f"{indicator} (YoY %)" if indicator in YOY_INDICATORS else indicator
                        formatted_value = f"{latest_value:.2f}%" if indicator in YOY_INDICATORS else f"{latest_value:.2f}"
                        
                        st.metric(
                            label=label,
                            value=formatted_value,
                            help=f"As of {latest_date}"
                        )
                    else:
                        st.warning(f"No data for {indicator}")
    
    st.markdown("---")
    
    # Individual charts for key indicators
    st.subheader("📈 Detailed Trends")
    
    # Labor Market Charts
    st.markdown("#### 👥 Labor Market")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        df_unemployment = fetch_fred_data("UNRATE", start_str, end_str)
        fig = create_time_series_chart(df_unemployment, "Unemployment Rate (%)", "Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col2:
        df_jobless = fetch_fred_data("ICSA", start_str, end_str)
        fig = create_time_series_chart(df_jobless, "Initial Jobless Claims", "Claims")
        st.plotly_chart(fig, use_container_width=True)
    
    # Prices & Inflation
    st.markdown("#### 💰 Inflation & Interest Rates")
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        df_cpi = fetch_fred_data("CPIAUCSL", start_str, end_str)
        df_cpi = compute_yoy_change(df_cpi)
        fig = create_time_series_chart(df_cpi, "CPI Inflation Rate (YoY %)", "% Change (YoY)")
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col4:
        df_fed_rate = fetch_fred_data("FEDFUNDS", start_str, end_str)
        fig = create_time_series_chart(df_fed_rate, "Federal Funds Rate (%)", "Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Housing & Production
    st.markdown("#### 🏠 Housing & 🏭 Production")
    chart_col5, chart_col6 = st.columns(2)
    
    with chart_col5:
        df_housing = fetch_fred_data("HOUST", start_str, end_str)
        fig = create_time_series_chart(df_housing, "Housing Starts (Thousands)", "Units Started")
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col6:
        df_industrial = fetch_fred_data("INDPRO", start_str, end_str)
        df_industrial = compute_yoy_change(df_industrial)
        fig = create_time_series_chart(df_industrial, "Industrial Production (YoY %)", "% Change (YoY)")
        st.plotly_chart(fig, use_container_width=True)

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
            st.plotly_chart(fig, use_container_width=True)
            
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
        st.dataframe(df_data, use_container_width=True)
        
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
# TAB 4: DATA DICTIONARY
# ============================================================================
with tab4:
    st.subheader("📖 Data Dictionary")
    st.markdown("Definitions and source details for every indicator in this dashboard.")
    
    data_dictionary = {
        "🏢 Macroeconomic": [
            {
                "name": "GDP",
                "full_name": "Real Gross Domestic Product (% Change)",
                "series": "A191RL1Q225SBEA",
                "frequency": "Quarterly",
                "unit": "% Change (annualized)",
                "definition": "The inflation-adjusted rate of change in the total value of goods and services produced in the U.S. A positive value indicates economic expansion; negative for two consecutive quarters signals a recession.",
                "source": "U.S. Bureau of Economic Analysis"
            },
        ],
        "👥 Labor Market": [
            {
                "name": "Unemployment Rate",
                "full_name": "Civilian Unemployment Rate",
                "series": "UNRATE",
                "frequency": "Monthly",
                "unit": "%",
                "definition": "The percentage of the labor force that is jobless and actively seeking employment. Does not count people who have stopped looking for work.",
                "source": "U.S. Bureau of Labor Statistics"
            },
            {
                "name": "Labor Force Participation",
                "full_name": "Civilian Labor Force Participation Rate",
                "series": "CIVPART",
                "frequency": "Monthly",
                "unit": "%",
                "definition": "The percentage of the civilian working-age population (16+) that is either employed or actively looking for work. A declining rate can mask true unemployment levels.",
                "source": "U.S. Bureau of Labor Statistics"
            },
            {
                "name": "Initial Jobless Claims",
                "full_name": "Initial Claims for Unemployment Insurance",
                "series": "ICSA",
                "frequency": "Weekly",
                "unit": "Number of persons",
                "definition": "The number of people who filed for unemployment benefits for the first time in a given week. A leading indicator — spikes suggest a deteriorating labor market.",
                "source": "U.S. Department of Labor"
            },
            {
                "name": "Non-Farm Payroll",
                "full_name": "All Employees: Total Nonfarm Payrolls",
                "series": "PAYEMS",
                "frequency": "Monthly",
                "unit": "Thousands of persons (YoY % change displayed)",
                "definition": "Total number of paid U.S. workers excluding farm workers, private household employees, and non-profit organization employees. One of the most closely watched labor indicators.",
                "source": "U.S. Bureau of Labor Statistics"
            },
            {
                "name": "Unemployment (25+ years)",
                "full_name": "Unemployment Rate: 25 Years and Over",
                "series": "LNU04000025",
                "frequency": "Monthly",
                "unit": "%",
                "definition": "Unemployment rate for workers aged 25 and over. This age group has largely completed education, making this a cleaner measure of structural labor market health.",
                "source": "U.S. Bureau of Labor Statistics"
            },
        ],
        "💰 Inflation & Prices": [
            {
                "name": "Inflation (CPI)",
                "full_name": "Consumer Price Index for All Urban Consumers",
                "series": "CPIAUCSL",
                "frequency": "Monthly",
                "unit": "Index (YoY % change displayed)",
                "definition": "Measures the average change over time in prices paid by urban consumers for a basket of goods and services including food, energy, and shelter. The most widely cited inflation measure.",
                "source": "U.S. Bureau of Labor Statistics"
            },
            {
                "name": "Core CPI",
                "full_name": "CPI: All Items Less Food and Energy",
                "series": "CPILFESL",
                "frequency": "Monthly",
                "unit": "Index (YoY % change displayed)",
                "definition": "CPI excluding volatile food and energy prices. Preferred by the Federal Reserve for assessing underlying inflation trends since food and energy prices fluctuate seasonally.",
                "source": "U.S. Bureau of Labor Statistics"
            },
            {
                "name": "Producer Price Index",
                "full_name": "Personal Consumption Expenditures Price Index",
                "series": "PCEPI",
                "frequency": "Monthly",
                "unit": "Index (YoY % change displayed)",
                "definition": "The PCE Price Index measures price changes for goods and services consumed by households. The Federal Reserve's preferred inflation gauge for setting monetary policy (2% target).",
                "source": "U.S. Bureau of Economic Analysis"
            },
        ],
        "📊 Interest Rates": [
            {
                "name": "Federal Funds Rate",
                "full_name": "Effective Federal Funds Rate",
                "series": "FEDFUNDS",
                "frequency": "Monthly",
                "unit": "%",
                "definition": "The interest rate at which banks lend overnight reserves to each other. Set by the Federal Reserve's FOMC as the primary tool of U.S. monetary policy. Influences all other interest rates.",
                "source": "Federal Reserve Board"
            },
            {
                "name": "10-Year Treasury Yield",
                "full_name": "Market Yield on U.S. Treasury Securities at 10-Year Maturity",
                "series": "DGS10",
                "frequency": "Daily",
                "unit": "%",
                "definition": "The return on investment for U.S. government 10-year bonds. Acts as the benchmark for mortgage rates and corporate borrowing. Rising yields generally signal inflation expectations or tighter financial conditions.",
                "source": "Federal Reserve Board"
            },
            {
                "name": "2-Year Treasury Yield",
                "full_name": "Market Yield on U.S. Treasury Securities at 2-Year Maturity",
                "series": "DGS2",
                "frequency": "Daily",
                "unit": "%",
                "definition": "The return on 2-year U.S. government bonds. Highly sensitive to Federal Reserve policy expectations. When the 2-year yield exceeds the 10-year yield, the yield curve is 'inverted', historically a recession signal.",
                "source": "Federal Reserve Board"
            },
            {
                "name": "30-Year Mortgage Rate",
                "full_name": "30-Year Fixed Rate Mortgage Average",
                "series": "MORTGAGE30US",
                "frequency": "Weekly",
                "unit": "%",
                "definition": "The average interest rate on a conventional 30-year fixed-rate mortgage in the U.S. Directly affects housing affordability and the health of the real estate market.",
                "source": "Freddie Mac"
            },
        ],
        "🏠 Housing": [
            {
                "name": "Housing Starts",
                "full_name": "New Residential Construction: Housing Starts",
                "series": "HOUST",
                "frequency": "Monthly",
                "unit": "Thousands of units",
                "definition": "The number of new residential construction projects begun in a given month. A leading economic indicator reflecting consumer confidence, credit conditions, and demand for housing.",
                "source": "U.S. Census Bureau"
            },
            {
                "name": "Building Permits",
                "full_name": "New Residential Construction: Building Permits",
                "series": "PERMIT",
                "frequency": "Monthly",
                "unit": "Thousands of units",
                "definition": "The number of permits issued for new residential construction. Leads housing starts by 1–2 months, making it a forward-looking indicator for construction and housing supply.",
                "source": "U.S. Census Bureau"
            },
            {
                "name": "Home Prices (Case-Shiller)",
                "full_name": "S&P/Case-Shiller U.S. National Home Price Index",
                "series": "CSUSHPISA",
                "frequency": "Monthly",
                "unit": "Index",
                "definition": "Measures the change in value of residential real estate across the U.S. Based on repeat-sales transactions, it tracks the same homes over time to give a consistent picture of price appreciation.",
                "source": "S&P Dow Jones Indices / CoreLogic"
            },
        ],
        "🏭 Production & Business": [
            {
                "name": "Industrial Production",
                "full_name": "Industrial Production Index",
                "series": "INDPRO",
                "frequency": "Monthly",
                "unit": "Index (YoY % change displayed)",
                "definition": "Measures the real output of manufacturing, mining, and electric and gas utilities. A broad gauge of the production sector's health; declines often precede recessions.",
                "source": "Federal Reserve Board"
            },
            {
                "name": "ISM Manufacturing PMI",
                "full_name": "ISM Manufacturing: PMI Composite Index",
                "series": "MMNRNJ",
                "frequency": "Monthly",
                "unit": "Index (50 = neutral)",
                "definition": "A survey-based index of manufacturing activity. A reading above 50 indicates expansion; below 50 indicates contraction. One of the most timely indicators of economic momentum.",
                "source": "Institute for Supply Management"
            },
            {
                "name": "Retail Sales",
                "full_name": "Advance Retail Sales: Retail and Food Services",
                "series": "RSXFS",
                "frequency": "Monthly",
                "unit": "Millions of USD (YoY % change displayed)",
                "definition": "Total receipts at stores that sell merchandise and related services. Since consumer spending drives ~70% of U.S. GDP, retail sales is a key gauge of economic momentum.",
                "source": "U.S. Census Bureau"
            },
            {
                "name": "Consumer Disposable Income",
                "full_name": "Disposable Personal Income",
                "series": "DSPI",
                "frequency": "Monthly",
                "unit": "Billions of USD (annualized)",
                "definition": "The amount of money households have available to spend or save after paying taxes. A primary driver of consumer spending and a measure of household financial health.",
                "source": "U.S. Bureau of Economic Analysis"
            },
        ],
        "📈 Markets": [
            {
                "name": "S&P 500",
                "full_name": "S&P 500 Stock Market Index",
                "series": "SP500",
                "frequency": "Daily",
                "unit": "Index",
                "definition": "A market-capitalization-weighted index of 500 leading U.S. publicly traded companies. Widely regarded as the best single gauge of large-cap U.S. equity market performance.",
                "source": "S&P Dow Jones Indices via FRED"
            },
            {
                "name": "VIX Volatility Index",
                "full_name": "CBOE Volatility Index",
                "series": "VIXCLS",
                "frequency": "Daily",
                "unit": "Index",
                "definition": "Measures expected 30-day volatility of the S&P 500 derived from options prices. Known as the 'fear gauge' — readings above 20 indicate elevated uncertainty; above 30 signal significant market stress.",
                "source": "Chicago Board Options Exchange (CBOE)"
            },
            {
                "name": "USD Index",
                "full_name": "Nominal Broad U.S. Dollar Index",
                "series": "DTWEXBGS",
                "frequency": "Daily",
                "unit": "Index",
                "definition": "Measures the value of the U.S. dollar relative to a broad basket of foreign currencies. A stronger dollar makes U.S. exports more expensive and imports cheaper, affecting trade balances and corporate earnings.",
                "source": "Federal Reserve Board"
            },
        ],
    }
    
    for category, indicators in data_dictionary.items():
        st.markdown(f"### {category}")
        for ind in indicators:
            with st.expander(f"**{ind['name']}** — {ind['full_name']}"):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**Definition:** {ind['definition']}")
                    st.markdown(f"**Source:** {ind['source']}")
                with col_b:
                    st.markdown(f"**FRED Series:** `{ind['series']}`")
                    st.markdown(f"**Frequency:** {ind['frequency']}")
                    st.markdown(f"**Unit:** {ind['unit']}")
        st.markdown("---")


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
