"""Data Dictionary — Definitions, sources, and metadata for all indicators."""

import streamlit as st
from utils.helpers import FOOTER

st.set_page_config(page_title="Data Dictionary", page_icon="📖", layout="wide")

st.sidebar.title("📖 Data Dictionary")
st.sidebar.markdown("Browse definitions, FRED series IDs, units, and sources for all 23 indicators.")

st.title("📖 Data Dictionary")
st.markdown("Full reference for all indicators tracked in this dashboard.")
st.markdown("---")

DATA_DICTIONARY = {
    "🏛️ Macroeconomic": [
        {
            "name": "GDP",
            "full_name": "Real Gross Domestic Product",
            "definition": (
                "The inflation-adjusted value of all goods and services produced by the economy "
                "in a given period, expressed as a quarter-over-quarter percent change at a seasonally "
                "adjusted annual rate (SAAR). The broadest measure of economic output."
            ),
            "source": "Bureau of Economic Analysis (BEA) via FRED",
            "series": "A191RL1Q225SBEA",
            "frequency": "Quarterly",
            "unit": "% Change (SAAR)",
        },
    ],
    "👷 Labor Market": [
        {
            "name": "Unemployment Rate",
            "full_name": "Civilian Unemployment Rate",
            "definition": (
                "The percentage of the civilian labor force that is jobless and actively seeking "
                "employment. One of the most widely cited economic health indicators."
            ),
            "source": "Bureau of Labor Statistics (BLS) via FRED",
            "series": "UNRATE",
            "frequency": "Monthly",
            "unit": "Percent",
        },
        {
            "name": "Labor Force Participation",
            "full_name": "Civilian Labor Force Participation Rate",
            "definition": (
                "The percentage of the civilian noninstitutional population aged 16 and over "
                "that is either working or actively looking for work. Captures discouraged workers "
                "missed by the unemployment rate."
            ),
            "source": "Bureau of Labor Statistics (BLS) via FRED",
            "series": "CIVPART",
            "frequency": "Monthly",
            "unit": "Percent",
        },
        {
            "name": "Initial Jobless Claims",
            "full_name": "Initial Claims for Unemployment Insurance",
            "definition": (
                "The number of new claims filed for unemployment insurance in a given week. "
                "A leading indicator of labor market conditions — spikes signal rising layoffs."
            ),
            "source": "Department of Labor via FRED",
            "series": "ICSA",
            "frequency": "Weekly",
            "unit": "Thousands of Persons",
        },
        {
            "name": "Non-Farm Payroll",
            "full_name": "All Employees, Total Nonfarm",
            "definition": (
                "The total number of paid U.S. workers in all non-farm businesses. "
                "This monthly report is a key gauge of job creation and overall economic momentum."
            ),
            "source": "Bureau of Labor Statistics (BLS) via FRED",
            "series": "PAYEMS",
            "frequency": "Monthly",
            "unit": "Thousands of Persons",
        },
        {
            "name": "Unemployment (25+ years)",
            "full_name": "Unemployment Rate — 25 Years and Over",
            "definition": (
                "The unemployment rate for civilians aged 25 and older. Focuses on the prime-age "
                "and older workforce, filtering out younger workers who may be transitioning from school."
            ),
            "source": "Bureau of Labor Statistics (BLS) via FRED",
            "series": "LNU04000025",
            "frequency": "Monthly",
            "unit": "Percent",
        },
    ],
    "📈 Inflation & Prices": [
        {
            "name": "Inflation (CPI)",
            "full_name": "Consumer Price Index for All Urban Consumers (CPI-U)",
            "definition": (
                "Measures the average change in prices paid by urban consumers for a basket of "
                "goods and services. The primary headline inflation gauge in the United States."
            ),
            "source": "Bureau of Labor Statistics (BLS) via FRED",
            "series": "CPIAUCSL",
            "frequency": "Monthly",
            "unit": "YoY %",
        },
        {
            "name": "Core CPI",
            "full_name": "CPI for All Urban Consumers: All Items Less Food and Energy",
            "definition": (
                "CPI excluding the volatile food and energy components. Considered a more stable "
                "measure of underlying inflation trends and closely watched by the Federal Reserve."
            ),
            "source": "Bureau of Labor Statistics (BLS) via FRED",
            "series": "CPILFESL",
            "frequency": "Monthly",
            "unit": "YoY %",
        },
        {
            "name": "Producer Price Index",
            "full_name": "Personal Consumption Expenditures Price Index (PCE)",
            "definition": (
                "Measures the prices paid for goods and services by consumers, as tracked through "
                "the personal consumption expenditure deflator. The Federal Reserve's preferred "
                "measure of inflation for its 2% target."
            ),
            "source": "Bureau of Economic Analysis (BEA) via FRED",
            "series": "PCEPI",
            "frequency": "Monthly",
            "unit": "YoY %",
        },
    ],
    "🏦 Interest Rates": [
        {
            "name": "Federal Funds Rate",
            "full_name": "Federal Funds Effective Rate",
            "definition": (
                "The interest rate at which depository institutions lend reserve balances to each "
                "other overnight. Set by the Federal Open Market Committee (FOMC); the primary tool "
                "of U.S. monetary policy."
            ),
            "source": "Federal Reserve via FRED",
            "series": "FEDFUNDS",
            "frequency": "Monthly",
            "unit": "Percent",
        },
        {
            "name": "10-Year Treasury Yield",
            "full_name": "Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity",
            "definition": (
                "The yield on the benchmark 10-year U.S. Treasury note. Widely used as the "
                "risk-free rate in financial models and serves as a reference rate for mortgages "
                "and long-term lending."
            ),
            "source": "U.S. Treasury / Federal Reserve via FRED",
            "series": "DGS10",
            "frequency": "Daily",
            "unit": "Percent",
        },
        {
            "name": "2-Year Treasury Yield",
            "full_name": "Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity",
            "definition": (
                "The yield on the 2-year U.S. Treasury note. Sensitive to Federal Reserve policy "
                "expectations. The spread between the 2-year and 10-year yields (yield curve) is "
                "a closely watched recession indicator."
            ),
            "source": "U.S. Treasury / Federal Reserve via FRED",
            "series": "DGS2",
            "frequency": "Daily",
            "unit": "Percent",
        },
        {
            "name": "30-Year Mortgage Rate",
            "full_name": "30-Year Fixed Rate Mortgage Average in the United States",
            "definition": (
                "The national average interest rate for 30-year fixed-rate mortgages. "
                "Directly affects housing affordability and is influenced by the 10-year Treasury yield."
            ),
            "source": "Freddie Mac via FRED",
            "series": "MORTGAGE30US",
            "frequency": "Weekly",
            "unit": "Percent",
        },
    ],
    "🏠 Housing": [
        {
            "name": "Housing Starts",
            "full_name": "Housing Starts: Total New Privately Owned Housing Units Started",
            "definition": (
                "The number of new residential construction projects begun in a given month. "
                "A leading indicator of economic activity, employment in construction, and future "
                "housing supply."
            ),
            "source": "U.S. Census Bureau via FRED",
            "series": "HOUST",
            "frequency": "Monthly",
            "unit": "Thousands of Units (SAAR)",
        },
        {
            "name": "Building Permits",
            "full_name": "New Privately-Owned Housing Units Authorized by Building Permits",
            "definition": (
                "The number of new housing units authorized by building permits. Leads housing "
                "starts by several months and is a useful gauge of future construction activity."
            ),
            "source": "U.S. Census Bureau via FRED",
            "series": "PERMIT",
            "frequency": "Monthly",
            "unit": "Thousands of Units (SAAR)",
        },
        {
            "name": "Home Prices (Case-Shiller)",
            "full_name": "S&P/Case-Shiller U.S. National Home Price Index",
            "definition": (
                "A composite index measuring the change in value of single-family homes across "
                "the United States. The most widely cited measure of U.S. residential real estate values."
            ),
            "source": "S&P Dow Jones Indices via FRED",
            "series": "CSUSHPISA",
            "frequency": "Monthly",
            "unit": "Index (Jan 2000 = 100)",
        },
    ],
    "🏭 Production & Business": [
        {
            "name": "Industrial Production",
            "full_name": "Industrial Production: Total Index",
            "definition": (
                "Measures the real output of manufacturing, mining, and electric and gas utilities. "
                "An important coincident indicator of economic activity."
            ),
            "source": "Federal Reserve via FRED",
            "series": "INDPRO",
            "frequency": "Monthly",
            "unit": "YoY %",
        },
        {
            "name": "ISM Manufacturing PMI",
            "full_name": "ISM Manufacturing: PMI Composite Index",
            "definition": (
                "A survey-based index of manufacturing sector activity. Readings above 50 indicate "
                "expansion; below 50 indicate contraction. One of the most timely economic indicators available."
            ),
            "source": "Institute for Supply Management via FRED",
            "series": "MMNRNJ",
            "frequency": "Monthly",
            "unit": "Index (50 = neutral)",
        },
        {
            "name": "Retail Sales",
            "full_name": "Advance Retail Sales: Retail Trade and Food Services",
            "definition": (
                "Total receipts at stores selling merchandise and providing food and drinking services. "
                "Consumer spending drives roughly 70% of U.S. GDP, making this a critical demand indicator."
            ),
            "source": "U.S. Census Bureau via FRED",
            "series": "RSXFS",
            "frequency": "Monthly",
            "unit": "YoY %",
        },
        {
            "name": "Consumer Disposable Income",
            "full_name": "Real Disposable Personal Income",
            "definition": (
                "Personal income after taxes, adjusted for inflation. Represents the purchasing "
                "power available to households and drives consumer spending trends."
            ),
            "source": "Bureau of Economic Analysis (BEA) via FRED",
            "series": "DSPI",
            "frequency": "Monthly",
            "unit": "Billions of Chained 2017 Dollars (SAAR)",
        },
    ],
    "📊 Markets": [
        {
            "name": "S&P 500",
            "full_name": "S&P 500 Stock Price Index",
            "definition": (
                "A market-capitalization-weighted index of 500 large U.S. companies. "
                "The leading benchmark for U.S. equity performance and a component of the "
                "Conference Board's Leading Economic Index."
            ),
            "source": "S&P Dow Jones Indices via FRED",
            "series": "SP500",
            "frequency": "Daily",
            "unit": "Index",
        },
        {
            "name": "VIX Volatility Index",
            "full_name": "CBOE Volatility Index (VIX)",
            "definition": (
                "Measures the market's expectation of 30-day volatility of the S&P 500, derived "
                "from option prices. Often called the 'fear gauge' — spikes above 30 typically "
                "signal market stress or uncertainty."
            ),
            "source": "Chicago Board Options Exchange via FRED",
            "series": "VIXCLS",
            "frequency": "Daily",
            "unit": "Index",
        },
        {
            "name": "USD Index",
            "full_name": "Trade Weighted U.S. Dollar Index: Broad, Goods and Services",
            "definition": (
                "Measures the value of the U.S. dollar relative to a broad basket of currencies "
                "weighted by trade flows. A rising index means a stronger dollar, which affects "
                "exports, imports, and multinational corporate earnings."
            ),
            "source": "Federal Reserve via FRED",
            "series": "DTWEXBGS",
            "frequency": "Daily",
            "unit": "Index (Jan 2006 = 100)",
        },
    ],
}

for category, indicators in DATA_DICTIONARY.items():
    st.subheader(category)
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

st.markdown(FOOTER, unsafe_allow_html=True)
