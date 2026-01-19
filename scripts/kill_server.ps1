# Kill Flask Server Script
# Run this if Ctrl+C doesn't stop the server cleanly

Write-Host "Stopping all Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

Start-Sleep -Seconds 1

$remaining = Get-Process python -ErrorAction SilentlyContinue
if ($remaining) {
    Write-Host "Warning: Some Python processes are still running:" -ForegroundColor Red
    $remaining | Select-Object Id, ProcessName, StartTime
} else {
    Write-Host "All Python processes stopped successfully!" -ForegroundColor Green
}

