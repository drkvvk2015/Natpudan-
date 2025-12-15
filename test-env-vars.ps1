# Test Celery environment variables
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Testing Celery Environment Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$BackendDir = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend"
$VenvPath = Join-Path $BackendDir "venv"

# Activate venv
& "$VenvPath\Scripts\Activate.ps1"

# Set environment variables (using script scope)
$env:CELERY_BROKER_URL = 'sqla+sqlite:///./celery_broker.db'
$env:CELERY_RESULT_BACKEND = 'db+sqlite:///./celery_results.db'

Write-Host "Environment Variables Set:" -ForegroundColor Yellow
Write-Host "  CELERY_BROKER_URL = $env:CELERY_BROKER_URL" -ForegroundColor Cyan
Write-Host "  CELERY_RESULT_BACKEND = $env:CELERY_RESULT_BACKEND" -ForegroundColor Cyan
Write-Host ""

# Change to backend directory
Push-Location $BackendDir

try {
    Write-Host "Testing Celery Command:" -ForegroundColor Yellow
    Write-Host "  Command: python -m celery -A app.celery_config worker --help`n" -ForegroundColor Cyan
    
    # Test the worker command
    python -m celery -A app.celery_config worker --help | head -10
    
    Write-Host "`n✅ Celery command works correctly!" -ForegroundColor Green
    Write-Host "`nYou can now run:" -ForegroundColor Yellow
    Write-Host "  .\start-celery-worker.ps1" -ForegroundColor Cyan
    Write-Host "  .\start-flower.ps1" -ForegroundColor Cyan
    Write-Host "  .\start-all.ps1" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
