#!/usr/bin/env pwsh
<#
.SYNOPSIS
Start Celery Flower - Task Monitoring Dashboard

.DESCRIPTION
Starts Flower, a real-time monitoring web interface for Celery.
Provides visibility into background tasks, workers, and execution stats.

.PARAMETER Port
Port for Flower web interface (default: 5555)

.EXAMPLE
.\start-flower.ps1

.\start-flower.ps1 -Port 5555

.NOTES
Access the dashboard at: http://localhost:5555
#>

param(
    [int]$Port = 5555
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Green = @{ ForegroundColor = "Green" }
$Yellow = @{ ForegroundColor = "Yellow" }
$Red = @{ ForegroundColor = "Red" }

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         Celery Flower - Task Monitoring Dashboard             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$RootDir = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RootDir "backend"

if (-not (Test-Path $BackendDir)) {
    Write-Host "❌ Backend directory not found: $BackendDir" @Red
    exit 1
}

Push-Location $BackendDir

try {
    # Check if venv exists
    $VenvPath = Join-Path $BackendDir "venv"
    if (Test-Path $VenvPath) {
        Write-Host "Activating virtual environment..." @Yellow
        & "$VenvPath\Scripts\Activate.ps1"
    }

    Write-Host "`n⚙️  Configuration:" @Yellow
    Write-Host "   Port: $Port"
    Write-Host "   Broker: $(if ($env:REDIS_URL) { $env:REDIS_URL } else { 'redis://localhost:6379/0' })"

    Write-Host "`n🚀 Starting Celery Flower..." @Green
    Write-Host "📊 Open browser: http://localhost:$Port`n" @Yellow

    # Start Flower
    celery -A app.celery_config flower `
        --port=$Port `
        --basic_auth=admin:admin

} catch {
    Write-Host "`n❌ Error: $_" @Red
    exit 1
} finally {
    Pop-Location
}
