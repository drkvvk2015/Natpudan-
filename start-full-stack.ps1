# Natpudan Full Stack Startup Script

$BackendPath = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend"
$FrontendPath = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\frontend"
$VenvPath = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\.venv"
$PythonExe = "$VenvPath\Scripts\python.exe"
$MemuraiPath = "C:\Program Files\Memurai\memurai.exe"

Write-Host "`n========================================"  -ForegroundColor Cyan
Write-Host "   Natpudan Full Stack Startup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Memurai
Write-Host "[1/4] Checking Memurai Redis..." -ForegroundColor Yellow
if (Get-Process -Name "memurai" -ErrorAction SilentlyContinue) {
    Write-Host "       Memurai already running" -ForegroundColor Green
} elseif (Test-Path $MemuraiPath) {
    Start-Process -FilePath $MemuraiPath -ArgumentList "--port 6379" -WindowStyle Hidden
    Start-Sleep -Seconds 2
    Write-Host "       Memurai started" -ForegroundColor Green
} else {
    Write-Host "       Memurai not found" -ForegroundColor Red
    exit 1
}

# Start Backend
Write-Host "`n[2/4] Starting Backend (port 9000)..." -ForegroundColor Yellow
$env:PYTHONPATH = $BackendPath
$backendCmd = "cd '$BackendPath'; `$env:PYTHONPATH='$BackendPath'; & '$PythonExe' -m uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
Write-Host "       Backend starting" -ForegroundColor Green
Start-Sleep -Seconds 3

# Start Celery
Write-Host "`n[3/4] Starting Celery Worker..." -ForegroundColor Yellow
$celeryCmd = "cd '$BackendPath'; `$env:PYTHONPATH='$BackendPath'; & '$PythonExe' -m celery -A app.celery_config worker --loglevel=info --pool=solo -E"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $celeryCmd -WindowStyle Minimized
Write-Host "       Celery started" -ForegroundColor Green
Start-Sleep -Seconds 2

# Start Frontend
Write-Host "`n[4/4] Starting Frontend (port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendPath'; npm run dev:5173"
Write-Host "       Frontend starting" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "   All Services Started!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
Write-Host "Open: http://127.0.0.1:5173`n" -ForegroundColor Cyan
