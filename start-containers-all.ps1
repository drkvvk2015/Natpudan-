# Start ALL services in Podman containers with pre-installed dependencies
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== NATPUDAN - ALL CONTAINERS STARTUP ===" -ForegroundColor Cyan
Write-Host ""

# Stop existing
Write-Host "[1/4] Stopping existing containers..." -ForegroundColor Yellow
python -m podman_compose -f docker-compose.simple.yml down 2>$null

# Start databases
Write-Host "[2/4] Starting PostgreSQL + Redis..." -ForegroundColor Yellow
python -m podman_compose -f docker-compose.simple.yml up -d

Write-Host "[3/4] Waiting for databases..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Start backend in container with volume mount
Write-Host "[4/4] Starting Backend container..." -ForegroundColor Yellow
podman run -d --name natpudan-backend `
  --network container:natpudan_db_1 `
  -v "${PWD}/backend:/app:Z" `
  -w /app `
  -e DATABASE_URL=postgresql://natpudan:natpudan123@localhost:5432/natpudan `
  -e REDIS_URL=redis://localhost:6379/0 `
  -p 8000:8000 `
  mirror.gcr.io/library/python:3.12-slim `
  bash -c "pip install -q uvicorn && uvicorn app.main:app --host 0.0.0.0 --port 8000"

Write-Host ""
Write-Host "=== CONTAINERS RUNNING ===" -ForegroundColor Green
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""
Write-Host "Backend:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "Postgres: localhost:5432" -ForegroundColor Gray
Write-Host "Redis:    localhost:6379" -ForegroundColor Gray
Write-Host ""
Write-Host "Start frontend locally: cd frontend; npm run dev" -ForegroundColor Yellow
