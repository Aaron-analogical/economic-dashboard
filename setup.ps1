# Quick Setup Script for Windows PowerShell

Write-Host "Setting up US Economic Data Warehouse..." -ForegroundColor Green

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python not found. Please install Python 3.9+ from python.org" -ForegroundColor Red
    exit 1
}

Write-Host "OK: Python found" -ForegroundColor Green

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Cyan
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip setuptools wheel

# Install requirements
Write-Host "Installing Streamlit dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt
deactivate

# Pipeline environment (dbt and Streamlit need conflicting protobuf versions)
Write-Host "Creating pipeline virtual environment (ingestion + dbt)..." -ForegroundColor Cyan
python -m venv .venv-pipeline
& ".\.venv-pipeline\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv-pipeline\Scripts\python.exe" -m pip install -r requirements-pipeline.txt

# Create .env file from .env.example
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host "NOTE: Please edit .env and fill in your FRED API key and database credentials" -ForegroundColor Yellow
}
else {
    Write-Host "OK: .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Get a FRED API key at: https://fred.stlouisfed.org/docs/api/" -ForegroundColor White
Write-Host "2. Edit .env with your FRED API key and database credentials" -ForegroundColor White
Write-Host "3. Load raw data:  .\.venv-pipeline\Scripts\python.exe -m ingestion.load_raw" -ForegroundColor White
Write-Host "4. Build models:   cd dbt; dbt deps --profiles-dir .; dbt build --profiles-dir .  (see README for env vars)" -ForegroundColor White
Write-Host "5. Open powerbi\EconomicDashboard.pbip in Power BI Desktop and set PgHost / PgDatabase" -ForegroundColor White
Write-Host "6. Optional Streamlit app: .env\Scripts\streamlit.exe run Home.py" -ForegroundColor White
