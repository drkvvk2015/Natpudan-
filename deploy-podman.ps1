#!/usr/bin/env pwsh
# Deploy Natpudan AI in Podman - Production Setup

$ProjectRoot = Get-Location
$EnvFile = "$ProjectRoot\.env.prod.local"

Write-Host "Starting Natpudan AI Podman Deployment..." -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
if (-not (Get-Command podman -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Podman not found" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Podman $(podman --version)" -ForegroundColor Green

if (-not (Get-Command podman-compose -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: podman-compose not found" -ForegroundColor Red
    exit 1
}
Write-Host "OK: podman-compose found" -ForegroundColor Green

if (-not (Test-Path $EnvFile)) {
    Write-Host "ERROR: Environment file not found: $EnvFile" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Environment file loaded" -ForegroundColor Green

# Create directories
Write-Host ""
Write-Host "Creating required directories..." -ForegroundColor Yellow
@("nginx", "backend/data/uploads", "backend/logs", "backend/cache", "frontend/logs") | ForEach-Object {
    $dir = $_
    $fullPath = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  Exists: $dir" -ForegroundColor Cyan
    }
}

# Deploy services
Write-Host ""
Write-Host "Deploying services..." -ForegroundColor Yellow
Write-Host ""

Push-Location $ProjectRoot
try {
    $env:COMPOSE_PROJECT_NAME = "natpudan"
    & podman-compose --env-file $EnvFile up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Deployment failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "Waiting for services to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Show status
    Write-Host ""
    Write-Host "Service Status:" -ForegroundColor Yellow
    & podman-compose ps
    
    Write-Host ""
    Write-Host "Checking backend health..." -ForegroundColor Yellow
    
    $maxRetries = 30
    $retry = 0
    $ok = $false
    
    while ($retry -lt $maxRetries -and -not $ok) {
        try {
            $health = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2 -ErrorAction Stop
            if ($health.StatusCode -eq 200) {
                Write-Host "OK: Backend is healthy" -ForegroundColor Green
                $ok = $true
            }
        } catch {
            $retry++
            if ($retry % 5 -eq 0) {
                Write-Host "  Waiting... (attempt $retry/$maxRetries)" -ForegroundColor Cyan
            }
            Start-Sleep -Seconds 1
        }
    }
    
    if (-not $ok) {
        Write-Host "WARNING: Backend health check timeout" -ForegroundColor Yellow
    }
    
    # Success message
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access Points:" -ForegroundColor Cyan
    Write-Host "  Frontend: http://127.0.0.1:3000" -ForegroundColor Yellow
    Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
    Write-Host "  Health:   http://127.0.0.1:8000/health" -ForegroundColor Yellow
    Write-Host "  Flower:   http://127.0.0.1:5555" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Running Services:" -ForegroundColor Cyan
    Write-Host "  - backend   (FastAPI on 8000)" -ForegroundColor White
    Write-Host "  - frontend  (Vite on 3000)" -ForegroundColor White
    Write-Host "  - db        (PostgreSQL on 5432)" -ForegroundColor White
    Write-Host "  - redis     (Redis on 6379)" -ForegroundColor White
    Write-Host "  - celery    (Async workers)" -ForegroundColor White
    Write-Host "  - flower    (Task monitoring on 5555)" -ForegroundColor White
    Write-Host "  - nginx     (Reverse proxy on 80/443)" -ForegroundColor White
    Write-Host ""
    Write-Host "Useful Commands:" -ForegroundColor Cyan
    Write-Host "  Logs:    podman-compose logs -f backend" -ForegroundColor Gray
    Write-Host "  Stop:    podman-compose down" -ForegroundColor Gray
    Write-Host "  Shell:   podman-compose exec backend bash" -ForegroundColor Gray
    Write-Host ""
    Write-Host "IMPORTANT: Change default credentials in .env.prod.local for production!" -ForegroundColor Red
    Write-Host ""
    
} finally {
    Pop-Location
}
