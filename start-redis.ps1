# Start Redis Podman/Docker Container for Celery Broker
# Required for APScheduler + Celery integration

param(
    [int]$Port = 6379
)

$ContainerName = "physician-ai-redis"
$Image = "mirror.gcr.io/library/redis:alpine"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Redis Startup Script (Podman)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check for Podman first
$engine = "podman"
if (-not (Get-Command podman -ErrorAction SilentlyContinue)) {
    $engine = "docker"
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] Neither Podman nor Docker found." -ForegroundColor Red
        exit 1
    }
}

Write-Host "[OK] Using container engine: $engine" -ForegroundColor Green

# Check if container already running
$running = & $engine ps --filter "name=$ContainerName" --format "{{.Names}}" 2>$null
if ($running -match $ContainerName) {
    Write-Host "[OK] Redis already running" -ForegroundColor Green
    Write-Host "     Container: $ContainerName" -ForegroundColor Yellow
    Write-Host "     Port: $Port" -ForegroundColor Yellow
    exit 0
}

# Remove existing stopped container
& $engine rm -f $ContainerName 2>$null | Out-Null

# Start container
Write-Host "[INFO] Starting Redis container..." -ForegroundColor Yellow
try {
    & $engine run -d `
        --name $ContainerName `
        -p ${Port}:6379 `
        $Image redis-server --requirepass redis_password --maxmemory 512mb --maxmemory-policy allkeys-lru --appendonly yes | Out-Null
    
    Start-Sleep -Seconds 2
    
    $check = & $engine ps --filter "name=$ContainerName" --format "{{.Names}}" 2>$null
    if ($check -match $ContainerName) {
        Write-Host "[OK] Redis started successfully" -ForegroundColor Green
        Write-Host "     Container: $ContainerName" -ForegroundColor Yellow
        Write-Host "     Port: $Port" -ForegroundColor Yellow
        Write-Host "     URL: redis://:redis_password@localhost:$Port" -ForegroundColor Yellow
    } else {
        Write-Host "[ERROR] Failed to start Redis" -ForegroundColor Red
        & $engine logs $ContainerName
        exit 1
    }
} catch {
    Write-Host "[ERROR] $_" -ForegroundColor Red
    exit 1
}
