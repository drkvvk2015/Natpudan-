param(
  [int]$Port = 8000,
  [string]$HostAddr = "127.0.0.1"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"

# If config/ports.json exists, prefer its backend port unless an explicit -Port was supplied by caller
try {
  $configPath = Join-Path $root "config/ports.json"
  if (Test-Path $configPath -and $PSBoundParameters["Port"] -eq $null) {
    $cfg = Get-Content $configPath -Raw | ConvertFrom-Json
    if ($cfg.services.backend.dev) { $Port = [int]$cfg.services.backend.dev }
    if ($cfg.urls.backend.dev) {
      $u = [Uri]$cfg.urls.backend.dev
      if ($u.Host) { $HostAddr = $u.Host }
      if ($u.Port -gt 0) { $Port = $u.Port }
    }
  }
} catch {}
$python = Join-Path $backend ".venv/Scripts/python.exe"

if (-not (Test-Path $python)) {
  Write-Host "Virtual environment Python not found at $python" -ForegroundColor Red
  exit 1
}

Write-Host "Starting backend at http://${HostAddr}:${Port} (no reload)" -ForegroundColor Cyan
Start-Process -FilePath $python -ArgumentList "-m","uvicorn","app.main:app","--host",$HostAddr,"--port",$Port -WorkingDirectory $backend
Write-Host "Waiting for backend to initialize (12s)..." -ForegroundColor Gray
Start-Sleep -Seconds 12
try {
  $h = Invoke-RestMethod -Uri "http://${HostAddr}:${Port}/health" -TimeoutSec 15
  Write-Host "Backend health: $($h.status)" -ForegroundColor Green
} catch {
  Write-Host "Health check timed out (server may still be initializing). Backend is starting..." -ForegroundColor Yellow
  Write-Host "It will be ready in a few seconds. Check: http://${HostAddr}:${Port}/health" -ForegroundColor Gray
}