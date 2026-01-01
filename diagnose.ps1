# Quick Diagnostic Script for Natpudan AI Debug Setup
# Run this to check the health of all services

param(
    [switch]$Fix = $false,    # Auto-fix issues where possible
    [switch]$Verbose = $false  # Show detailed output
)

# ============================================================================
# CONFIGURATION
# ============================================================================
$global:RootDir = $PSScriptRoot
$global:BackendDir = Join-Path $global:RootDir "backend"

# Colors
$Colors = @{
    "Success"  = "Green"
    "Error"    = "Red"
    "Warning"  = "Yellow"
    "Info"     = "Cyan"
    "Debug"    = "Magenta"
}

# ============================================================================
# FUNCTIONS
# ============================================================================

function Write-Status {
    param([string]$Message, [string]$Type = "Info", [string]$Icon = "")
    if ($Icon) {
        Write-Host "[$Icon] $Message" -ForegroundColor $Colors[$Type]
    } else {
        Write-Host "$Message" -ForegroundColor $Colors[$Type]
    }
}

function Test-Port {
    param([int]$Port)
    $tcp = New-Object System.Net.Sockets.TcpClient
    try {
        $tcp.Connect("127.0.0.1", $Port)
        $tcp.Close()
        return $true
    } catch {
        return $false
    } finally {
        if ($tcp) { $tcp.Dispose() }
    }
}

function Test-Service {
    param([string]$Name, [int]$Port, [string]$Url)
    
    Write-Host "`n[ $Name ]" -ForegroundColor Cyan
    
    # Test port
    if (Test-Port -Port $Port) {
        Write-Status "Port ${Port}: OPEN" "Success" "OK"
        
        # Test HTTP endpoint if URL provided
        if ($Url) {
            try {
                $response = Invoke-WebRequest -Uri $Url -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
                Write-Status "HTTP Status: $($response.StatusCode) OK" "Success" "OK"
            } catch {
                Write-Status "HTTP Request Failed: $($_.Exception.Message)" "Error" "ERR"
            }
        }
    } else {
        Write-Status "Port ${Port}: CLOSED (Service not running)" "Error" "ERR"
    }
}

function Check-Docker {
    Write-Host "`n[ DOCKER & CONTAINERS ]" -ForegroundColor Cyan
    
    # Check Docker installation
    $dockerVersion = try { docker --version 2>$null } catch { $null }
    if ($dockerVersion) {
        Write-Status "$dockerVersion" "Success" "OK"
    } else {
        Write-Status "Docker not found or not in PATH" "Error" "ERR"
        return $false
    }
    
    # Check Docker daemon
    try {
        docker ps >$null 2>&1
        Write-Status "Docker daemon running" "Success" "OK"
    } catch {
        Write-Status "Docker daemon not responding" "Error" "ERR"
        return $false
    }
    
    # List running containers
    Write-Host "`nRunning Containers:" -ForegroundColor Yellow
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    if ($containers -and ($containers.Count -gt 1)) {
        $containers | ForEach-Object {
            if ($_ -match "physician-ai") {
                Write-Host "  $_" -ForegroundColor Green
            } else {
                Write-Host "  $_" -ForegroundColor Gray
            }
        }
    } else {
        Write-Status "  No containers running" "Warning" "WARN"
    }
    
    return $true
}

function Check-Python {
    Write-Host "`n[ PYTHON ENVIRONMENT ]" -ForegroundColor Cyan
    
    # Check Python
    $pythonVersion = try { python --version 2>&1 } catch { $null }
    if ($pythonVersion) {
        Write-Status "$pythonVersion" "Success" "OK"
    } else {
        Write-Status "Python not found" "Error" "ERR"
        return $false
    }
    
    # Check virtual environment
    $venvPath = Join-Path $global:BackendDir ".venv"
    if (-not (Test-Path $venvPath)) {
        $venvPath = Join-Path $global:BackendDir "venv"
    }

    if (Test-Path $venvPath) {
        Write-Status "Virtual environment found at $venvPath" "Success" "OK"
        
        # Check if activated
        if ($env:VIRTUAL_ENV) {
            Write-Status "Virtual environment is ACTIVE" "Success" "OK"
        } else {
            Write-Status "Virtual environment not active" "Warning" "WARN"
        }
    } else {
        Write-Status "Virtual environment not found" "Error" "ERR"
        return $false
    }
    
    return $true
}

function Check-Database {
    Write-Host "`n[ DATABASE ]" -ForegroundColor Cyan
    
    if (Test-Path (Join-Path $global:BackendDir "natpudan.db")) {
        Write-Status "SQLite Database: natpudan.db exists" "Success" "OK"
    } else {
        Write-Status "SQLite Database: natpudan.db MISSING" "Warning" "WARN"
    }

    if (Test-Path (Join-Path $global:BackendDir "physician_ai.db")) {
        Write-Status "SQLite Database: physician_ai.db exists" "Success" "OK"
    }
}

function Check-Backend {
    Write-Host "`n[ FASTAPI BACKEND ]" -ForegroundColor Cyan
    
    # Try to get port from config
    $BackendPort = 8000
    $ConfigPath = Join-Path $global:RootDir "config/ports.json"
    if (Test-Path $ConfigPath) {
        try {
            $cfg = Get-Content $ConfigPath -Raw | ConvertFrom-Json
            if ($cfg.services.backend.dev) { $BackendPort = [int]$cfg.services.backend.dev }
        } catch {}
    }

    if (Test-Port -Port $BackendPort) {
        Write-Status "Backend: RUNNING on port ${BackendPort}" "Success" "OK"
        
        # Test health
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:${BackendPort}/health" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
            Write-Status "Health Check: $($response.StatusCode)" "Success" "OK"
        } catch {
            Write-Status "Health Check: FAILED" "Error" "ERR"
        }
    } else {
        Write-Status "Backend: NOT RUNNING on port ${BackendPort}" "Error" "ERR"
    }
}

function Check-Frontend {
    Write-Host "`n[ REACT FRONTEND ]" -ForegroundColor Cyan
    
    if (Test-Port -Port 5173) {
        Write-Status "Frontend Dev Server: RUNNING on port 5173" "Success" "OK"
    } else {
        Write-Status "Frontend Dev Server: NOT RUNNING on port 5173" "Warning" "WARN"
    }
}

function Show-Summary {
    Write-Host "`n[ DIAGNOSTICS SUMMARY ]" -ForegroundColor Cyan
    
    # Try to get port from config
    $BackendPort = 8000
    $ConfigPath = Join-Path $global:RootDir "config/ports.json"
    if (Test-Path $ConfigPath) {
        try {
            $cfg = Get-Content $ConfigPath -Raw | ConvertFrom-Json
            if ($cfg.services.backend.dev) { $BackendPort = [int]$cfg.services.backend.dev }
        } catch {}
    }

    $services = @(
        @{Name="Backend"; Port=$BackendPort},
        @{Name="Frontend"; Port=5173},
        @{Name="Redis"; Port=6379}
    )
    
    foreach ($service in $services) {
        if (Test-Port -Port $service.Port) {
            Write-Status "$($service.Name): RUNNING" "Success" "OK"
        } else {
            Write-Status "$($service.Name): NOT RUNNING" "Warning" "FAIL"
        }
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Host "`nNATPUDAN AI - DIAGNOSTIC REPORT`n" -ForegroundColor Green

# Run all checks
Check-Docker
Check-Python
Check-Database
Check-Backend
Check-Frontend

# Show summary
Show-Summary

Write-Host "`n"
