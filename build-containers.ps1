#!/usr/bin/env pwsh
# Build containers sequentially to avoid timeout issues

Write-Host "=== BUILDING NATPUDAN CONTAINERS ===" -ForegroundColor Cyan
Write-Host ""

# Stop and remove existing containers
Write-Host "[1/6] Cleaning up existing containers..." -ForegroundColor Yellow
python.exe -m podman_compose down 2>$null

# Build backend image (used by backend, celery, flower)
Write-Host "[2/6] Building backend image..." -ForegroundColor Yellow
podman build -t natpudan-backend:latest ./backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Backend build failed!" -ForegroundColor Red
    exit 1
}

# Build frontend image
Write-Host "[3/6] Building frontend image..." -ForegroundColor Yellow
podman build -t natpudan-frontend:latest `
    --build-arg VITE_API_BASE_URL=http://localhost:8000 `
    --build-arg VITE_WS_URL=ws://localhost:8000 `
    ./frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Frontend build failed!" -ForegroundColor Red
    exit 1
}

# Pull PostgreSQL image
Write-Host "[4/6] Pulling PostgreSQL image..." -ForegroundColor Yellow
podman pull postgres:15-alpine
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PostgreSQL pull failed!" -ForegroundColor Red
    exit 1
}

# Pull Redis image
Write-Host "[5/6] Pulling Redis image..." -ForegroundColor Yellow
podman pull redis:7-alpine
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Redis pull failed!" -ForegroundColor Red
    exit 1
}

# Pull Nginx image
Write-Host "[6/6] Pulling Nginx image..." -ForegroundColor Yellow
podman pull nginx:alpine
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Nginx pull failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "All images built successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Run './start-all.ps1 -UsePodman' to start the containers" -ForegroundColor Cyan
