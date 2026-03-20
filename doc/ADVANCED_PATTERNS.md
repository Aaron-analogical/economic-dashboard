# 🚀 Advanced Streamlit Patterns

Beyond the basics—techniques for building production-quality dashboards.

## Table of Contents
1. [Session State Patterns](#session-state-patterns)
2. [Callbacks & Forms](#callbacks--forms)
3. [Custom Functions & Reusability](#custom-functions--reusability)
4. [Performance Optimization](#performance-optimization)
5. [Error Handling & Validation](#error-handling--validation)
6. [Styling & Theming](#styling--theming)
7. [Production Deployment](#production-deployment)

---

## Session State Patterns

### Problem: Lost State on Re-runs

Streamlit re-runs the entire script when users interact. Without state management:

```python
counter = 0

if st.button("Add"):
    counter += 1  # ❌ Lost on re-run!

st.write(counter)  # Always shows 0
```

### Solution: Session State

```python
# Initialize once
if "counter" not in st.session_state:
    st.session_state.counter = 0

# Persist across re-runs
if st.button("Add"):
    st.session_state.counter += 1

st.write(st.session_state.counter)  # ✅ Persists correctly
```

### Complex State Example

```python
# Initialize nested state
if "dashboard" not in st.session_state:
    st.session_state.dashboard = {
        "selected_metrics": [],
        "date_range": (None, None),
        "filters": {},
        "refresh_count": 0
    }

# Access and modify
state = st.session_state.dashboard
state["filters"]["region"] = "US-EAST"
state["refresh_count"] += 1
```

---

## Callbacks & Forms

### The Issue: Re-run on Every Input

By default, Streamlit re-runs when ANY input widget changes:

```python
# Each change triggers re-run
value1 = st.slider("Slider 1", 0, 100, 50)  # ← Re-run
value2 = st.slider("Slider 2", 0, 100, 50)  # ← Re-run
button = st.button("Submit")                  # ← Re-run (only actually does something if clicked)

# Result: Expensive operations run on every slider change!
df = fetch_huge_dataset()
```

### Solution 1: Callbacks

Run code when input changes WITHOUT full re-run:

```python
def update_metric():
    """Called when slider changes, before re-run"""
    st.session_state.last_update = time.time()

value = st.slider(
    "Select value", 
    0, 100, 50,
    on_change=update_metric  # Called immediately
)

# Use cached value instead of re-fetching
@st.cache_data
def get_data():
    return fetch_data()

data = get_data()  # Uses cache if callback didn't cause refresh
```

### Solution 2: Form Blocks

Batch inputs and submit together:

```python
with st.form("my_form"):
    st.write("### Settings")
    
    # Multiple inputs collected
    name = st.text_input("Name")
    age = st.number_input("Age")
    metric = st.selectbox("Metric", ["A", "B", "C"])
    
    # Single submission button
    submitted = st.form_submit_button("Apply Settings")

# Only re-runs when button clicked, not on each input change!
if submitted:
    st.write(f"Name: {name}, Age: {age}, Metric: {metric}")
    df = fetch_data()  # Only run once on submit
```

### Best Practice: Form + Callback + State

```python
def on_date_change():
    """Update state when dates change in form"""
    st.session_state.date_updated = True

with st.form("date_filter"):
    start_date = st.date_input("Start", key="start")
    end_date = st.date_input("End", key="end")
    submitted = st.form_submit_button("Filter", on_click=on_date_change)

if submitted and st.session_state.get("date_updated"):
    @st.cache_data(ttl=3600)
    def get_filtered_data(start, end):
        return fetch_data_between(start, end)
    
    df = get_filtered_data(start_date, end_date)
    st.dataframe(df)
```

---

## Custom Functions & Reusability

### Create Reusable Components

```python
def metric_card(title: str, value: float, 
                 previous: float = None, format: str = ".2f") -> None:
    """Display a professional metric card"""
    
    formatter = f"{{:{format}}}"
    formatted_value = formatter.format(value)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.metric(title, formatted_value)
    
    if previous:
        change = value - previous
        with col2:
            st.metric("Change", formatter.format(change))

# Use it
metric_card("Revenue", 152000, 150000, ".0f")
metric_card("Growth %", 5.23, 4.89, ".2f")
```

### Dashboard Builder Pattern

```python
class Dashboard:
    def __init__(self, title: str):
        self.title = title
        self.sections = []
    
    def add_metric_row(self, metrics: dict) -> None:
        """Add a row of metrics"""
        self.sections.append({"type": "metrics", "data": metrics})
    
    def add_chart(self, df: pd.DataFrame, chart_type: str) -> None:
        """Add a chart"""
        self.sections.append({"type": "chart", "data": df, "chart": chart_type})
    
    def render(self) -> None:
        """Render entire dashboard"""
        st.title(self.title)
        
        for section in self.sections:
            if section["type"] == "metrics":
                cols = st.columns(len(section["data"]))
                for i, (metric_name, metric_value) in enumerate(section["data"].items()):
                    cols[i].metric(metric_name, metric_value)
            
            elif section["type"] == "chart":
                if section["chart"] == "line":
                    st.line_chart(section["data"])
                elif section["chart"] == "bar":
                    st.bar_chart(section["data"])

# Usage
dashboard = Dashboard("Sales Dashboard")
dashboard.add_metric_row({"Total": "152k", "Growth": "+5%"})
dashboard.add_chart(sales_df, "line")
dashboard.render()
```

---

## Performance Optimization

### 1. Caching Strategies

```python
# Standard cache (1 hour)
@st.cache_data(ttl=3600)
def get_data():
    return fetch_data()

# Resource you only want one instance of (ML models, DB connections)
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("model.h5")

# Manual cache clearing
if st.button("Clear Cache"):
    st.cache_data.clear()
    st.rerun()
```

### 2. Lazy Loading

```python
# Load only when user navigates to tab
tab1, tab2, tab3 = st.tabs(["Overview", "Details", "Export"])

with tab1:
    st.write("Quick overview (always loaded)")

with tab2:
    if st.button("Load detailed analysis"):
        # Expensive operation only if user clicks
        detailed_data = expensive_analysis()
        st.dataframe(detailed_data)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export CSV"):
            csv = generate_csv()  # Only generate on demand
            st.download_button("Download", csv, "data.csv")
```

### 3. Incremental Updates

```python
# Use container to update specific parts
placeholder = st.empty()

for i in range(10):
    with placeholder.container():
        st.write(f"Loading... {i+1}/10")
        st.progress((i+1) / 10)
    time.sleep(1)

# Replace entire container when done
with placeholder.container():
    st.success("✅ Loaded!")
    st.dataframe(results)
```

### 4. Query Optimization

```python
@st.cache_data(ttl=3600)
def get_large_dataset():
    # Fetch entire dataset once
    return pd.read_sql("SELECT * FROM huge_table", connection)

# Filter in Python, not via re-query
if st.button("Apply Filters"):
    full_data = get_large_dataset()  # Uses cache
    
    # Filter in memory (fast)
    region = st.selectbox("Region", ["US", "EU", "ASIA"])
    filtered = full_data[full_data["region"] == region]
    
    st.dataframe(filtered)
```

---

## Error Handling & Validation

### Input Validation

```python
def validate_dates(start_date, end_date) -> tuple[bool, str]:
    """Validate date inputs"""
    if start_date > end_date:
        return False, "Start date must be before end date"
    
    if (end_date - start_date).days > 365*5:
        return False, "Date range cannot exceed 5 years"
    
    return True, ""

# Usage
start = st.date_input("Start")
end = st.date_input("End")

if st.button("Analyze"):
    is_valid, error_msg = validate_dates(start, end)
    
    if not is_valid:
        st.error(error_msg)
    else:
        results = analyze(start, end)
        st.dataframe(results)
```

### API Error Handling

```python
@st.cache_data
def fetch_with_retry(url: str, max_retries: int = 3) -> dict:
    """Fetch with exponential backoff"""
    import time
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout:
            st.warning(f"Timeout (attempt {attempt+1}/{max_retries})")
        
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API")
            return {}
        
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt
                st.info(f"Rate limited. Retry in {wait_time}s...")
                time.sleep(wait_time)
            else:
                st.error(f"API Error: {e}")
                return {}
        
        except ValueError:
            st.error("Invalid JSON response")
            return {}
    
    st.error("Max retries exceeded")
    return {}
```

### Try-Except Wrapper

```python
def safe_operation(operation_func, *args, **kwargs):
    """Wrap any operation with error handling"""
    try:
        result = operation_func(*args, **kwargs)
        if result is None or (isinstance(result, pd.DataFrame) and result.empty):
            st.warning("No data returned")
            return None
        return result
    
    except KeyError as e:
        st.error(f"Missing key: {e}")
    except ValueError as e:
        st.error(f"Invalid value: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.write("Debug info:", type(e).__name__)
    
    return None

# Usage
df = safe_operation(fetch_data, "API_KEY", date="2024-01-01")
if df is not None:
    st.dataframe(df)
```

---

## Styling & Theming

### Custom Colors & Fonts

```python
st.markdown("""
<style>
    /* Override CSS variables for dark mode */
    :root {
        --primary-color: #3498db;
        --background-color: #1a1a1a;
        --secondary-background-color: #2d2d2d;
    }
    
    /* Custom classes */
    .big-text {
        font-size: 24px;
        font-weight: bold;
        color: #3498db;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 4px;
        padding: 12px;
        color: #155724;
    }
    
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 4px;
        padding: 12px;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-text">My Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="success-box">✅ All systems operational</div>', unsafe_allow_html=True)
```

### Conditional Styling

```python
def style_value(value: float, threshold: float) -> str:
    """Apply color based on value"""
    if value > threshold:
        return f"<span style='color: green; font-weight: bold;'>{value:.2f}</span>"
    elif value < threshold:
        return f"<span style='color: red; font-weight: bold;'>{value:.2f}</span>"
    else:
        return f"<span style='color: gray;'>{value:.2f}</span>"

unemployment_rate = 3.8
threshold = 4.0

st.markdown(
    f"Unemployment Rate: {style_value(unemployment_rate, threshold)}",
    unsafe_allow_html=True
)
```

### Theme Configuration (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#FF6F59"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = false
toolbarMode = "viewer"

[logger]
level = "info"
```

---

## Production Deployment

### Deployment Checklist

- [ ] Remove hardcoded credentials (use `.env` or cloud secrets)
- [ ] Add error handling for all APIs
- [ ] Implement caching to minimize API calls
- [ ] Add logging for debugging
- [ ] Test with realistic data volumes
- [ ] Set up monitoring/alerting
- [ ] Document API key setup
- [ ] Create deployment guide

### Secrets Management

**Local Development (.env):**
```
FRED_API_KEY=xxxxxxxxxxxx
DATABASE_URL=postgresql://user:pass@host:5432/db
```

**Streamlit Cloud (in Dashboard UI):**
```
FRED_API_KEY = xxxxxxxxxxxx
DATABASE_URL = postgresql://user:pass@host:5432/db
```

**Access in Code:**
```python
# Automatically works in cloud; reads .env locally
import os
api_key = os.getenv("FRED_API_KEY")

# Or use st.secrets in cloud only
try:
    api_key = st.secrets["FRED_API_KEY"]
except KeyError:
    api_key = os.getenv("FRED_API_KEY")
```

### Logging for Production

```python
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_data():
    try:
        logger.info("Fetching data from API")
        data = requests.get(API_URL).json()
        logger.info(f"Successfully fetched {len(data)} records")
        return data
    
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}", exc_info=True)
        raise
```

### Health Check Endpoint (for monitoring)

```python
# health_check.py
import requests
from datetime import datetime

def check_fred_api():
    """Health check for FRED API"""
    try:
        response = requests.get(
            "https://api.stlouisfed.org/fred/series/observations",
            params={"series_id": "UNRATE", "api_key": "YOUR_KEY"},
            timeout=5
        )
        response.raise_for_status()
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    result = check_fred_api()
    print(result)
```

---

## Common Anti-Patterns to Avoid

| ❌ Don't | ✅ Do | Why |
|----------|--------|------|
| Fetch data in main code | Use `@st.cache_data` | Improves performance |
| Global variables | Use `st.session_state` | Avoids state issues |
| Long synchronous operations | Add progress indicators | Better UX |
| Hardcoded credentials | Use `.env` or secrets | Security |
| Ignore errors | Add try-except | Reliability |
| No input validation | Validate before use | Prevents crashes |
| Serve large files directly | Stream or provide download link | Reduces server load |
| Query database multiple times | Cache results | Better performance |

---

## Testing Streamlit Apps

```python
# test_app.py
import pytest
from streamlit.testing.v1 import AppTest

def test_metric_displays_correctly():
    """Test that metrics display proper values"""
    at = AppTest.from_file("app.py")
    at.run()
    
    # Check if metric is displayed
    assert len(at.metric) == 1
    assert at.metric[0].value == "3.8"

def test_chart_renders():
    """Test that charts render without error"""
    at = AppTest.from_file("app.py")
    at.run()
    
    # Check if plotly chart is displayed
    assert len(at.plotly_chart) > 0

def test_download_button_works():
    """Test CSV download"""
    at = AppTest.from_file("app.py")
    at.run()
    
    # Check if download button exists
    assert len(at.download_button) > 0
```

---

## Resources & Next Steps

- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- [Advanced Features Guide](https://docs.streamlit.io/library/advanced-features)
- [Deployment Guide](https://docs.streamlit.io/deploy/streamlit-cloud)
- [Community Components](https://streamlit.io/components)
