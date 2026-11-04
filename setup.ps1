# Quick Setup Script for Windows PowerShell

Write-Host "Setting up Economic Data Warehouse..." -ForegroundColor Green

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python not found. Please install Python 3.10+ from python.org" -ForegroundColor Red
    exit 1
}

Write-Host "OK: Python found" -ForegroundColor Green

# Virtual environment with the pipeline (ingestion + dbt) and pytest
Write-Host "Creating virtual environment..." -ForegroundColor Cyan
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements-dev.txt

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
Write-Host "3. Run the tests:  .\.venv\Scripts\python.exe -m pytest" -ForegroundColor White
Write-Host "4. Load raw data:  .\.venv\Scripts\python.exe -m ingestion.load_raw; .\.venv\Scripts\python.exe -m ingestion.load_worldbank" -ForegroundColor White
Write-Host "5. Build models:   cd dbt; dbt deps --profiles-dir .; dbt build --profiles-dir .  (see README for env vars)" -ForegroundColor White
Write-Host "6. Open powerbi\EconomicDashboard.pbip in Power BI Desktop and set PgHost / PgDatabase" -ForegroundColor White
