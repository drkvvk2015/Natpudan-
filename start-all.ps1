# Natpudan AI - Full Stack Startup Script (SQLite Edition)
# Starts all services: Backend, Celery, Flower, Frontend (No Docker needed)

param([switch]$Help)

if ($Help) {
    Write-Host "`nNatpudan AI - Full Stack SQLite Setup" -ForegroundColor Cyan
    Write-Host "Usage: .\start-all.ps1`n" -ForegroundColor Yellow
    Write-Host "Starts all services in separate terminal windows" -ForegroundColor Gray
    Write-Host "Database: SQLite (no Docker required)" -ForegroundColor Gray
    exit 0
}

$RootDir = Get-Location
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$VenvPath = Join-Path $BackendDir ".venv"
$DbPath = Join-Path $BackendDir "natpudan.db"

Write-Host "`n=== NATPUDAN AI - FULL STACK STARTUP (SQLite) ===" -ForegroundColor Cyan
Write-Host "Starting all services...`n" -ForegroundColor Yellow

# 0. Setup Database (SQLite)
Write-Host "[0/5] Initializing SQLite database..." -ForegroundColor Green
if (Test-Path $DbPath) {
    Remove-Item $DbPath -Force 2>$null
    Write-Host "  Cleared old database" -ForegroundColor Gray
}
Write-Host "  SQLite database path: $DbPath" -ForegroundColor Gray

# 1. Backend
Write-Host "[1/5] Starting FastAPI Backend..." -ForegroundColor Green
$backendScript = Join-Path $RootDir "start-backend-stable.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", $backendScript
Start-Sleep -Seconds 8

# 2. Celery Worker
Write-Host "[2/5] Starting Celery Worker..." -ForegroundColor Green
$celeryScript = Join-Path $RootDir "start-celery-worker.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", $celeryScript
Start-Sleep -Seconds 4

# 3. Flower Dashboard (only if using Redis/RabbitMQ broker)
$useRedis = $env:REDIS_URL -and $env:REDIS_URL.Trim() -ne ''
if ($useRedis) {
    Write-Host "[3/5] Starting Flower Dashboard..." -ForegroundColor Green
    $flowerCmd = @"
cd "$BackendDir"
& "$VenvPath\Scripts\Activate.ps1"
python -m celery -A app.celery_config flower --port=5555 --basic_auth=admin:admin
"@
    Start-Process powershell -NoNewWindow -ArgumentList "-NoExit", "-Command", $flowerCmd
    Start-Sleep -Seconds 3
} else {
    Write-Host "[3/5] Skipping Flower: requires Redis or RabbitMQ broker (set REDIS_URL)." -ForegroundColor Yellow
    Write-Host "      Tip: .\start-redis.ps1 then set REDIS_URL=redis://localhost:6379/0" -ForegroundColor DarkYellow
}

# 4. Frontend
Write-Host "[4/5] Starting React Frontend..." -ForegroundColor Green
$frontendCmd = "cd '$FrontendDir'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd
Start-Sleep -Seconds 4

Write-Host "`n=== ALL SERVICES STARTED ===" -ForegroundColor Cyan
Write-Host "`nSERVICE ENDPOINTS:" -ForegroundColor Yellow
Write-Host "  Frontend:        http://localhost:5173" -ForegroundColor White
Write-Host "  Backend API:     http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:        http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Flower:          http://localhost:5555 (admin/admin)" -ForegroundColor White
Write-Host "" -ForegroundColor Gray
Write-Host "DATABASE:" -ForegroundColor Yellow
Write-Host "  SQLite:          $DbPath" -ForegroundColor White
Write-Host "  Celery Broker:   $BackendDir\celery_broker.db" -ForegroundColor White
Write-Host "  Celery Results:  $BackendDir\celery_results.db" -ForegroundColor White

Write-Host "`nAI FEATURES:" -ForegroundColor Yellow
Write-Host "  OpenAI API:      ENABLED" -ForegroundColor Green
Write-Host "  Medical Diagnosis: Available" -ForegroundColor Green
Write-Host "  Knowledge Base:  Ready for upload" -ForegroundColor Green
Write-Host "  Drug Checker:    Available" -ForegroundColor Green

Write-Host "`nTo stop all services:" -ForegroundColor Gray
Write-Host "  1. Close the individual terminal windows" -ForegroundColor Gray
Write-Host "  2. Or run: taskkill /F /IM powershell.exe" -ForegroundColor Gray

Write-Host "`nPress Ctrl+C to exit this window`n" -ForegroundColor Gray
while ($true) { Start-Sleep -Seconds 10 }

