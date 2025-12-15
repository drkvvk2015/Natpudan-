# Start FastAPI Backend with APScheduler
# Runs with automatic venv activation

$BackendDir = Join-Path (Get-Location) "backend"
$VenvPath = Join-Path $BackendDir "venv"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   FastAPI Backend Startup" -ForegroundColor Cyan
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

# Navigate to backend
Push-Location $BackendDir

try {
    Write-Host "[INFO] Checking Python..." -ForegroundColor Yellow
    python --version
    
    Write-Host "[INFO] Starting FastAPI server..." -ForegroundColor Yellow
    Write-Host "      URL: http://127.0.0.1:8000" -ForegroundColor Cyan
    Write-Host "      Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
    Write-Host "`n[INFO] Server is running...`n" -ForegroundColor Green
    Write-Host "Logs will appear below:" -ForegroundColor Gray
    Write-Host "----------------------------------------`n" -ForegroundColor Gray
    
    # Start the server
    python -m uvicorn app.main:app `
        --reload `
        --host 127.0.0.1 `
        --port 8000 `
        --timeout-keep-alive 120

} catch {
    Write-Host "`n[ERROR] Failed to start backend: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
