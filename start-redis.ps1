#!/usr/bin/env pwsh
<#
.SYNOPSIS
Start Redis Server for Celery Broker

.DESCRIPTION
Starts Redis server using Docker (simplest method).
Redis is required for Celery to work with APScheduler.

.PARAMETER Image
Docker image to use (default: redis:latest)

.PARAMETER Port
Redis port (default: 6379)

.EXAMPLE
.\start-redis.ps1

.\start-redis.ps1 -Port 6380

.NOTES
Prerequisites:
- Docker Desktop installed and running

If Docker is not available, install Redis locally:
- Windows: https://github.com/microsoftarchive/redis/releases
- Or use WSL2: wsl sudo apt-get install redis-server
#>

param(
    [string]$Image = "redis:latest",
    [int]$Port = 6379
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Green = @{ ForegroundColor = "Green" }
$Yellow = @{ ForegroundColor = "Yellow" }
$Red = @{ ForegroundColor = "Red" }

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              Redis Server - Celery Broker                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check if Docker is available
try {
    $DockerCheck = docker --version 2>&1
    Write-Host "✅ Docker found: $DockerCheck" @Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop." @Red
    Write-Host "   Download: https://www.docker.com/products/docker-desktop" @Yellow
    exit 1
}

# Check if Redis container is already running
$ExistingContainer = docker ps --filter "name=redis" --format "{{.Names}}" 2>&1 | Select-Object -First 1

if ($ExistingContainer) {
    Write-Host "⚠️  Redis container already running: $ExistingContainer" @Yellow
    Write-Host "   Run: docker stop $ExistingContainer" @Yellow
    Write-Host "   Then retry this script" @Yellow
    exit 0
}

Write-Host "📦 Image: $Image" @Yellow
Write-Host "🔌 Port: $Port" @Yellow
Write-Host ""

Write-Host "🚀 Starting Redis container..." @Green

# Start Redis container
try {
    docker run -d `
        --name redis-natpudan `
        -p ${Port}:6379 `
        $Image `
        redis-server --appendonly yes

    # Wait for container to start
    Start-Sleep -Seconds 2

    # Verify it's running
    $Running = docker ps --filter "name=redis-natpudan" --format "{{.Names}}"
    
    if ($Running) {
        Write-Host "`n✅ Redis started successfully!" @Green
        Write-Host "   Container: redis-natpudan" @Yellow
        Write-Host "   Listening: localhost:$Port" @Yellow
        Write-Host "   Connection: redis://localhost:$Port" @Yellow
        Write-Host "`n📝 To stop Redis:" @Yellow
        Write-Host "   docker stop redis-natpudan" @Yellow
        Write-Host "   docker remove redis-natpudan" @Yellow
    } else {
        Write-Host "❌ Failed to start Redis container" @Red
        exit 1
    }
} catch {
    Write-Host "❌ Error starting Redis: $_" @Red
    exit 1
}
