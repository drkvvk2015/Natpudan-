#!/usr/bin/env pwsh
<#
.SYNOPSIS
Start Celery Worker for Background Tasks (APScheduler + Celery Combined)

.DESCRIPTION
Starts a Celery worker to process background tasks submitted by APScheduler.
This enables high-performance, scalable knowledge base updates.

.PARAMETER WorkerName
Name of the worker (default: worker1)

.PARAMETER Concurrency
Number of concurrent tasks (default: 4)

.PARAMETER LogLevel
Log level (DEBUG, INFO, WARNING, ERROR)

.EXAMPLE
.\start-celery-worker.ps1

.\start-celery-worker.ps1 -WorkerName doctor-worker -Concurrency 8

.NOTES
Requirements:
- Python 3.10+
- Redis server running (localhost:6379 or REDIS_URL env var)
- Celery and dependencies installed (pip install -r requirements.txt)

Start Redis first:
  Option 1: Docker - docker run -d -p 6379:6379 redis:latest
  Option 2: Install locally - https://github.com/microsoftarchive/redis/releases
  Option 3: WSL2 - wsl sudo service redis-server start
#>

param(
    [string]$WorkerName = "worker1",
    [int]$Concurrency = 4,
    [ValidateSet("DEBUG", "INFO", "WARNING", "ERROR")]
    [string]$LogLevel = "INFO"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Colors for output
$Green = @{ ForegroundColor = "Green" }
$Yellow = @{ ForegroundColor = "Yellow" }
$Red = @{ ForegroundColor = "Red" }

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       Celery Worker - Knowledge Base Auto-Update              ║" -ForegroundColor Cyan
Write-Host "║       (APScheduler + Celery Combined Setup)                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Get current directory
$RootDir = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RootDir "backend"

Write-Host "📁 Root Directory: $RootDir" @Yellow
Write-Host "📁 Backend Directory: $BackendDir" @Yellow

# Check if backend directory exists
if (-not (Test-Path $BackendDir)) {
    Write-Host "❌ Backend directory not found: $BackendDir" @Red
    exit 1
}

# Check Redis connection
Write-Host "`n🔍 Checking Redis connection..." @Yellow

$RedisURL = $env:REDIS_URL -replace '^redis://' -split '/' | Select-Object -First 1
if (-not $RedisURL) {
    $RedisURL = "localhost:6379"
}

$RedisHost, $RedisPort = $RedisURL -split ':'
if (-not $RedisPort) { $RedisPort = "6379" }

Write-Host "   Redis URL: redis://$RedisHost:$RedisPort"

try {
    $RedisCheck = Test-NetConnection -ComputerName $RedisHost -Port $RedisPort -WarningAction SilentlyContinue
    if ($RedisCheck.TcpTestSucceeded) {
        Write-Host "   ✅ Redis is accessible" @Green
    } else {
        Write-Host "   ❌ Redis not accessible at $RedisHost:$RedisPort" @Red
        Write-Host "`n   💡 Start Redis:" @Yellow
        Write-Host "      Option 1: Docker:  docker run -d -p 6379:6379 redis:latest"
        Write-Host "      Option 2: Windows: https://github.com/microsoftarchive/redis/releases"
        Write-Host "      Option 3: WSL2:    wsl sudo service redis-server start"
        Write-Host "      Option 4: Custom:  set REDIS_URL=redis://custom-host:6379`n"
        exit 1
    }
} catch {
    Write-Host "   ⚠️  Could not verify Redis (will continue): $_" @Yellow
}

# Navigate to backend
Push-Location $BackendDir

try {
    # Check Python
    Write-Host "`n🐍 Checking Python..." @Yellow
    $PythonCheck = python --version 2>&1
    Write-Host "   $PythonCheck" @Green

    # Check if virtual environment exists and use it
    $VenvPath = Join-Path $BackendDir "venv"
    if (Test-Path $VenvPath) {
        Write-Host "   ✅ Virtual environment found" @Green
        Write-Host "   Activating venv..." @Yellow
        & "$VenvPath\Scripts\Activate.ps1"
        $env:Path = "$VenvPath\Scripts;$env:Path"
    } else {
        Write-Host "   ⚠️  No venv found - Creating one..." @Yellow
        python -m venv $VenvPath
        & "$VenvPath\Scripts\Activate.ps1"
        $env:Path = "$VenvPath\Scripts;$env:Path"
        Write-Host "   Installing dependencies..." @Yellow
        & "$VenvPath\Scripts\pip.exe" install -r requirements.txt -q
        Write-Host "   ✅ Virtual environment created and dependencies installed" @Green
    }

    # Display configuration
    Write-Host "`n⚙️  Worker Configuration:" @Yellow
    Write-Host "   Worker Name: $WorkerName"
    Write-Host "   Concurrency: $Concurrency"
    Write-Host "   Log Level: $LogLevel"
    Write-Host "   Module: app.celery_config:celery_app"
    Write-Host "   Broker: $(if ($env:REDIS_URL) { $env:REDIS_URL } else { 'redis://localhost:6379/0' })"

    Write-Host "`n🚀 Starting Celery Worker...`n" @Green
    Write-Host "Worker is running. Press Ctrl+C to stop." @Yellow
    Write-Host "📊 Monitor tasks at: http://localhost:5555 (if Flower is running)`n" @Yellow

    # Start Celery worker
    celery -A app.celery_config worker `
        --loglevel=$LogLevel `
        --concurrency=$Concurrency `
        --hostname=$WorkerName@%h `
        --max-tasks-per-child=100 `
        --time-limit=3600 `
        --soft-time-limit=3000 `
        --prefetch-multiplier=1 `
        --without-gossip `
        --without-mingle `
        --without-heartbeat

} catch {
    Write-Host "`n❌ Error: $_" @Red
    exit 1
} finally {
    Pop-Location
}
