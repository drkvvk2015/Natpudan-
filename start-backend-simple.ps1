# Simple backend startup - no Celery, no multi-window complexity
# Just backend + frontend

$RootDir = Get-Location
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$VenvPath = Join-Path $BackendDir ".venv"

Write-Host "`n=== NATPUDAN - BACKEND + FRONTEND ===" -ForegroundColor Cyan
Write-Host "Starting backend on http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Starting frontend on http://127.0.0.1:5173" -ForegroundColor Yellow
Write-Host ""

# Backend in new window
Write-Host "[1/2] Opening Backend window..." -ForegroundColor Green
$backendScript = Join-Path $RootDir "start-backend-stable.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", $backendScript
Start-Sleep -Seconds 5

# Frontend in new window
Write-Host "[2/2] Opening Frontend window..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendDir'; npm run dev"
Start-Sleep -Seconds 3

Write-Host "`n✅ Both services launched in separate windows" -ForegroundColor Green
Write-Host "   Backend:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "   Frontend: http://127.0.0.1:5173" -ForegroundColor White
Write-Host "   Docs:     http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
