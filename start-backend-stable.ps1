param(
  [int]$Port = 8000,
  [string]$Host = "127.0.0.1"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"
$python = Join-Path $backend ".venv/Scripts/python.exe"

if (-not (Test-Path $python)) {
  Write-Host "Virtual environment Python not found at $python" -ForegroundColor Red
  exit 1
}

Write-Host "Starting backend at http://$Host:$Port (no reload)" -ForegroundColor Cyan
Start-Process -FilePath $python -ArgumentList "-m","uvicorn","app.main:app","--host",$Host,"--port",$Port -WorkingDirectory $backend
Start-Sleep -Seconds 2
try {
  $h = Invoke-RestMethod -Uri "http://$Host:$Port/health" -TimeoutSec 5
  Write-Host "Backend health: $($h.status)" -ForegroundColor Green
} catch {
  Write-Host "Health check failed. Server may still be starting." -ForegroundColor Yellow
}