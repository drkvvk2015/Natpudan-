<#
.SYNOPSIS
Start Natpudan AI with Podman Compose
.DESCRIPTION
Starts all services (Backend, Frontend, Database, Redis, Celery) using Podman Compose
.EXAMPLE
.\start-podman-compose.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Natpudan AI - Podman Compose Startup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check prerequisites
Write-Host "[1/4] Checking Podman installation..." -ForegroundColor Yellow

$podmanCmd = (Get-Command podman -ErrorAction SilentlyContinue).Path
if (-not $podmanCmd) {
    Write-Error "Podman not found. Please install Podman first: https://podman.io/docs/installation/windows"
    exit 1
}

Write-Host "  [OK] Podman found: $podmanCmd" -ForegroundColor Green

# Check Podman Compose
$podmanComposeCmd = (Get-Command podman-compose -ErrorAction SilentlyContinue).Path
if (-not $podmanComposeCmd) {
    Write-Error "podman-compose not found. Install with: pip install podman-compose"
    exit 1
}

Write-Host "  [OK] Podman Compose found: $podmanComposeCmd" -ForegroundColor Green

# Check Podman machine status
Write-Host "`n[2/4] Checking Podman Machine..." -ForegroundColor Yellow

try {
    $machineStatus = podman machine list --format=json | ConvertFrom-Json
    $isRunning = $machineStatus | Where-Object { $_.IsRunning -eq $true }
    
    if (-not $isRunning) {
        Write-Host "  [!] Podman Machine not running. Starting..." -ForegroundColor Yellow
        podman machine start
        Start-Sleep -Seconds 5
    }
    
    Write-Host "  [OK] Podman Machine is running" -ForegroundColor Green
} catch {
    Write-Host "  [!] Could not check Podman Machine status" -ForegroundColor Yellow
}

# Check .env file
Write-Host "`n[3/4] Checking environment configuration..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "  [!] .env file not found" -ForegroundColor Yellow
    Write-Host "      Creating .env from template..." -ForegroundColor Gray
    
    $envTemplate = @"
# Natpudan AI - Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
POSTGRES_USER=physician_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=physician_ai
ENVIRONMENT=production
DEBUG=False
"@
    
    $envTemplate | Out-File -FilePath ".env" -Encoding ASCII
    Write-Host "  [OK] Created .env file - UPDATE WITH YOUR KEYS!" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] .env file found" -ForegroundColor Green
}

# Start services
Write-Host "`n[4/4] Starting services with Podman Compose..." -ForegroundColor Yellow

try {
    podman-compose up -d
    
    if ($LASTEXITCODE -ne 0) {
        throw "podman-compose failed with exit code $LASTEXITCODE"
    }
    
    Write-Host "  [OK] Services started" -ForegroundColor Green
} catch {
    Write-Error "Failed to start services: $_"
    exit 1
}

# Wait for services to be ready
Write-Host "`n[Waiting for services...]" -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Show status
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Services Started Successfully!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Service Status:" -ForegroundColor Cyan
podman-compose ps

Write-Host "`nAccess Points:" -ForegroundColor Cyan
Write-Host "  Backend API:        http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "  Frontend:           http://127.0.0.1:3000" -ForegroundColor Yellow
Write-Host "  PostgreSQL:         127.0.0.1:5432" -ForegroundColor Yellow
Write-Host "  Redis:              127.0.0.1:6379" -ForegroundColor Yellow
Write-Host "  Flower (Tasks):     http://127.0.0.1:5555" -ForegroundColor Yellow

Write-Host "`nUseful Commands:" -ForegroundColor Cyan
Write-Host "  View logs:          podman-compose logs -f [service]" -ForegroundColor Gray
Write-Host "  Stop services:      podman-compose down" -ForegroundColor Gray
Write-Host "  Rebuild images:     podman-compose build --no-cache" -ForegroundColor Gray
Write-Host "  Execute command:    podman-compose exec backend [command]" -ForegroundColor Gray

Write-Host "`nNote: Press Ctrl+C to close this window (services continue running)" -ForegroundColor Gray
Write-Host ""

# Keep window open and show live logs
Write-Host "Showing live logs (press Ctrl+C to stop):`n" -ForegroundColor Cyan
podman-compose logs -f
