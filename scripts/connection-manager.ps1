#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Connection Manager - Quick Status Check
.DESCRIPTION
    Validates service connectivity and configuration
#>

param(
    [switch]$Detailed
)

$ConfigFile = Join-Path $PSScriptRoot "..\config\ports.json"

Write-Host "`n==========================================="  -ForegroundColor Cyan
Write-Host "    Natpudan Connection Manager" -ForegroundColor White
Write-Host "===========================================`n" -ForegroundColor Cyan

# Load configuration
if (-not (Test-Path $ConfigFile)) {
    Write-Host "[ERROR] Config file not found: $ConfigFile" -ForegroundColor Red
    exit 1
}

$config = Get-Content $ConfigFile | ConvertFrom-Json
$backendPort = $config.services.backend.dev
$frontendPort = $config.services.frontend.dev
$backendUrl = $config.urls.backend.dev

function Test-PortListening {
    param([int]$Port)
    $connections = netstat -ano | Select-String ":$Port.*LISTENING"
    return $connections.Count -gt 0
}

function Test-HttpEndpoint {
    param([string]$Url)
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        return @{ Success = $true; StatusCode = $response.StatusCode; Content = $response.Content }
    } catch {
        return @{ Success = $false }
    }
}

# Check Backend
Write-Host "--- Backend Service ---" -ForegroundColor Cyan
Write-Host "  Port: $backendPort" -ForegroundColor White

$backendListening = Test-PortListening -Port $backendPort
$healthCheck = @{ Success = $false }

if ($backendListening) {
    Write-Host "  Listening: YES" -ForegroundColor Green
    $healthCheck = Test-HttpEndpoint -Url "$backendUrl/health"
    if ($healthCheck.Success) {
        Write-Host "  Health: HEALTHY" -ForegroundColor Green
        if ($Detailed) {
            $health = $healthCheck.Content | ConvertFrom-Json
            Write-Host "    Database: $($health.services.database)" -ForegroundColor Gray
            Write-Host "    OpenAI: $($health.services.openai)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  Health: UNREACHABLE" -ForegroundColor Red
    }
} else {
    Write-Host "  Listening: NO" -ForegroundColor Red
    Write-Host "  Health: OFFLINE" -ForegroundColor Red
}

# Check Frontend
Write-Host "`n--- Frontend Service ---" -ForegroundColor Cyan
Write-Host "  Port: $frontendPort" -ForegroundColor White

$frontendListening = Test-PortListening -Port $frontendPort
if ($frontendListening) {
    Write-Host "  Listening: YES" -ForegroundColor Green
    $frontendCheck = Test-HttpEndpoint -Url "http://localhost:$frontendPort"
    if ($frontendCheck.Success) {
        Write-Host "  Accessible: YES" -ForegroundColor Green
    } else {
        Write-Host "  Accessible: SLOW/TIMEOUT" -ForegroundColor Yellow
    }
} else {
    Write-Host "  Listening: NO" -ForegroundColor Red
    Write-Host "  Accessible: OFFLINE" -ForegroundColor Red
}

# Check Configuration
Write-Host "`n--- Configuration Status ---" -ForegroundColor Cyan

$frontendEnv = Join-Path $PSScriptRoot "..\frontend\.env.development"
$configMatch = $false
if (Test-Path $frontendEnv) {
    $envContent = Get-Content $frontendEnv -Raw
    if ($envContent -match "VITE_API_BASE_URL=(.*)") {
        $configuredUrl = $matches[1].Trim()
        if ($configuredUrl -eq $backendUrl) {
            Write-Host "  Config Match: YES" -ForegroundColor Green
            Write-Host "    Frontend -> Backend: $backendUrl" -ForegroundColor Gray
            $configMatch = $true
        } else {
            Write-Host "  Config Match: MISMATCH!" -ForegroundColor Red
            Write-Host "    Expected: $backendUrl" -ForegroundColor Yellow
            Write-Host "    Configured: $configuredUrl" -ForegroundColor Red
            Write-Host "`n  [FIX] Run: .\scripts\check-ports.ps1 -Fix" -ForegroundColor Yellow
        }
    }
}

# Summary
Write-Host "`n===========================================`n" -ForegroundColor Cyan

$allGood = $healthCheck.Success -and $frontendListening -and $configMatch

if ($allGood) {
    Write-Host "[SUCCESS] ALL SYSTEMS GO!" -ForegroundColor Green
    Write-Host "`n  Login URL: http://localhost:$frontendPort" -ForegroundColor Cyan
    Write-Host "  Backend API: $backendUrl" -ForegroundColor Cyan
    Write-Host "  Credentials: admin@admin.com / admin123`n" -ForegroundColor Gray
    exit 0
} else {
    Write-Host "[WARNING] ISSUES DETECTED`n" -ForegroundColor Yellow
    
    if (-not $backendListening) {
        Write-Host "  1. Start backend: .\start-backend.ps1" -ForegroundColor Yellow
    }
    if (-not $frontendListening) {
        Write-Host "  2. Start frontend: cd frontend; npm run dev" -ForegroundColor Yellow
    }
    if (-not $configMatch) {
        Write-Host "  3. Fix config: .\scripts\check-ports.ps1 -Fix" -ForegroundColor Yellow
    }
    
    Write-Host ""
    exit 1
}
