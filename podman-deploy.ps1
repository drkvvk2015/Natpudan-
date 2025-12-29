#!/usr/bin/env pwsh
<#
.SYNOPSIS
Quick start script for deploying Natpudan AI in Podman production environment

.DESCRIPTION
This script automates the entire production deployment process:
1. Validates prerequisites (Podman, podman-compose)
2. Loads environment configuration
3. Builds container images
4. Creates volumes and networks
5. Starts all services
6. Validates health checks
7. Displays access information

.PARAMETER EnvFile
Path to environment file (default: .env.prod)

.PARAMETER DeploymentMode
'local' = development on localhost
'staging' = staging environment with Let's Encrypt
'production' = full production deployment

.PARAMETER SkipBuild
Skip building images (use existing ones)

.EXAMPLE
.\podman-deploy.ps1 -EnvFile .env.prod
.\podman-deploy.ps1 -DeploymentMode production -SkipBuild
#>

Param(
    [ValidateSet('local', 'staging', 'production')]
    [string]$DeploymentMode = 'local',
    [string]$EnvFile = '.env.prod',
    [switch]$SkipBuild,
    [switch]$Recreate
)

$ErrorActionPreference = "Stop"
$VerbosePreference = "Continue"

# ============================================
# Color Output
# ============================================
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

# ============================================
# Validation Functions
# ============================================
function Test-PodmanInstalled {
    $podman = Get-Command podman -ErrorAction SilentlyContinue
    if (-not $podman) {
        Write-Error-Custom "Podman not found. Install from: https://podman.io/docs/installation/windows"
        exit 1
    }
    Write-Success "Podman found: $($podman.Source)"
}

function Test-PodmanComposeInstalled {
    $compose = Get-Command podman-compose -ErrorAction SilentlyContinue
    if (-not $compose) {
        Write-Error-Custom "podman-compose not found. Install with: pip install podman-compose"
        exit 1
    }
    Write-Success "podman-compose found"
}

function Test-EnvFileExists {
    param([string]$FilePath)
    if (-not (Test-Path $FilePath)) {
        Write-Error-Custom "Environment file not found: $FilePath"
        Write-Info "Create one from .env.sample or .env.prod"
        exit 1
    }
    Write-Success "Environment file found: $FilePath"
}

function Test-DockerfileExists {
    @('./backend/Dockerfile', './frontend/Dockerfile') | ForEach-Object {
        if (-not (Test-Path $_)) {
            Write-Error-Custom "Dockerfile not found: $_"
            exit 1
        }
    }
    Write-Success "Dockerfiles found"
}

# ============================================
# Deployment Functions
# ============================================
function Build-Images {
    param([string]$EnvFile, [switch]$NoBuild)
    
    if ($NoBuild) {
        Write-Info "Skipping image build (using existing images)"
        return
    }

    Write-Info "Building container images..."
    
    try {
        podman-compose -f docker-compose.yml --env-file $EnvFile build --no-cache
        Write-Success "Images built successfully"
    }
    catch {
        Write-Error-Custom "Failed to build images: $_"
        exit 1
    }
}

function Start-Services {
    param([string]$EnvFile, [switch]$RecreateContainers)

    Write-Info "Starting services..."
    
    $args = @(
        "-f", "docker-compose.yml",
        "--env-file", $EnvFile,
        "up", "-d"
    )
    
    if ($RecreateContainers) {
        $args += @("--force-recreate")
    }
    
    try {
        podman-compose @args
        Write-Success "Services started"
    }
    catch {
        Write-Error-Custom "Failed to start services: $_"
        exit 1
    }
}

function Wait-ForHealthy {
    param([string[]]$Services, [int]$TimeoutSeconds = 300)
    
    Write-Info "Waiting for services to be healthy (timeout: ${TimeoutSeconds}s)..."
    
    $startTime = Get-Date
    $allHealthy = $false
    
    while ((Get-Date) - $startTime -lt [timespan]::FromSeconds($TimeoutSeconds)) {
        $statuses = podman-compose ps --format json 2>$null | ConvertFrom-Json -ErrorAction SilentlyContinue
        
        if ($statuses) {
            $healthy = $statuses | Where-Object { $Services -contains $_.Names -and $_.Status -like "*healthy*" }
            if ($healthy.Count -eq $Services.Count) {
                $allHealthy = $true
                break
            }
        }
        
        Start-Sleep -Seconds 5
    }
    
    if ($allHealthy) {
        Write-Success "All services are healthy"
    } else {
        Write-Warning-Custom "Services did not reach healthy state within timeout"
    }
}

function Get-ServiceStatus {
    Write-Info "Service Status:"
    Write-Host ""
    
    podman-compose ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    Write-Host ""
}

function Display-AccessInfo {
    param([string]$DeploymentMode)
    
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Success "Deployment Complete!"
    Write-Host "=" * 60 -ForegroundColor Green
    
    switch ($DeploymentMode) {
        'local' {
            Write-Info "Access the application:"
            Write-Host "  Frontend:      http://127.0.0.1:3000"
            Write-Host "  Backend API:   http://127.0.0.1:8000"
            Write-Host "  API Docs:      http://127.0.0.1:8000/docs"
            Write-Host "  Flower (Jobs): http://127.0.0.1:5555"
            Write-Host "  Health:        http://127.0.0.1:8000/health"
        }
        'staging' {
            Write-Info "Access the application:"
            Write-Host "  Frontend:      https://staging.yourdomain.com"
            Write-Host "  API Docs:      https://api.staging.yourdomain.com/docs"
            Write-Host "  Flower (Jobs): https://api.staging.yourdomain.com/flower"
        }
        'production' {
            Write-Info "Access the application:"
            Write-Host "  Frontend:      https://yourdomain.com"
            Write-Host "  API Docs:      https://api.yourdomain.com/docs"
            Write-Host "  Flower (Jobs): https://api.yourdomain.com/flower"
        }
    }
    
    Write-Host ""
    Write-Info "Useful commands:"
    Write-Host "  View logs:       podman-compose logs -f backend"
    Write-Host "  Stop services:   podman-compose down"
    Write-Host "  Restart service: podman restart physician-ai-backend"
    Write-Host "  Check health:    curl http://127.0.0.1:8000/health | jq"
    Write-Host ""
    Write-Info "Documentation:"
    Write-Host "  Production Guide: ./PRODUCTION_DEPLOYMENT_PODMAN.md"
    Write-Host "  Troubleshooting:  See 'Troubleshooting' section in guide"
    Write-Host ""
}

function Create-RequiredDirectories {
    Write-Info "Creating required directories..."
    
    @(
        'nginx',
        'nginx/ssl',
        'backend/data',
        'backend/logs',
        'backend/cache',
        'backend/data/flower'
    ) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
            Write-Success "Created directory: $_"
        }
    }
}

# ============================================
# Main Execution
# ============================================
function Main {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  Natpudan AI - Podman Production Deployment       ║" -ForegroundColor Cyan
    Write-Host "║  Deployment Mode: $DeploymentMode$((' ' * (30 - $DeploymentMode.Length)))║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # Step 1: Validation
    Write-Info "Step 1: Validating prerequisites..."
    Test-PodmanInstalled
    Test-PodmanComposeInstalled
    Test-EnvFileExists -FilePath $EnvFile
    Test-DockerfileExists
    Write-Success "All prerequisites met!"
    Write-Host ""
    
    # Step 2: Create directories
    Write-Info "Step 2: Creating required directories..."
    Create-RequiredDirectories
    Write-Host ""
    
    # Step 3: Build images
    Write-Info "Step 3: Building container images..."
    Build-Images -EnvFile $EnvFile -NoBuild:$SkipBuild
    Write-Host ""
    
    # Step 4: Start services
    Write-Info "Step 4: Starting services..."
    Start-Services -EnvFile $EnvFile -RecreateContainers:$Recreate
    Write-Host ""
    
    # Step 5: Wait for health
    Write-Info "Step 5: Waiting for services to be healthy..."
    $services = @("physician-ai-backend", "physician-ai-db", "physician-ai-redis")
    Wait-ForHealthy -Services $services
    Write-Host ""
    
    # Step 6: Display status
    Get-ServiceStatus
    
    # Step 7: Display access info
    Display-AccessInfo -DeploymentMode $DeploymentMode
}

# Run main function
try {
    Main
}
catch {
    Write-Error-Custom "Deployment failed: $_"
    exit 1
}
