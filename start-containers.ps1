# Start database containers only
$ErrorActionPreference = "Stop"

Write-Host "=== Starting Database Containers ===" -ForegroundColor Cyan

Write-Host "Starting PostgreSQL and Redis..." -ForegroundColor Yellow
python.exe -m podman_compose -f docker-compose.simple.yml up -d

Write-Host "Waiting for services..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Container Status:" -ForegroundColor Yellow
podman ps

Write-Host ""
Write-Host "=== READY ===" -ForegroundColor Green
Write-Host "PostgreSQL: localhost:5432 (natpudan/natpudan123)" -ForegroundColor Gray
Write-Host "Redis:      localhost:6379" -ForegroundColor Gray
Write-Host ""
Write-Host "Start backend: cd backend; uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "Start frontend: cd frontend; npm run dev" -ForegroundColor White
