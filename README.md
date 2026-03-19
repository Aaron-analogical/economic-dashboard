# Macroeconomic Dashboard with Streamlit & FRED Data

A professional macroeconomic dashboard built with Streamlit that fetches real-time economic data from the Federal Reserve Economic Data (FRED) API.

## Learning Objectives

This project teaches you:

### Core Streamlit Concepts

- **Page Configuration**: `st.set_page_config()` for setting page title, icon, and layout
- **Layout Components**: Columns and tabs for organizing content
- **Data Display**: Metrics, dataframes, and charts
- **User Input**: Date pickers, multiselect, selectbox
- **Caching**: `@st.cache_data` decorator for performance
- **State Management**: Working with sidebar for persistent settings

### Advanced Streamlit Features

- **Tabs**: Organizing related content with `st.tabs()`
- **Columns**: Creating responsive grid layouts
- **Charts**: Integrating Plotly for interactive visualizations
- **File Download**: CSV export functionality with `st.download_button()`
- **Error Handling**: Graceful error messages and data validation

### Data Engineering

- **API Integration**: Making HTTP requests to REST APIs
- **Data Processing**: Pandas for data transformation and normalization
- **Caching Strategy**: Using TTL (time-to-live) for efficient API usage
- **Date Range Handling**: User-friendly date selection and validation

## Quick Start

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**

   ```bash
   cd <directory-path>
   ```

2. **Create a Python virtual environment** (recommended)

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Get a FRED API Key**

   - Visit [fred.stlouisfed.org](https://fred.stlouisfed.org/)
   - Register for a free account
   - Go to Account → API Keys
   - Generate a new key

5. **Configure your API key**

   - Copy `.env.example` to `.env`:

   ```bash
   copy .env.example .env
   ```

   - Open `.env` and replace `your_api_key_here` with your actual FRED API key
   - **Important**: Never commit `.env` to version control!

6. **Run the app**

   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

## Features

### Tab 1: Key Indicators

- **Metric Cards**: Display latest values for unemployment rate, inflation, federal funds rate, and treasury yield
- **Time Series Charts**: Four detailed trend charts showing historical data
- **Interactive Exploration**: Hover to see exact values and dates

### Tab 2: Comparisons

- **Multi-Select**: Compare multiple indicators simultaneously
- **Normalized Display**: All indicators indexed to 100 for meaningful comparison
- **Dynamic Charts**: Charts update as you select/deselect indicators

### Tab 3: Data Export

- **Raw Data Table**: View exact values for any indicator
- **CSV Download**: Export data for use in Excel, R, Python, etc.

## Key Code Patterns

### 1. Caching Data

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_fred_data(series_id, start_date, end_date):
    # Fetch from API
    return df
```

Why? Avoids redundant API calls, improves performance, respects API rate limits.

### 2. Creating Columns (Responsive Grids)

```python
col1, col2, col3, col4 = st.columns(4)
col1.metric("Label", "Value")
col2.metric("Label", "Value")
```

Why? Creates professional layouts that adapt to screen size.

### 3. Using Tabs

```python
tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
with tab1:
    st.write("Content for tab 1")
with tab2:
    st.write("Content for tab 2")
```

Why? Organizes content logically without scrolling.

### 4. Plotly Interactivity

```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["date"], y=df["value"]))
st.plotly_chart(fig, width='stretch')
```

Why? Provides zoom, pan, hover information, and responsive sizing.

### 5. Error Handling

```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    st.error(f"Error: {e}")
```

Why? Prevents crashes and provides user feedback.

## Economic Indicators Included

| Indicator | FRED Series ID | Frequency | Use Case |
|-----------|----------------|-----------|----------|
| GDP | A191RL1Q225SBEA | Quarterly | Overall economic growth |
| Unemployment Rate | UNRATE | Monthly | Labor market health |
| CPI | CPIAUCSL | Monthly | Inflation measure |
| Federal Funds Rate | FEDFUNDS | Monthly | Monetary policy |
| 10-Year Treasury Yield | DGS10 | Daily | Long-term interest rates |
| S&P 500 | SP500 | Daily | Stock market performance |
| USD Index | DTWEXBGS | Daily | Currency strength |
| Initial Jobless Claims | ICSA | Weekly | Labor market timing |

## Customization Ideas

### Add New Indicators

Edit the `ECONOMIC_INDICATORS` dictionary:

```python
ECONOMIC_INDICATORS = {
    "Your Indicator": "FRED_SERIES_ID",  # Add new line
    # ... existing indicators
}
```

### Change Date Ranges

Modify the default date range in the sidebar:

```python
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=365*10))
```

### Add New Charts

```python
with st.columns(2)[0]:
    df = fetch_fred_data("SERIES_ID", start_str, end_str)
    fig = create_time_series_chart(df, "Title", "Y-Axis Label")
    st.plotly_chart(fig, width='stretch')
```

## Troubleshooting

**"FRED API Key not found" error**

- Ensure `.env` file exists in the project root
- Verify your API key is correctly pasted
- Restart the Streamlit app after saving `.env`

**"No data available" warning**

- FRED data has different frequencies and availability periods
- Try extending the date range
- Check [FRED website](https://fred.stlouisfed.org/) directly to verify data exists

**App runs slowly**

- Cache times out after 1 hour; wait for cached data to reload
- Reduce the date range to fetch less data
- FRED API has rate limits; space out requests

**Invalid date range error**

- Ensure start date is before end date
- Some FRED series don't have data for all historical periods

## Learn More

### Streamlit Documentation

- [Streamlit Docs](https://docs.streamlit.io/)
- [API Reference](https://docs.streamlit.io/library/api-reference)
- [Components Gallery](https://streamlit.io/components)

### FRED API

- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/)
- [Available Series](https://fred.stlouisfed.org/series/)
- [API Examples](https://fred.stlouisfed.org/docs/api/fred/series_observations.html)

### Data Visualization

- [Plotly Documentation](https://plotly.com/python/)
- [Streamlit + Plotly Guide](https://docs.streamlit.io/library/api-reference/charts/st.plotly_chart)

## Next Steps for Learning

1. **Add a new chart** displaying a different economic indicator
2. **Create a custom metric** showing year-over-year change
3. **Add filtering** by indicator type (e.g., "Employment", "Inflation")
4. **Deploy to Streamlit Cloud** for free hosting
5. **Add forecasting** using a time series model (Prophet, ARIMA)
6. **Integrate additional data sources** (Yahoo Finance, World Bank, etc.)

## License

This project is open source and available for educational purposes.

## Contributing

Have ideas for improvement? Feel free to:

- Add new indicators
- Improve chart styling
- Add more analysis features
- Fix bugs or improve documentation

---

**Built with Streamlit and FRED Data**