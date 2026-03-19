# 📋 Streamlit Cheat Sheet

Quick reference for common Streamlit patterns and commands.

## Installation & Setup

```bash
# Install Streamlit
pip install streamlit

# Run app
streamlit run app.py

# Clear cache
streamlit cache clear

# Run with specific port
streamlit run app.py --server.port 8501
```

## Page Config

```python
st.set_page_config(
    page_title="App Title",
    page_icon="📊",
    layout="wide",  # or "centered"
    initial_sidebar_state="expanded"  # or "collapsed"
)
```

## Layout

```python
# Sidebar
st.sidebar.title("Sidebar")
st.sidebar.write("Content")

# Columns
col1, col2, col3 = st.columns(3)
col1.write("Column 1")

# Unequal columns
col1, col2 = st.columns([3, 1])  # 75%, 25%

# Tabs
tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])
with tab1:
    st.write("Content in tab 1")

# Container
with st.container():
    st.write("In container")

# Expander
with st.expander("Click to expand"):
    st.write("Hidden content")
```

## Text & Display

```python
st.title("Title")
st.header("Header")
st.subheader("Subheader")
st.text("Plain text")
st.markdown("**Bold** and _italic_")
st.code("print('hello')", language="python")

# With HTML
st.markdown("<h1>HTML content</h1>", unsafe_allow_html=True)

# Divider
st.divider()
st.markdown("---")
```

## Messages & Alerts

```python
st.success("✅ Success!")
st.info("ℹ️ Info message")
st.warning("⚠️ Warning!")
st.error("❌ Error!")

# With icon
st.write("✨ Custom emoji message")
```

## Data Display

```python
# Dataframe (interactive)
st.dataframe(df, use_container_width=True)

# Table (static)
st.table(df)

# Metrics (KPIs)
st.metric("Label", "Value", delta=5)

# Columns of metrics
col1, col2, col3 = st.columns(3)
col1.metric("Metric 1", "100")
col2.metric("Metric 2", "200")
col3.metric("Metric 3", "300")
```

## Charts

```python
# Streamlit built-in
st.line_chart(df)
st.bar_chart(df)
st.area_chart(df)
st.scatter_chart(df)

# Plotly
import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=[1,2,3], y=[1,2,3]))
st.plotly_chart(fig, use_container_width=True)
```

## Input Widgets

```python
# Text
text = st.text_input("Label", "default")
text_area = st.text_area("Multi-line", height=150)

# Number
number = st.number_input("Value", min_value=0, max_value=100, value=50)

# Slider
value = st.slider("Slide", 0, 100, 50)

# Dropdown
option = st.selectbox("Choose:", ["A", "B", "C"])

# Multi-select
selections = st.multiselect("Choose multiple:", ["A", "B", "C"])

# Date & Time
date = st.date_input("Date")
time = st.time_input("Time")

# Radio buttons
choice = st.radio("Pick one:", ["Yes", "No", "Maybe"])

# Checkbox
agreed = st.checkbox("I agree")

# Button
if st.button("Click me"):
    st.write("Clicked!")

# Download
st.download_button("Download", data, file_name="data.csv", mime="text/csv")
```

## Session State

```python
# Initialize
if "count" not in st.session_state:
    st.session_state.count = 0

# Use
if st.button("Add"):
    st.session_state.count += 1

st.write(st.session_state.count)

# Clear all
if st.button("Reset"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()
```

## Caching

```python
# Cache data (API calls, file reads)
@st.cache_data(ttl=3600)  # 1 hour
def load_data():
    return fetch_data()

# Cache resources (models, connections)
@st.cache_resource
def load_model():
    return load_ml_model()

# Clear cache
st.cache_data.clear()
st.cache_resource.clear()
```

## Forms & Callbacks

```python
# Form (batch inputs)
with st.form("my_form"):
    name = st.text_input("Name")
    age = st.number_input("Age")
    submit = st.form_submit_button("Submit")

# Callback (run before re-run)
def on_change():
    st.session_state.changed = True

value = st.slider("Value", on_change=on_change)
```

## Files & Downloads

```python
# File uploader
uploaded = st.file_uploader("Upload file")
if uploaded:
    df = pd.read_csv(uploaded)

# Download
csv = df.to_csv(index=False)
st.download_button("Download CSV", csv, "data.csv", "text/csv")

# JSON
import json
json_str = json.dumps(data)
st.download_button("Download JSON", json_str, "data.json", "application/json")
```

## Control Flow

```python
# Conditional
if condition:
    st.write("True branch")

# Early exit
if error:
    st.error("Error occurred")
    st.stop()  # Stops execution

# Repeat (loop in cache)
results = []
for item in items:
    result = process(item)
    results.append(result)

st.dataframe(pd.DataFrame(results))
```

## API Requests

```python
import requests

# GET request
response = requests.get(url, params={"key": "value"})
data = response.json()

# With error handling
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    st.error(f"Error: {e}")
```

## Loading States

```python
# Spinner
with st.spinner("Loading..."):
    time.sleep(2)

# Progress bar
progress_bar = st.progress(0)
for i in range(100):
    progress_bar.progress(i)
    time.sleep(0.1)

# Status updates
st.status("Processing...", state="running")
```

## Debugging

```python
# Print to console
print("Debug info:", variable)

# Display in app
st.write("Debug:", variable)

# Inspect DataFrame
st.dataframe(df.dtypes)
st.write(df.info())

# Session state
st.write("Session state:", st.session_state)
```

## Configuration (`.streamlit/config.toml`)

```toml
[client]
showErrorDetails = true
toolbarMode = "viewer"

[logger]
level = "info"

[server]
port = 8501
headless = true

[theme]
primaryColor = "#FF6F59"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## Common Patterns

### API Caching
```python
@st.cache_data(ttl=3600)
def fetch_api(endpoint):
    response = requests.get(endpoint)
    return response.json()
```

### Filtered Data
```python
df = load_data()
selected = st.multiselect("Filter:", df.columns)
st.dataframe(df[selected])
```

### Metrics Row
```python
col1, col2, col3 = st.columns(3)
col1.metric("Metric 1", value1)
col2.metric("Metric 2", value2)
col3.metric("Metric 3", value3)
```

### Data Download
```python
csv = df.to_csv(index=False)
st.download_button("Download", csv, "data.csv", "text/csv")
```

### Error Alert
```python
if error:
    st.error("❌ Error message")
else:
    st.success("✅ Success!")
    st.dataframe(df)
```

## Performance Tips

| Problem | Solution |
|---------|----------|
| Slow loads | Use `@st.cache_data` |
| Lost values on re-run | Use `st.session_state` |
| Too many API calls | Cache with TTL |
| Large dataframes | Filter before display |
| Slow charts | Use `use_container_width=True` |

## Deployment

```bash
# Streamlit Cloud
git push  # Deploy automatically from GitHub

# Docker
docker run -p 8501:8501 streamlit-app

# Traditional server
gunicorn --bind 0.0.0.0:8000 app:run_streamlit
```

## Resources

- [Official Docs](https://docs.streamlit.io/)
- [API Reference](https://docs.streamlit.io/library/api-reference)
- [Components Gallery](https://streamlit.io/components)
- [Deployment](https://docs.streamlit.io/deploy/streamlit-cloud)
- [Discord Community](https://discord.com/invite/NUck8HT7uK)
