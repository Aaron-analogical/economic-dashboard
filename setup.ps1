# Quick Setup Script for Windows PowerShell

Write-Host "Setting up Streamlit Dashboard..." -ForegroundColor Green

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
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r streamlit/requirements.txt

# Create .env file from .env.example
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host "NOTE: Please edit .env and add your FRED API key" -ForegroundColor Yellow
}
else {
    Write-Host "OK: .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Get a FRED API key at: https://fred.stlouisfed.org/docs/api/" -ForegroundColor White
Write-Host "2. Edit .env and add your API key" -ForegroundColor White
Write-Host "3. Run: streamlit run app.py" -ForegroundColor White
Write-Host ""
Write-Host "App will open at: http://localhost:8501" -ForegroundColor Cyan
