#!/usr/bin/env pwsh
<#
.SYNOPSIS
Quick status check for Natpudan AI application

.DESCRIPTION
Checks if backend and frontend are running and accessible
#>

$ErrorActionPreference = 'SilentlyContinue'

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "     Natpudan AI - Application Status Check" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Check Backend
Write-Host "Backend Services:" -ForegroundColor Yellow
Write-Host "─────────────────" -ForegroundColor Gray

$backendPorts = @(8000, 8001)
$backendRunning = $false

foreach ($port in $backendPorts) {
    $isOpen = Test-NetConnection -ComputerName 127.0.0.1 -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($isOpen) {
        Write-Host "  ✅ Port $port : LISTENING" -ForegroundColor Green
        $backendPort = $port
        $backendRunning = $true
        
        # Try health check
        try {
            $health = Invoke-RestMethod -Uri "http://127.0.0.1:$port/health" -TimeoutSec 3
            Write-Host "     Status: $($health.status)" -ForegroundColor Cyan
            if ($health.database) {
                Write-Host "     Database: $($health.database)" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "     Status: Initializing..." -ForegroundColor Yellow
        }
    }
}

if (-not $backendRunning) {
    Write-Host "  ❌ Backend not running" -ForegroundColor Red
    Write-Host "     Start with: .\start-backend.ps1" -ForegroundColor Gray
}

# Check Frontend
Write-Host "`nFrontend Service:" -ForegroundColor Yellow
Write-Host "─────────────────" -ForegroundColor Gray

$frontendPort = 5173
$isFrontendOpen = Test-NetConnection -ComputerName 127.0.0.1 -Port $frontendPort -InformationLevel Quiet -WarningAction SilentlyContinue

if ($isFrontendOpen) {
    Write-Host "  ✅ Port $frontendPort : RUNNING" -ForegroundColor Green
    
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$frontendPort" -TimeoutSec 3
        if ($response.StatusCode -eq 200) {
            Write-Host "     Status: Ready" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "     Status: Starting..." -ForegroundColor Yellow
    }
} else {
    Write-Host "  ❌ Frontend not running" -ForegroundColor Red
    Write-Host "     Start with: cd frontend; npm run dev" -ForegroundColor Gray
}

# Access URLs
Write-Host "`nAccess Points:" -ForegroundColor Yellow
Write-Host "─────────────────" -ForegroundColor Gray

if ($backendRunning) {
    Write-Host "  Frontend:     http://127.0.0.1:5173" -ForegroundColor Cyan
    Write-Host "  Backend API:  http://127.0.0.1:$backendPort" -ForegroundColor Cyan
    Write-Host "  API Docs:     http://127.0.0.1:$backendPort/docs" -ForegroundColor Cyan
    Write-Host "  Health:       http://127.0.0.1:$backendPort/health" -ForegroundColor Cyan
}

# Database Check
Write-Host "`nDatabase:" -ForegroundColor Yellow
Write-Host "─────────────────" -ForegroundColor Gray

$dbPath = "backend\natpudan.db"
if (Test-Path $dbPath) {
    $dbSize = (Get-Item $dbPath).Length / 1KB
    Write-Host "  ✅ SQLite: Found (${dbSize:N0} KB)" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Database not found (will be created on first run)" -ForegroundColor Yellow
}

# Quick Actions
Write-Host "`nQuick Actions:" -ForegroundColor Yellow
Write-Host "─────────────────" -ForegroundColor Gray
Write-Host "  Start All:      .\start-dev.ps1" -ForegroundColor Gray
Write-Host "  Start Backend:  .\start-backend.ps1" -ForegroundColor Gray
Write-Host "  Start Frontend: cd frontend; npm run dev" -ForegroundColor Gray
Write-Host "  View Logs:      Get-Job | Receive-Job" -ForegroundColor Gray
Write-Host "  Stop All:       Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor Gray

Write-Host "`n" -NoNewline
Write-Host "============================================================" -ForegroundColor Cyan
$timestamp = Get-Date -Format "HH:mm:ss"
Write-Host "Status check completed at $timestamp" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
