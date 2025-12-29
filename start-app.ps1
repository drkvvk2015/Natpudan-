<#
.SYNOPSIS
Start Natpudan AI using Podman (Production/Containerized Mode)
.DESCRIPTION
This script manages the full lifecycle of the Podman-based deployment.
It handles checking prerequisites, cleaning up errors, setting up networks,
and starting services via Podman Compose.
.PARAMETER Clear
If set, cleans up all existing containers and volumes before starting (Fixes errors).
.PARAMETER Build
If set, rebuilds the container images.
.EXAMPLE
.\start-app.ps1 -Clear
.EXAMPLE
.\start-app.ps1 -Build
#>

param(
    [switch]$Clear,
    [switch]$Build,
    [switch]$Native  # Runs locally without containers (fallback)
)

$ErrorActionPreference = "Stop"

$global:RootDir = "D:\Users\CNSHO\Documents\GitHub\Natpudan-"
$global:BackendDir = Join-Path $global:RootDir "backend"
$global:FrontendDir = Join-Path $global:RootDir "frontend"
$global:VenvPython = Join-Path $global:RootDir ".venv\Scripts\python.exe"

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    $colors = @{ "Success"="Green"; "Error"="Red"; "Warning"="Yellow"; "Info"="Cyan" }
    Write-Host $Message -ForegroundColor $colors[$Type]
}

Clear-Host
Write-Status "========================================" "Info"
Write-Status "   Natpudan AI - Podman Controller" "Info"
Write-Status "========================================" "Info"

# Handle Native Fallback
if ($Native) {
    Write-Status "Running in NATIVE mode (Local installation)..." "Warning"
    
    # Check Python Venv
    if (-not (Test-Path $global:VenvPython)) {
        Write-Status "Virtual environment not found at $($global:VenvPython). Please run .\recreate-venv-fixed.ps1" "Error"
        exit 1
    }

    Write-Status "Starting Backend..." "Info"
    $backendJob = Start-Job -ScriptBlock {
        param($dir, $python)
        Set-Location $dir
        & $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    } -ArgumentList $global:BackendDir, $global:VenvPython

    Write-Status "Starting Frontend..." "Info"
    $frontendJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        npm run dev -- --port 5173
    } -ArgumentList $global:FrontendDir

    Write-Status "Native services started (Jobs: $($backendJob.Id), $($frontendJob.Id))" "Success"
    Write-Host "Wait for services to initialize..."
    Start-Sleep -Seconds 10
    Read-Host "Press Enter to stop services..."
    Get-Job | Stop-Job
    exit 0
}

# 1. Check Podman
if (-not (Get-Command podman -ErrorAction SilentlyContinue)) {
    Write-Status "Podman not found in PATH." "Error"
    Write-Host "Please install Podman Desktop: https://podman.io/docs/installation/windows"
    exit 1
}
Write-Status "[OK] Podman detected" "Success"

# 2. Check Podman Machine (Windows specific)
try {
    $machineJson = podman machine list --format=json | ConvertFrom-Json
    $runningMachine = $machineJson | Where-Object { $_.IsRunning -eq $true }
    if (-not $runningMachine) {
        Write-Status "Starting Podman Machine..." "Warning"
        podman machine start
        Start-Sleep -Seconds 5
    }
    Write-Status "[OK] Podman Machine running" "Success"
} catch {
    Write-Status "Could not check Podman Machine (ignoring if on Linux)..." "Warning"
}

# 3. Clear Errors / Cleanup (Requested by User)
if ($Clear) {
    Write-Status "Clearing all errors and previous sessions..." "Warning"
    try {
        podman-compose down 2>$null
        podman system prune -f 2>$null
        Write-Status "[OK] System cleaned" "Success"
    } catch {
        Write-Status "Cleanup minor warning: $_" "Warning"
    }
}

# 4. Check/Create .env
if (-not (Test-Path ".env")) {
    Write-Status "Creating .env configuration..." "Warning"
    $envContent = @"
ENVIRONMENT=production
DEBUG=False
POSTGRES_USER=physician_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=physician_ai
# OpenAI API Key - PLEASE UPDATE
OPENAI_API_KEY=sk-placeholder
# Redis Configuration (Container-friendly)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
# Ollama Configuration (Pointing to Host)
OLLAMA_HOST=http://host.containers.internal:11434
"@
    Set-Content -Path ".env" -Value $envContent
    Write-Status "[OK] .env created" "Success"
}

# 5. Start Services
Write-Status "Starting Services (Redis, DB, Backend, Frontend)..." "Info"

# Capture host proxy settings to pass to build (Filtered for garbage)
$buildArgs = ""
$garbage = @("", "...", "placeholder")
if ($garbage -notcontains $env:HTTP_PROXY) { $buildArgs += " --build-arg HTTP_PROXY=$env:HTTP_PROXY" }
if ($garbage -notcontains $env:HTTPS_PROXY) { $buildArgs += " --build-arg HTTPS_PROXY=$env:HTTPS_PROXY" }
if ($garbage -notcontains $env:http_proxy) { $buildArgs += " --build-arg http_proxy=$env:http_proxy" }
if ($garbage -notcontains $env:https_proxy) { $buildArgs += " --build-arg https_proxy=$env:https_proxy" }

$composeArgs = "up -d"
if ($Build) { 
    Write-Status "Building with proxy support..." "Info"
    $composeArgs = "build $buildArgs; podman-compose up -d"
}

try {
    # Ensure podman-compose is available
    if (-not (Get-Command podman-compose -ErrorAction SilentlyContinue)) {
        throw "podman-compose not found. Run 'pip install podman-compose' or ensure it's in PATH."
    }

    if ($Build) {
        # Run build separately to ensure args are passed
        Invoke-Expression "podman-compose build $buildArgs"
        podman-compose up -d
    } else {
        podman-compose up -d
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "[OK] Services started successfully" "Success"
    } else {
        throw "podman-compose exited with code $LASTEXITCODE"
    }
} catch {
    Write-Status "Failed to start services: $_" "Error"
    exit 1
}

# 6. Verification
Write-Status "`nVerifying services..." "Info"
Start-Sleep -Seconds 5

# Check Backend
$backendHealth = podman inspect -f '{{.State.Health.Status}}' physician-ai-backend 2>$null
if ($backendHealth -eq "healthy") {
    Write-Status "[OK] Backend is HEALTHY" "Success"
} else {
    Write-Status "[!] Backend status: $backendHealth" "Warning"
}

# Check Redis
if ((podman exec physician-ai-redis redis-cli ping) -eq "PONG") {
    Write-Status "[OK] Redis is ONLINE and RESPONDING" "Success"
} else {
    Write-Status "[!] Redis is not responding" "Error"
}

Write-Status "`n========================================" "Info"
Write-Status "   Natpudan AI - Deployment Ready" "Success"
Write-Status "========================================" "Info"
Write-Host "Services are running at:"
Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  - Backend API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`nTo access container shell (SSH):"
Write-Host "  .\connect-ssh.ps1 -Container backend" -ForegroundColor Yellow
Write-Host "  .\connect-ssh.ps1 -Container redis" -ForegroundColor Yellow
Write-Host "  Flower:   http://localhost:5555"
Write-Host "`nTo stop: podman-compose down" -ForegroundColor Gray
