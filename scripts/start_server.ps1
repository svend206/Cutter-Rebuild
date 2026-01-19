# Clean Start Flask Server Script
# This kills any existing Python processes first, then starts fresh

Write-Host "Cleaning up any existing Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

Write-Host "Starting Flask server..." -ForegroundColor Green

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$appPath = Join-Path $repoRoot "app.py"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found in PATH. Install Python 3.11+ or fix PATH." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $appPath)) {
    Write-Host "app.py not found in repo root: $appPath" -ForegroundColor Red
    exit 1
}

Set-Location $repoRoot
python app.py

