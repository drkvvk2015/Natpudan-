# Quick Start - Backend + Frontend Only
# No Docker, No Celery - Just the essentials

$BackendDir = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend"
$FrontendDir = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\frontend"
$VenvPath = Join-Path $BackendDir "venv"

Write-Host "`n=== NATPUDAN AI - QUICK START ===" -ForegroundColor Cyan
Write-Host "Starting Backend + Frontend...`n" -ForegroundColor Yellow

# Start Backend
Write-Host "[1/2] Starting FastAPI Backend..." -ForegroundColor Green
$backendCmd = "cd '$BackendDir'; . '$VenvPath\Scripts\Activate.ps1'; `$env:DATABASE_URL='sqlite:///./natpudan.db'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process powershell -ArgumentList @('-NoExit', '-Command', $backendCmd)

Start-Sleep -Seconds 5

# Start Frontend
Write-Host "[2/2] Starting React Frontend..." -ForegroundColor Green
$frontendCmd = "cd '$FrontendDir'; npm run dev"
Start-Process powershell -ArgumentList @('-NoExit', '-Command', $frontendCmd)

Start-Sleep -Seconds 3

Write-Host "`n=== SERVICES STARTED ===" -ForegroundColor Cyan
Write-Host "Backend:  http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://127.0.0.1:5173" -ForegroundColor Yellow
Write-Host "API Docs: http://127.0.0.1:8000/docs`n" -ForegroundColor Yellow
Write-Host "Close the terminal windows to stop services" -ForegroundColor Gray
