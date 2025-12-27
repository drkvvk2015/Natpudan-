# Start Celery Worker for APScheduler + Celery
# Executes background tasks scheduled by APScheduler

$BackendDir = Join-Path (Get-Location) "backend"
$VenvPath = Join-Path $BackendDir ".venv"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Celery Worker Startup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Activate virtual environment (if not already active)
$venvActive = Test-Path env:VIRTUAL_ENV
if (-not $venvActive) {
    if (Test-Path $VenvPath) {
        Write-Host "[INFO] Using virtual environment..." -ForegroundColor Yellow
        & "$VenvPath\Scripts\Activate.ps1"
    } else {
        Write-Host "[WARNING] Virtual environment not found" -ForegroundColor Yellow
        Write-Host "[INFO] Creating virtual environment..." -ForegroundColor Yellow
        python -m venv $VenvPath
        & "$VenvPath\Scripts\Activate.ps1"
        Write-Host "[INFO] Installing dependencies..." -ForegroundColor Yellow
        pip install -q -r "$BackendDir\requirements.txt"
    }
} else {
    Write-Host "[INFO] Virtual environment already active" -ForegroundColor Green
}

# Change to backend directory and set PYTHONPATH
Push-Location $BackendDir

# Ensure the backend directory is in PYTHONPATH for worker subprocesses
$env:PYTHONPATH = $BackendDir

try {
    Write-Host "[INFO] Starting Celery worker..." -ForegroundColor Yellow
    Write-Host "      App: app.celery_config" -ForegroundColor Cyan
    Write-Host "      Concurrency: 1 worker (Windows compatibility)" -ForegroundColor Cyan
    Write-Host "      Pool: solo (Windows requirement)" -ForegroundColor Cyan
    Write-Host "      Log level: info" -ForegroundColor Cyan
    Write-Host "      Task events: ENABLED (-E)" -ForegroundColor Cyan
    Write-Host "`n[INFO] Worker ready and waiting for tasks...`n" -ForegroundColor Green
    Write-Host "Logs will appear below:" -ForegroundColor Gray
    Write-Host "----------------------------------------`n" -ForegroundColor Gray
    
    # Start the worker with solo pool for Windows compatibility
    # Solo pool runs tasks in the main process, avoiding subprocess import issues
    celery -A app.celery_config worker `
        --pool=solo `
        --loglevel=info `
        -E
    
} catch {
    Write-Host "`n[ERROR] Failed to start worker: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
