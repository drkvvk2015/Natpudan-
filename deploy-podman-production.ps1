<#
.SYNOPSIS
Deploy Natpudan AI in production using Podman
.DESCRIPTION
Deploys all services using Podman Compose with production settings
Prerequisites: Podman, podman-compose, valid .env file with secrets
.PARAMETER EnvFile
Path to environment file (default: .env)
.PARAMETER Recreate
Force recreation of containers
.PARAMETER Pull
Pull latest images before deployment
.EXAMPLE
.\deploy-podman-production.ps1
.\deploy-podman-production.ps1 -EnvFile .env.prod -Pull
.\deploy-podman-production.ps1 -Recreate
#>

Param(
    [string]$EnvFile = ".env",
    [switch]$Recreate,
    [switch]$Pull
)

$ErrorActionPreference = "Stop"

# ============================================
# Helper Functions
# ============================================

function Get-PodmanCmd {
    $cmd = (Get-Command podman -ErrorAction SilentlyContinue).Path
    if ($cmd) { return $cmd }
    throw "Podman not found. Please install Podman: https://podman.io/docs/installation/windows"
}

function Get-PodmanComposeCmd {
    $cmd = (Get-Command podman-compose -ErrorAction SilentlyContinue).Path
    if ($cmd) { return $cmd }
    throw "podman-compose not found. Install with: pip install podman-compose"
}

function Test-Connectivity {
    param(
        [string]$Service,
        [int]$Port,
        [int]$MaxRetries = 30
    )
    
    $retries = 0
    while ($retries -lt $MaxRetries) {
        try {
            $connection = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port -ErrorAction SilentlyContinue
            if ($connection.TcpTestSucceeded) {
                return $true
            }
        } catch { }
        
        $retries++
        Start-Sleep -Seconds 2
    }
    
    return $false
}

# ============================================
# Main Deployment
# ============================================

Write-Host "[Deploy] Starting Podman production deployment..." -ForegroundColor Cyan
Write-Host "[Deploy] Environment: $EnvFile`n" -ForegroundColor Cyan

# Validate environment file
if (-not (Test-Path $EnvFile)) {
    Write-Error "Environment file '$EnvFile' not found. Create it based on .env.sample"
    exit 1
}

Write-Host "[Deploy] [OK] Environment file found: $EnvFile" -ForegroundColor Green

# Get Podman commands
$PodmanCmd = Get-PodmanCmd
$PodmanComposeCmd = Get-PodmanComposeCmd

Write-Host "[Deploy] [OK] Podman: $PodmanCmd" -ForegroundColor Green
Write-Host "[Deploy] [OK] Podman Compose: $PodmanComposeCmd" -ForegroundColor Green

# Ensure Podman machine is running
Write-Host "`n[Deploy] Checking Podman Machine..." -ForegroundColor Cyan
try {
    $machineStatus = podman machine list --format=json | ConvertFrom-Json
    $isRunning = $machineStatus | Where-Object { $_.IsRunning -eq $true }
    
    if (-not $isRunning) {
        Write-Host "[Deploy] Starting Podman Machine..." -ForegroundColor Yellow
        podman machine start
        Start-Sleep -Seconds 5
    }
    
    Write-Host "[Deploy] [OK] Podman Machine is running" -ForegroundColor Green
} catch {
    Write-Warning "[Deploy] Could not verify Podman Machine status: $_"
}

# Pull latest images if requested
if ($Pull) {
    Write-Host "`n[Deploy] Pulling latest images..." -ForegroundColor Cyan
    & $PodmanComposeCmd --env-file $EnvFile pull
    if ($LASTEXITCODE -ne 0) { 
        throw "podman-compose pull failed (exit code $LASTEXITCODE)" 
    }
    Write-Host "[Deploy] [OK] Images pulled successfully" -ForegroundColor Green
}

# Stop existing containers (non-critical, ignore errors if none exist)
Write-Host "`n[Deploy] Stopping existing containers..." -ForegroundColor Cyan
try {
    & $PodmanComposeCmd --env-file $EnvFile down --remove-orphans 2>&1 | Out-Null
} catch {
    Write-Host "[Deploy] [INFO] No existing containers to stop (first run)" -ForegroundColor Gray
}
Write-Host "[Deploy] [OK] Containers stopped" -ForegroundColor Green

# Build images
Write-Host "`n[Deploy] Building container images..." -ForegroundColor Cyan
$buildArgs = @("--env-file", $EnvFile, "build")
if ($Recreate) {
    $buildArgs += "--no-cache"
}
& $PodmanComposeCmd $buildArgs
if ($LASTEXITCODE -ne 0) { 
    throw "podman-compose build failed (exit code $LASTEXITCODE)" 
}
Write-Host "[Deploy] [OK] Images built successfully" -ForegroundColor Green

# Start services
Write-Host "`n[Deploy] Starting services..." -ForegroundColor Cyan
$upArgs = @("--env-file", $EnvFile, "up", "-d")
if ($Recreate) {
    $upArgs += "--force-recreate"
}
& $PodmanComposeCmd $upArgs
if ($LASTEXITCODE -ne 0) { 
    throw "podman-compose up failed (exit code $LASTEXITCODE)" 
}
Write-Host "[Deploy] [OK] Services started" -ForegroundColor Green

# Wait for services to be ready
Write-Host "`n[Deploy] Waiting for services to be ready..." -ForegroundColor Cyan

$services = @{
    "PostgreSQL" = 5432
    "Redis" = 6379
    "Backend" = 8000
}

foreach ($service in $services.GetEnumerator()) {
    Write-Host "[Deploy] Waiting for $($service.Key) (port $($service.Value))..." -ForegroundColor Gray
    
    if (Test-Connectivity -Service $service.Key -Port $service.Value) {
        Write-Host "[Deploy] [OK] $($service.Key) is ready" -ForegroundColor Green
    } else {
        Write-Warning "[Deploy] [!] $($service.Key) may not be ready (timeout)"
    }
}

# Show deployment status
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Deployment Successful!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Container Status:" -ForegroundColor Cyan
& $PodmanComposeCmd --env-file $EnvFile ps

Write-Host "`nAccess Points:" -ForegroundColor Cyan
Write-Host "  Backend API:        http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "  Frontend:           http://127.0.0.1:3000" -ForegroundColor Yellow
Write-Host "  PostgreSQL:         127.0.0.1:5432" -ForegroundColor Yellow
Write-Host "  Redis:              127.0.0.1:6379" -ForegroundColor Yellow
Write-Host "  Flower (Tasks):     http://127.0.0.1:5555" -ForegroundColor Yellow

Write-Host "`nManagement Commands:" -ForegroundColor Cyan
Write-Host "  View logs:          podman-compose --env-file $EnvFile logs -f [service]" -ForegroundColor Gray
Write-Host "  Stop services:      podman-compose --env-file $EnvFile down" -ForegroundColor Gray
Write-Host "  Health check:       podman-compose --env-file $EnvFile ps" -ForegroundColor Gray
Write-Host "  Execute command:    podman-compose --env-file $EnvFile exec backend [cmd]" -ForegroundColor Gray

Write-Host "`n[Deploy] Production deployment complete!" -ForegroundColor Green
Write-Host ""
