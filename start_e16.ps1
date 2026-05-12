Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".env")) {
  Write-Host "Missing .env. Copy .env.example to .env and update values first." -ForegroundColor Red
  exit 1
}

python -m pip install -r requirements.txt

$env:FLASK_APP = "app.py"
flask db upgrade

flask seed

Write-Host "E16 is running at http://127.0.0.1:5000" -ForegroundColor Green
python app.py
