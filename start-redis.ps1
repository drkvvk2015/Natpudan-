# Start Redis Docker Container for Celery Broker
# Required for APScheduler + Celery integration

param(
    [int]$Port = 6379
)

$ContainerName = "redis-natpudan"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Redis Startup Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Docker is installed
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "[OK] Docker installed: $dockerVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Docker not found. Please install Docker Desktop." -ForegroundColor Red
    Write-Host "`n[INFO] Installation options:" -ForegroundColor Yellow
    Write-Host "  1. Official: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    Write-Host "  2. Chocolatey (Admin): choco install docker-desktop" -ForegroundColor Cyan
    Write-Host "  3. Windows Package Manager (Admin): winget install Docker.DockerDesktop" -ForegroundColor Cyan
    Write-Host "`nAfter installing, restart your terminal and try again.`n" -ForegroundColor Gray
    exit 1
}

# Check if container already running
$running = docker ps --filter "name=$ContainerName" --format "{{.Names}}" 2>$null

if ($running -eq $ContainerName) {
    Write-Host "[OK] Redis already running" -ForegroundColor Green
    Write-Host "     Container: $ContainerName" -ForegroundColor Yellow
    Write-Host "     Port: $Port" -ForegroundColor Yellow
    Write-Host "     URL: redis://localhost:$Port`n" -ForegroundColor Yellow
    exit 0
}

# Start container
Write-Host "[INFO] Starting Redis container..." -ForegroundColor Yellow
try {
    docker run -d `
        --name $ContainerName `
        -p ${Port}:6379 `
        -v redis-data:/data `
        --restart unless-stopped `
        redis:latest 2>&1 | Out-Null
    
    Start-Sleep -Seconds 2
    
    $check = docker ps --filter "name=$ContainerName" --format "{{.Names}}" 2>$null
    
    if ($check -eq $ContainerName) {
        Write-Host "[OK] Redis started successfully" -ForegroundColor Green
        Write-Host "     Container: $ContainerName" -ForegroundColor Yellow
        Write-Host "     Port: $Port" -ForegroundColor Yellow
        Write-Host "     URL: redis://localhost:$Port" -ForegroundColor Yellow
        Write-Host "`nTo stop: docker stop $ContainerName`n" -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] Failed to start Redis" -ForegroundColor Red
        docker logs $ContainerName 2>&1
        exit 1
    }
} catch {
    Write-Host "[ERROR] $_" -ForegroundColor Red
    exit 1
}
