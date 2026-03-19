# 📚 Streamlit Learning Guide

This guide walks through the app code and explains key Streamlit concepts as you learn to build interactive dashboards.

## Table of Contents
1. [Setup & Imports](#setup--imports)
2. [Page Configuration](#page-configuration)
3. [Caching & Performance](#caching--performance)
4. [Layout & Organization](#layout--organization)
5. [User Input](#user-input)
6. [Data Visualization](#data-visualization)
7. [Common Patterns](#common-patterns)

---

## Setup & Imports

### Required Libraries

```python
import streamlit as st          # Main framework
import pandas as pd             # Data manipulation
import plotly.graph_objects as go  # Interactive charts
import requests                 # HTTP requests for APIs
from datetime import datetime, timedelta  # Date handling
import os                       # Environment variables
from dotenv import load_dotenv  # Load .env files
```

**Why each library?**
- `streamlit`: Core framework for building the app
- `pandas`: Efficient data transformation and analysis
- `plotly`: Interactive, professional charts
- `requests`: Simple HTTP client for API calls
- `datetime`: Date arithmetic and formatting
- `dotenv`: Secure API key management

---

## Page Configuration

### The First Streamlit Command

```python
st.set_page_config(
    page_title="Macro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

**Important Rules:**
- `st.set_page_config()` MUST be the first Streamlit command
- Must appear before any other `st.` calls
- Sets browser tab title, icon, and initial layout

**Parameters:**
- `page_title`: Browser tab title
- `page_icon`: Emoji or URL for tab icon
- `layout`: "centered" (default) or "wide"
- `initial_sidebar_state`: "expanded" or "collapsed"

---

## Caching & Performance

### Problem: Streamlit Re-runs Everything

When a user interacts with your app (clicks a button, types in a box), Streamlit **re-executes the entire script from top to bottom**. This means:
- API calls run again
- Dataframes are recreated
- Charts are redrawn
- **Result**: Slow, janky experience

### Solution: Caching with Decorators

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_fred_data(series_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    # Fetch from API
    response = requests.get(FRED_BASE_URL, params=...)
    # Process data
    return df
```

**How it works:**
1. Function is called with arguments `(series_id, start_date, end_date)`
2. Streamlit creates a cache key from the function name + arguments
3. If called again with same arguments, return cached result (skip function)
4. After `ttl` seconds, cache expires and function runs again

**Cache Types:**

| Decorator | Use Case |
|-----------|----------|
| `@st.cache_data` | Data processing (API calls, database queries, file reads) |
| `@st.cache_resource` | Expensive objects (ML models, database connections) |
| `@st.memo` (deprecated) | Same as cache_data (old syntax) |

### Cache Invalidation

```python
@st.cache_data(ttl=3600)
def get_data():
    return fetch_data()

# User clicks this button
if st.button("Refresh Data"):
    # Clear specific function cache
    get_data.clear()
    st.rerun()  # Re-run app to fetch fresh data
```

---

## Layout & Organization

### Sidebar

Sidebars hold configuration without taking main screen space:

```python
st.sidebar.title("⚙️ Settings")

# Inputs in sidebar
option = st.sidebar.selectbox("Choose an option", ["A", "B", "C"])
value = st.sidebar.slider("Value", 0, 100, 50)

# Markdown content
st.sidebar.markdown("---")
st.sidebar.info("This is helpful info!")
```

### Columns (Grid Layout)

Create responsive, side-by-side layouts:

```python
# 4 equal columns
col1, col2, col3, col4 = st.columns(4)

col1.metric("Label 1", "Value 1")
col2.metric("Label 2", "Value 2")
col3.metric("Label 3", "Value 3")
col4.metric("Label 4", "Value 4")
```

**Unequal widths:**
```python
# 60% width, 40% width
col_wide, col_narrow = st.columns([3, 2])

col_wide.write("Takes up 60% of width")
col_narrow.write("Takes up 40%")
```

### Tabs (Tabbed Sections)

Organize content without scrolling:

```python
tab1, tab2, tab3 = st.tabs(["📈 Tab 1", "📊 Tab 2", "📋 Tab 3"])

with tab1:
    st.write("Content in first tab")
    st.chart(...)

with tab2:
    st.write("Content in second tab")
    
with tab3:
    st.write("Content in third tab")
```

### Containers

Group and organize content:

```python
with st.container():
    st.write("This group will have a visible border")
    st.write("And organized styling")

expander = st.expander("Click to expand")
with expander:
    st.write("Hidden content shown on click")
```

---

## User Input

### Input Widgets

Streamlit re-runs when users interact with these:

```python
# Text input
name = st.text_input("Enter your name", "John")

# Number input
age = st.number_input("Age", min_value=0, max_value=120, value=25)

# Dropdown/Select
option = st.selectbox("Choose one:", ["Option A", "Option B"])

# Multi-select
options = st.multiselect("Choose multiple:", ["A", "B", "C"])

# Date picker
date = st.date_input("Pick a date")

# Slider
value = st.slider("Value", 0, 100, 50)

# Radio buttons
choice = st.radio("Choose one:", ["Yes", "No", "Maybe"])

# Checkbox
agreed = st.checkbox("I agree to terms")

# Button (triggers re-run)
if st.button("Click me"):
    st.write("Button was clicked!")
```

### Session State (Remembering Values)

By default, variables are lost on re-run. Use Session State to persist:

```python
# Initialize
if "counter" not in st.session_state:
    st.session_state.counter = 0

# Modify
if st.button("Increment"):
    st.session_state.counter += 1

# Display
st.write(f"Count: {st.session_state.counter}")
```

---

## Data Visualization

### Streamlit Built-in Charts

Simple charts (don't require Plotly):

```python
# Line chart
st.line_chart(df)

# Bar chart
st.bar_chart(df)

# Area chart
st.area_chart(df)

# Dataframe table
st.dataframe(df, use_container_width=True)
```

### Plotly for Advanced Charts

Interactive, professional charts:

```python
import plotly.graph_objects as go

fig = go.Figure()

# Add a line trace
fig.add_trace(go.Scatter(
    x=df["date"],
    y=df["value"],
    mode="lines",
    name="Series 1",
    line=dict(color="blue", width=2)
))

# Customize layout
fig.update_layout(
    title="My Chart",
    xaxis_title="X Axis",
    yaxis_title="Y Axis",
    hovermode="x unified",
    template="plotly_white",
    height=400
)

# Display
st.plotly_chart(fig, use_container_width=True)
```

**Plotly Advantages:**
- Hover to see values
- Zoom and pan
- Interactive legend
- Professional styling
- Responsive sizing

---

## Common Patterns

### Error Handling

```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    st.error(f"❌ Error: {e}")
    return pd.DataFrame()
except ValueError as e:
    st.warning(f"⚠️ Invalid data: {e}")
    return pd.DataFrame()
```

### Loading States

```python
with st.spinner('Loading data...'):
    data = fetch_data()
    time.sleep(2)  # Simulate work

st.success('Done!')
```

### Conditional Display

```python
if df.empty:
    st.warning("No data available")
else:
    st.dataframe(df)
    
if user_approved:
    st.success("✅ Approved!")
else:
    st.error("❌ Not approved")
```

### CSV Download

```python
csv = df.to_csv(index=False)

st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name="data.csv",
    mime="text/csv"
)
```

### API Integration Pattern

```python
@st.cache_data(ttl=3600)
def fetch_from_api(params):
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        df = pd.DataFrame(data["items"])
        df["date"] = pd.to_datetime(df["date"])
        
        return df
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()
```

---

## Development Tips

### Hot Reload

Streamlit automatically reloads when you save changes (during development).

### Debug Prints

```python
import streamlit as st

st.write("Debug info:", variable)  # Display in app
print("Console log", variable)     # Show in terminal
```

### Testing Locally

```bash
streamlit run app.py
```

App opens at `http://localhost:8501`

### Understanding Re-runs

Streamlit runs top-to-bottom on every user interaction. Key concepts:

1. **Caching**: Skip expensive operations
2. **Callbacks**: Modify state before re-run
3. **Session State**: Persist values across runs
4. **Sidebar**: Isolate inputs from main content

---

## Practice Exercises

### Exercise 1: Add a Refresh Button
```python
if st.sidebar.button("🔄 Refresh Data"):
    fetch_data.clear()
    st.rerun()
```

### Exercise 2: Add Filtering
```python
selected_year = st.sidebar.slider("Year", 2020, 2024)
filtered_df = df[df["year"] == selected_year]
st.dataframe(filtered_df)
```

### Exercise 3: Add Statistics
```python
col1, col2, col3 = st.columns(3)
col1.metric("Average", df["value"].mean())
col2.metric("Min", df["value"].min())
col3.metric("Max", df["value"].max())
```

### Exercise 4: Add Custom Styling
```python
st.markdown("""
<style>
    .big-font {
        font-size:32px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">Important Text</p>', unsafe_allow_html=True)
```

---

## Deployment

### Deploy to Streamlit Cloud (Free)

1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub repository
4. App deploys instantly and gets a URL

```
https://your-app-name.streamlit.app
```

### Secrets Management in Cloud

Store API keys securely:

1. In Streamlit Cloud dashboard, click "Secrets"
2. Add your secret:
   ```
   FRED_API_KEY=your_key_here
   ```
3. Access in code:
   ```python
   api_key = st.secrets["FRED_API_KEY"]
   ```

---

## Common Gotchas

| Problem | Solution |
|---------|----------|
| Data fetched every rerun | Use `@st.cache_data` |
| Values lost on rerun | Use `st.session_state` |
| Set page config error | Must be first Streamlit command |
| Slow app | Optimize caching, reduce data |
| API errors | Add error handling and timeouts |
| Layout shifts | Use `use_container_width=True` |

---

## Next Level

Once comfortable with basics, explore:
- **State Management**: Complex workflows with callbacks
- **Streaming**: Real-time data with `st.write_stream()`
- **Custom Components**: Build JavaScript-based widgets
- **Performance**: Profile and optimize with `--logger.level=debug`
- **Testing**: Write tests for Streamlit apps

**More resources:**
- [Streamlit Discord Community](https://discord.com/invite/NUck8HT7uK)
- [Streamlit Blog](https://blog.streamlit.io/)
- [Gallery of Examples](https://streamlit.io/gallery)
