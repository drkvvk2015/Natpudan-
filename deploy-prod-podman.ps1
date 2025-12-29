#!/usr/bin/env pwsh
<#
.SYNOPSIS
Deploy Natpudan AI Medical Assistant in Podman - Production Setup

.DESCRIPTION
This script deploys all 7 services (backend, frontend, PostgreSQL, Redis, Celery, Flower, Nginx) 
using podman-compose with production configuration.

.EXAMPLE
.\deploy-prod-podman.ps1

#>

$ErrorActionPreference = "Stop"
$ProjectRoot = (Get-Location).Path
$EnvFile = "$ProjectRoot\.env.prod.local"

Write-Host "🚀 Natpudan AI - Production Podman Deployment" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
if (-not (Get-Command podman -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Podman not found. Please install Podman for Windows" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Podman: $(podman --version)" -ForegroundColor Green

if (-not (Get-Command podman-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ podman-compose not found. Please install it" -ForegroundColor Red
    exit 1
}
Write-Host "✅ podman-compose: $(podman-compose --version)" -ForegroundColor Green

if (-not (Test-Path $EnvFile)) {
    Write-Host "❌ Environment file not found: $EnvFile" -ForegroundColor Red
    Write-Host "   Please copy .env.prod to .env.prod.local and configure it" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Environment file loaded: $EnvFile" -ForegroundColor Green

# Create required directories
Write-Host ""
Write-Host "📁 Creating required directories..." -ForegroundColor Yellow
$dirs = @(
    "nginx",
    "backend/data/uploads",
    "backend/logs",
    "backend/cache",
    "frontend/logs"
)
foreach ($dir in $dirs) {
    $fullPath = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "   ✅ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "   ✔️  Exists: $dir" -ForegroundColor Cyan
    }
}

# Copy nginx config if doesn't exist
if (-not (Test-Path "nginx/nginx.conf")) {
    Write-Host "   ⚠️  nginx.conf missing - you may need to configure SSL" -ForegroundColor Yellow
}

# Deploy
Write-Host ""
Write-Host "🐳 Starting Podman services..." -ForegroundColor Yellow
Write-Host "   Running: podman-compose --env-file '$EnvFile' up -d" -ForegroundColor Cyan
Write-Host ""

Push-Location $ProjectRoot
try {
    # Set environment variable for podman-compose
    $env:COMPOSE_PROJECT_NAME = "natpudan"
    
    # Start all services
    & podman-compose --env-file $EnvFile --file docker-compose.yml up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Deployment failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "⏳ Waiting for services to become healthy..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Check service status
    Write-Host ""
    Write-Host "📊 Service Status:" -ForegroundColor Yellow
    & podman-compose ps
    
    Write-Host ""
    Write-Host "🔍 Checking health endpoints..." -ForegroundColor Yellow
    
    $maxRetries = 30
    $retry = 0
    $backend_ok = $false
    
    while ($retry -lt $maxRetries -and -not $backend_ok) {
        try {
            $health = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2 -ErrorAction Stop
            if ($health.StatusCode -eq 200) {
                Write-Host "✅ Backend health check passed" -ForegroundColor Green
                $backend_ok = $true
            }
        } catch {
            $retry++
            if ($retry % 5 -eq 0) {
                Write-Host "   ⏳ Waiting for backend... (attempt $retry/$maxRetries)" -ForegroundColor Cyan
            }
            Start-Sleep -Seconds 1
        }
    }
    
    if (-not $backend_ok) {
        Write-Host "⚠️  Backend health check timeout - services may still be initializing" -ForegroundColor Yellow
    }
    
    # Display access information
    Write-Host ""
    Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access Points:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Frontend (Web UI):" -ForegroundColor White
    Write-Host "    -> http://127.0.0.1:3000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Backend (API):" -ForegroundColor White
    Write-Host "    -> http://127.0.0.1:8000" -ForegroundColor Yellow
    Write-Host "    -> http://127.0.0.1:8000/docs (OpenAPI docs)" -ForegroundColor Yellow
    Write-Host "    -> http://127.0.0.1:8000/health (Health check)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Task Monitoring:" -ForegroundColor White
    Write-Host "    -> http://127.0.0.1:5555 (Flower dashboard)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Running Services:" -ForegroundColor Cyan
    Write-Host "  • backend       - FastAPI application server" -ForegroundColor White
    Write-Host "  • frontend      - Vite/React application" -ForegroundColor White
    Write-Host "  • db            - PostgreSQL database (port 5432)" -ForegroundColor White
    Write-Host "  • redis         - Redis cache/broker (port 6379)" -ForegroundColor White
    Write-Host "  • celery        - Celery worker (async tasks)" -ForegroundColor White
    Write-Host "  • flower        - Flower monitoring dashboard" -ForegroundColor White
    Write-Host "  • nginx         - Reverse proxy (ports 80/443)" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Useful Commands:" -ForegroundColor Cyan
    Write-Host "  View logs:       podman-compose logs -f backend" -ForegroundColor Gray
    Write-Host "  Stop services:   podman-compose down" -ForegroundColor Gray
    Write-Host "  Restart:         podman-compose restart" -ForegroundColor Gray
    Write-Host "  Shell access:    podman-compose exec backend bash" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️  IMPORTANT NOTES:" -ForegroundColor Yellow
    Write-Host "  1. Default credentials (CHANGE THESE in production!):" -ForegroundColor White
    Write-Host "     - Database: physician_user / Secure@Password123#$%" -ForegroundColor Gray
    Write-Host "     - Admin account: auto-created on first startup" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. To access as admin, use the login page and sign up first" -ForegroundColor White
    Write-Host "     (Admin promotion happens on first user registration)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Check logs for errors:" -ForegroundColor White
    Write-Host "     podman-compose logs" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📚 Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Open browser to http://127.0.0.1:3000" -ForegroundColor White
    Write-Host "  2. Register an account (first user becomes admin)" -ForegroundColor White
    Write-Host "  3. Configure OpenAI API key in .env.prod.local if not set" -ForegroundColor White
    Write-Host "  4. Check /health endpoint for system status" -ForegroundColor White
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Green
    
} finally {
    Pop-Location
}
