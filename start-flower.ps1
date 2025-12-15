# Start Flower Monitoring Dashboard for Celery
# Web UI to monitor tasks and workers at http://localhost:5555

$BackendDir = Join-Path (Get-Location) "backend"
$VenvPath = Join-Path $BackendDir "venv"
$Port = 5555

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Flower Monitoring Dashboard" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Activate virtual environment (if not already active)
$venvActive = Test-Path env:VIRTUAL_ENV
if (-not $venvActive) {
    if (Test-Path $VenvPath) {
        Write-Host "[INFO] Using virtual environment..." -ForegroundColor Yellow
        & "$VenvPath\Scripts\Activate.ps1"
    } else {
        Write-Host "[WARNING] Virtual environment not found" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "[INFO] Virtual environment already active" -ForegroundColor Green
}

# Change to backend
Push-Location $BackendDir

try {
    Write-Host "[INFO] Starting Flower dashboard..." -ForegroundColor Yellow
    Write-Host "      URL: http://localhost:$Port" -ForegroundColor Cyan
    Write-Host "      Username: admin" -ForegroundColor Cyan
    Write-Host "      Password: admin" -ForegroundColor Cyan
    Write-Host "`n[INFO] Open browser to http://localhost:$Port`n" -ForegroundColor Green
    Write-Host "Logs will appear below:" -ForegroundColor Gray
    Write-Host "----------------------------------------`n" -ForegroundColor Gray
    
    # Set Celery broker and result backend for SQLite
    $env:CELERY_BROKER_URL = 'sqla+sqlite:///./celery_broker.db'
    $env:CELERY_RESULT_BACKEND = 'db+sqlite:///./celery_results.db'
    
    # Start Flower
    python -m celery -A app.celery_config flower `
        --port=$Port `
        --basic_auth=admin:admin

} catch {
    Write-Host "`n[ERROR] Failed to start Flower: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
