# ============================================================================
# Natpudan AI - DEBUG SETUP (NO DOCKER)
# ============================================================================
# Starts only local services without Docker:
#   - FastAPI Backend (Port 8000) with SQLite
#   - React Frontend (Port 5173)
#   - Celery Worker (background tasks)
# ============================================================================

param(
    [switch]$NoFrontend,     # Skip frontend startup
    [switch]$Help            # Show help
)

$ErrorActionPreference = "Continue"
$global:RootDir = "D:\Users\CNSHO\Documents\GitHub\Natpudan-"
$global:BackendDir = Join-Path $global:RootDir "backend"
$global:FrontendDir = Join-Path $global:RootDir "frontend"
$global:VenvPath = Join-Path $global:BackendDir "venv"

$global:BackendUrl = "http://127.0.0.1:8000"
$global:FrontendUrl = "http://127.0.0.1:5173"

$Colors = @{
    "Success"  = "Green"
    "Error"    = "Red"
    "Warning"  = "Yellow"
    "Info"     = "Cyan"
}

function Write-Section {
    param([string]$Title, [string]$Type = "Info")
    Write-Host "`n$("=" * 80)" -ForegroundColor $Colors[$Type]
    Write-Host "  $Title" -ForegroundColor $Colors[$Type]
    Write-Host ("=" * 80) -ForegroundColor $Colors[$Type]
}

function Write-Status {
    param([string]$Message, [string]$Type = "Info", [string]$Icon = "")
    $timestamp = Get-Date -Format "HH:mm:ss"
    if ($Icon) {
        Write-Host "[$timestamp] [$Icon] $Message" -ForegroundColor $Colors[$Type]
    } else {
        Write-Host "[$timestamp] $Message" -ForegroundColor $Colors[$Type]
    }
}

function Test-Python {
    try {
        $version = python --version 2>&1
        if ($version -match "Python") {
            Write-Status "Python found: $version" "Success" "OK"
            return $true
        }
    } catch {
        Write-Status "Python not found" "Error" "ERROR"
        return $false
    }
}

function Setup-Venv {
    if (Test-Path $global:VenvPath) {
        Write-Status "Virtual environment exists" "Info" "OK"
    } else {
        Write-Status "Creating virtual environment..." "Warning" "[WAIT]"
        python -m venv $global:VenvPath
        Write-Status "Virtual environment created" "Success" "OK"
    }
    
    Write-Status "Installing dependencies..." "Info" "[SETUP]"
    & "$global:VenvPath\Scripts\python.exe" -m pip install --upgrade pip -q
    & "$global:VenvPath\Scripts\pip.exe" install -r "$global:BackendDir\requirements.txt" -q
    Write-Status "Dependencies ready" "Success" "OK"
}

function Start-Backend {
    Write-Section "STARTING FASTAPI BACKEND (SQLite)" "Info"
    
    Setup-Venv
    
    Write-Status "Starting backend on port 8000..." "Info" "[STARTUP]"
    
    # Set SQLite database URL
    $env:DATABASE_URL = "sqlite:///./natpudan.db"
    
    $psCommand = '& "' + $global:VenvPath + '\Scripts\Activate.ps1"; cd "' + $global:BackendDir + '"; $env:DATABASE_URL="sqlite:///./natpudan.db"; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload'
    
    Start-Process powershell -ArgumentList @('-NoExit', '-Command', $psCommand)
    
    Write-Status "Backend started" "Success" "OK"
    Write-Status "API: $($global:BackendUrl)" "Info" "[API]"
    Write-Status "Docs: $($global:BackendUrl)/docs" "Info" "[DOCS]"
    Start-Sleep -Seconds 5
}

function Start-Frontend {
    if ($NoFrontend) {
        Write-Status "Frontend skipped" "Info" "[SKIP]"
        return
    }
    
    Write-Section "STARTING REACT FRONTEND" "Info"
    
    Write-Status "Starting Vite dev server..." "Info" "[VITE]"
    
    Push-Location $global:FrontendDir
    try {
        if (-not (Test-Path "node_modules")) {
            Write-Status "Installing npm dependencies..." "Warning" "[WAIT]"
            npm install
        }
        
        $psCommand = 'cd "' + $global:FrontendDir + '"; npm run dev'
        
        Start-Process powershell -ArgumentList @('-NoExit', '-Command', $psCommand)
        
        Write-Status "Frontend started" "Success" "OK"
        Write-Status "URL: $($global:FrontendUrl)" "Info" "[WEB]"
    } finally {
        Pop-Location
    }
}

function Show-Summary {
    Write-Section "SETUP COMPLETE" "Success"
    
    Write-Host @"

SERVICE ENDPOINTS:
==================
  Backend (FastAPI):    $($global:BackendUrl)
  API Documentation:    $($global:BackendUrl)/docs
  Frontend (React):     $($global:FrontendUrl)

DATABASE:
=========
  Using SQLite:         backend/natpudan.db
  (No PostgreSQL needed)

NOTES:
======
  - Backend uses SQLite (no Docker required)
  - Celery/Redis features disabled (no background tasks)
  - To stop: Close the terminal windows
  
  For full features with Docker, run:
    .\start-debug-full.ps1

"@ -ForegroundColor Cyan
}

function Main {
    if ($Help) {
        Write-Host "Natpudan AI - Simple Debug Setup (No Docker)`n"
        Write-Host "USAGE: .\start-debug-no-docker.ps1 [-NoFrontend]`n"
        Write-Host "Starts Backend (SQLite) + Frontend without Docker dependencies"
        return
    }
    
    Write-Section "PRE-FLIGHT CHECKS" "Info"
    
    if (-not (Test-Python)) {
        Write-Status "Python is required!" "Error" "ERROR"
        exit 1
    }
    
    Write-Status "All prerequisites met" "Success" "OK"
    
    Write-Section "NATPUDAN AI - SIMPLE DEBUG SETUP" "Success"
    
    Start-Backend
    Start-Sleep -Seconds 3
    Start-Frontend
    
    Show-Summary
    
    Write-Status "Press Ctrl+C to stop" "Info" "[INFO]"
    while ($true) { Start-Sleep -Seconds 10 }
}

Main
