# Natpudan AI - Full Stack Startup Script (SQLite Edition)
# Starts all services: Backend, Celery, Flower, Frontend (No Docker needed)

param(
    [switch]$Help,
    [switch]$RecreateDb,
    [switch]$UsePodman
)

if ($Help) {
    Write-Host "`nNatpudan AI - Full Stack Startup Script" -ForegroundColor Cyan
    Write-Host "=========================================`n" -ForegroundColor Cyan
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\start-all.ps1                # Start with local SQLite (development)" -ForegroundColor White
    Write-Host "  .\start-all.ps1 -UsePodman     # Start with Podman containers (production-like)" -ForegroundColor White
    Write-Host "  .\start-all.ps1 -RecreateDb    # Reset SQLite database" -ForegroundColor White
    Write-Host ""
    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "  -UsePodman      Use Podman Compose to run all services in containers" -ForegroundColor Gray
    Write-Host "                  Includes: Backend, Frontend, PostgreSQL, Redis, Celery, Flower, Nginx" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  -RecreateDb     Delete and recreate SQLite database (local mode only)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  -Help           Show this help message" -ForegroundColor Gray
    Write-Host ""
    Write-Host "MODES:" -ForegroundColor Yellow
    Write-Host "  LOCAL MODE (default)" -ForegroundColor White
    Write-Host "    - Database: SQLite" -ForegroundColor Gray
    Write-Host "    - Services run in separate terminal windows" -ForegroundColor Gray
    Write-Host "    - Fast startup for development" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  PODMAN MODE (-UsePodman)" -ForegroundColor White
    Write-Host "    - Database: PostgreSQL in container" -ForegroundColor Gray
    Write-Host "    - All services containerized" -ForegroundColor Gray
    Write-Host "    - Production-like environment" -ForegroundColor Gray
    Write-Host "    - Requires: podman, podman-compose (pip install podman-compose)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\start-all.ps1                      # Quick dev start" -ForegroundColor White
    Write-Host "  .\start-all.ps1 -UsePodman           # Container-based deployment" -ForegroundColor White
    Write-Host "  .\start-all.ps1 -RecreateDb          # Fresh database" -ForegroundColor White
    Write-Host ""
    exit 0
}

$RootDir = Get-Location
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$VenvPath = Join-Path $BackendDir ".venv"
$DbPath = Join-Path $BackendDir "natpudan.db"

# Load ports and URLs from central config if available
$ConfigPath = Join-Path $RootDir "config/ports.json"
$BackendPort = 8001
$FrontendPort = 5173
$BackendHost = "127.0.0.1"
try {
    if (Test-Path $ConfigPath) {
        $cfg = Get-Content $ConfigPath -Raw | ConvertFrom-Json
        if ($cfg.services.backend.dev) { $BackendPort = [int]$cfg.services.backend.dev }
        if ($cfg.services.frontend.dev) { $FrontendPort = [int]$cfg.services.frontend.dev }
        if ($cfg.urls.backend.dev) {
            # derive host from URL if present
            $u = [Uri]$cfg.urls.backend.dev
            if ($u.Host) { $BackendHost = $u.Host }
            if ($u.Port -gt 0) { $BackendPort = $u.Port }
        }
    }
} catch {
    Write-Host "[WARN] Failed to read config/ports.json, using defaults (backend=$BackendPort, frontend=$FrontendPort)" -ForegroundColor Yellow
}

$BackendUrl = "http://${BackendHost}:${BackendPort}"
$FrontendUrl = "http://localhost:${FrontendPort}"

Write-Host "`n=== NATPUDAN AI - FULL STACK STARTUP (SQLite) ===" -ForegroundColor Cyan
Write-Host "Starting all services...`n" -ForegroundColor Yellow

if (-not $UsePodman) {
    # 0. Setup Database (SQLite)
    Write-Host "[0/5] Database setup (SQLite)..." -ForegroundColor Green
    if ($RecreateDb) {
        if (Test-Path $DbPath) {
            Remove-Item $DbPath -Force 2>$null
            Write-Host "  Cleared old database (per -RecreateDb)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  Preserving existing database (use -RecreateDb to reset)" -ForegroundColor Gray
    }
    Write-Host "  SQLite database path: $DbPath" -ForegroundColor Gray
}

# 1. Backend
if ($UsePodman) {
    Write-Host "[1/5] Starting stack with Podman Compose..." -ForegroundColor Green
    
    # Check if docker-compose.yml exists
    $composeFile = Join-Path $RootDir "docker-compose.yml"
    if (-not (Test-Path $composeFile)) {
        Write-Host "[ERROR] docker-compose.yml not found. Cannot start with Podman." -ForegroundColor Red
        exit 1
    }
    
    # Check if podman-compose is available
    try {
        python -m podman_compose --version 2>&1 | Out-Null
    } catch {
        Write-Host "[ERROR] podman-compose not found. Install with: pip install podman-compose" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "  Stopping any existing containers..." -ForegroundColor Gray
    python -m podman_compose -f docker-compose.nobuild.yml down 2>&1 | Out-Null
    
    Write-Host "  Starting all services with Podman Compose (no build)..." -ForegroundColor Gray
    python -m podman_compose -f docker-compose.nobuild.yml up -d
    
    Write-Host "  Waiting for containers to start (30s)..." -ForegroundColor Gray
    Start-Sleep -Seconds 30
    
    # Show container status
    Write-Host "`n  Container Status:" -ForegroundColor Cyan
    python -m podman_compose ps
    
    # Detect backend/frontend ports from environment or defaults
    $BackendUrl = "http://127.0.0.1:8000"
    $FrontendUrl = "http://127.0.0.1:3000"
    
    # Try to detect actual ports
    $possibleBackend = @("http://127.0.0.1:8000","http://127.0.0.1:8001")
    $possibleFrontend = @("http://127.0.0.1:3000","http://127.0.0.1:5173")
    
    Write-Host "`n  Checking service health..." -ForegroundColor Gray
    foreach ($u in $possibleBackend) {
        try { 
            $response = Invoke-RestMethod -Uri "$u/health" -TimeoutSec 10
            $BackendUrl = $u
            Write-Host "  ✓ Backend healthy at: $BackendUrl" -ForegroundColor Green
            break 
        } catch {
            Write-Host "  × Backend not ready at: $u" -ForegroundColor DarkGray
        }
    }
    
    foreach ($u in $possibleFrontend) {
        try { 
            Invoke-WebRequest -Uri $u -TimeoutSec 10 | Out-Null
            $FrontendUrl = $u
            Write-Host "  ✓ Frontend ready at: $FrontendUrl" -ForegroundColor Green
            break 
        } catch {
            Write-Host "  × Frontend not ready at: $u" -ForegroundColor DarkGray
        }
    }
} else {
    Write-Host "[1/5] Starting FastAPI Backend..." -ForegroundColor Green
    $backendScript = Join-Path $RootDir "start-backend-stable.ps1"
    $backendArgs = "-File `"$backendScript`" -Port $BackendPort -HostAddr $BackendHost"
    Start-Process powershell -ArgumentList "-NoExit", $backendArgs
    Write-Host "  Waiting for Backend to initialize (15s)..." -ForegroundColor Gray
    Start-Sleep -Seconds 15

    # Post-start health checks and connection auto-fix
    $maxBackendRetries = 3
    $backendRetryCount = 0
    $backendHealthy = $false

    while (-not $backendHealthy -and $backendRetryCount -lt $maxBackendRetries) {
        try {
            if ($backendRetryCount -gt 0) {
                Write-Host "  Retrying Backend health check ($($backendRetryCount + 1)/$maxBackendRetries)..." -ForegroundColor Gray
                Start-Sleep -Seconds 5
            }
            $h = Invoke-RestMethod -Uri "$BackendUrl/health" -TimeoutSec 10
            Write-Host "  Backend health: $($h.status)" -ForegroundColor Green
            $backendHealthy = $true
        } catch {
            $backendRetryCount++
            if ($backendRetryCount -eq $maxBackendRetries) {
                Write-Host "  [WARN] Backend health not reachable yet at $BackendUrl/health" -ForegroundColor Yellow
            }
        }
    }

    # Run connection manager auto-fix if available
    try {
        $ch = Invoke-RestMethod -Uri "$BackendUrl/api/connection/health" -TimeoutSec 5
        if (-not $ch.healthy) {
            Write-Host "  Connection issues detected, attempting auto-fix..." -ForegroundColor Yellow
            $fix = Invoke-RestMethod -Method Post -Uri "$BackendUrl/api/connection/auto-fix" -TimeoutSec 10
            Write-Host "  Auto-fix: $($fix.fixes_successful)/$($fix.fixes_attempted) fixes applied" -ForegroundColor Green
        } else {
            Write-Host "  Connection config healthy" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [INFO] Connection health API not available (older build)" -ForegroundColor DarkGray
    }
}

# 2. Celery Worker
if (-not $UsePodman) {
    Write-Host "[2/5] Starting Celery Worker..." -ForegroundColor Green
    $celeryScript = Join-Path $RootDir "start-celery-worker.ps1"
    Start-Process powershell -ArgumentList "-NoExit", "-File", $celeryScript
    Start-Sleep -Seconds 4
} else {
    Write-Host "[2/5] Celery Worker managed by Podman (container)" -ForegroundColor Green
}

# 3. Flower Dashboard (only if using Redis/RabbitMQ broker)
$useRedis = $env:REDIS_URL -and $env:REDIS_URL.Trim() -ne ''
if (-not $UsePodman -and $useRedis) {
    Write-Host "[3/5] Starting Flower Dashboard..." -ForegroundColor Green
    $flowerCmd = @"
cd "$BackendDir"
& "$VenvPath\Scripts\Activate.ps1"
python -m celery -A app.celery_config flower --port=5555 --basic_auth=admin:admin
"@
    Start-Process powershell -NoNewWindow -ArgumentList "-NoExit", "-Command", $flowerCmd
    Start-Sleep -Seconds 3
} else {
    Write-Host "[3/5] Skipping Flower: requires Redis or RabbitMQ broker (set REDIS_URL)." -ForegroundColor Yellow
    Write-Host "      Tip: .\start-redis.ps1 then set REDIS_URL=redis://localhost:6379/0" -ForegroundColor DarkYellow
}

# 4. Frontend
if (-not $UsePodman) {
    Write-Host "[4/5] Starting React Frontend..." -ForegroundColor Green
    # Pre-check and auto-fix .env ports if script exists
    $checkPorts = Join-Path $RootDir "scripts/check-ports.ps1"
    if (Test-Path $checkPorts) {
        try { & powershell -NoProfile -ExecutionPolicy Bypass -File $checkPorts -Fix | Out-Null } catch {}
    }
    $frontendCmd = "cd '$FrontendDir'; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd
    Start-Sleep -Seconds 4
} else {
    Write-Host "[4/5] Frontend managed by Podman (container)" -ForegroundColor Green
}

Write-Host "`n=== ALL SERVICES STARTED ===" -ForegroundColor Cyan
Write-Host "`nSERVICE ENDPOINTS:" -ForegroundColor Yellow
Write-Host "  Frontend:        $FrontendUrl" -ForegroundColor White
Write-Host "  Backend API:     $BackendUrl" -ForegroundColor White
Write-Host "  API Docs:        $BackendUrl/docs" -ForegroundColor White
if ($UsePodman) {
    Write-Host "  PostgreSQL:      localhost:5432" -ForegroundColor White
    Write-Host "  Redis:           localhost:6379" -ForegroundColor White
    Write-Host "  Flower:          http://localhost:5555 (admin/changeme)" -ForegroundColor White
    Write-Host "  Nginx Proxy:     http://localhost:80" -ForegroundColor White
} else {
    Write-Host "  Flower:          http://localhost:5555 (admin/admin)" -ForegroundColor White
}
Write-Host "" -ForegroundColor Gray

if ($UsePodman) {
    Write-Host "PODMAN CONTAINERS:" -ForegroundColor Yellow
    Write-Host "  Running services: Backend, Frontend, Database (PostgreSQL), Redis, Celery, Flower, Nginx" -ForegroundColor White
    Write-Host "  View logs:        python -m podman_compose logs -f [service]" -ForegroundColor Gray
    Write-Host "  Stop all:         python -m podman_compose down" -ForegroundColor Gray
    Write-Host "  Restart:          python -m podman_compose restart [service]" -ForegroundColor Gray
} else {
    Write-Host "DATABASE:" -ForegroundColor Yellow
    Write-Host "  SQLite:          $DbPath" -ForegroundColor White
    Write-Host "  Celery Broker:   $BackendDir\celery_broker.db" -ForegroundColor White
    Write-Host "  Celery Results:  $BackendDir\celery_results.db" -ForegroundColor White
}

Write-Host "`nAI FEATURES:" -ForegroundColor Yellow
Write-Host "  OpenAI API:      ENABLED" -ForegroundColor Green
Write-Host "  Medical Diagnosis: Available" -ForegroundColor Green
Write-Host "  Knowledge Base:  Ready for upload" -ForegroundColor Green
Write-Host "  Drug Checker:    Available" -ForegroundColor Green

if ($UsePodman) {
    Write-Host "`nTo stop all services:" -ForegroundColor Gray
    Write-Host "  python -m podman_compose down" -ForegroundColor White
    Write-Host "`nTo view logs:" -ForegroundColor Gray
    Write-Host "  python -m podman_compose logs -f" -ForegroundColor White
    Write-Host "`nTo restart a service:" -ForegroundColor Gray
    Write-Host "  python -m podman_compose restart backend" -ForegroundColor White
} else {
    Write-Host "`nTo stop all services:" -ForegroundColor Gray
    Write-Host "  1. Close the individual terminal windows" -ForegroundColor Gray
    Write-Host "  2. Or run: taskkill /F /IM powershell.exe" -ForegroundColor Gray
}

Write-Host "`nPress Ctrl+C to exit this window`n" -ForegroundColor Gray
while ($true) { Start-Sleep -Seconds 10 }

