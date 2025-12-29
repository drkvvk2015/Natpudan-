# Natpudan AI - Full Stack Startup Script (SQLite Edition)
# Starts all services: Backend, Celery, Flower, Frontend (No Docker needed)

param(
    [switch]$Help,
    [switch]$RecreateDb,
    [switch]$UsePodman
)

if ($Help) {
    Write-Host "`nNatpudan AI - Full Stack SQLite Setup" -ForegroundColor Cyan
    Write-Host "Usage: .\start-all.ps1`n" -ForegroundColor Yellow
    Write-Host "Starts all services in separate terminal windows" -ForegroundColor Gray
    Write-Host "Database: SQLite (no Docker required)" -ForegroundColor Gray
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
    Write-Host "[1/5] Starting stack with Podman (production-like)..." -ForegroundColor Green
    $deployScript = Join-Path $RootDir "deploy-podman-production.ps1"
    if (-not (Test-Path $deployScript)) {
        Write-Host "[ERROR] deploy-podman-production.ps1 not found. Cannot start with Podman." -ForegroundColor Red
        exit 1
    }
    # Run deployment (detached containers)
    & powershell -NoProfile -ExecutionPolicy Bypass -File $deployScript

    # Detect backend/frontend ports (compose uses 8000/3000 typically)
    $possibleBackend = @("http://127.0.0.1:8001","http://127.0.0.1:8000")
    $possibleFrontend = @("http://127.0.0.1:5173","http://127.0.0.1:3000")
    foreach ($u in $possibleBackend) {
        try { Invoke-RestMethod -Uri "$u/health" -TimeoutSec 5 | Out-Null; $BackendUrl = $u; break } catch {}
    }
    foreach ($u in $possibleFrontend) {
        try { Invoke-WebRequest -Uri $u -TimeoutSec 5 | Out-Null; $FrontendUrl = $u; break } catch {}
    }
    Write-Host "  Detected Backend at: $BackendUrl" -ForegroundColor Gray
    Write-Host "  Detected Frontend at: $FrontendUrl" -ForegroundColor Gray
} else {
    Write-Host "[1/5] Starting FastAPI Backend..." -ForegroundColor Green
    $backendScript = Join-Path $RootDir "start-backend-stable.ps1"
    $backendArgs = "-File `"$backendScript`" -Port $BackendPort -HostAddr $BackendHost"
    Start-Process powershell -ArgumentList "-NoExit", $backendArgs
    Start-Sleep -Seconds 10

    # Post-start health checks and connection auto-fix
    try {
        $h = Invoke-RestMethod -Uri "$BackendUrl/health" -TimeoutSec 10
        Write-Host "  Backend health: $($h.status)" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] Backend health not reachable yet at $BackendUrl/health" -ForegroundColor Yellow
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
Write-Host "  Flower:          http://localhost:5555 (admin/admin)" -ForegroundColor White
Write-Host "" -ForegroundColor Gray
Write-Host "DATABASE:" -ForegroundColor Yellow
Write-Host "  SQLite:          $DbPath" -ForegroundColor White
Write-Host "  Celery Broker:   $BackendDir\celery_broker.db" -ForegroundColor White
Write-Host "  Celery Results:  $BackendDir\celery_results.db" -ForegroundColor White

Write-Host "`nAI FEATURES:" -ForegroundColor Yellow
Write-Host "  OpenAI API:      ENABLED" -ForegroundColor Green
Write-Host "  Medical Diagnosis: Available" -ForegroundColor Green
Write-Host "  Knowledge Base:  Ready for upload" -ForegroundColor Green
Write-Host "  Drug Checker:    Available" -ForegroundColor Green

Write-Host "`nTo stop all services:" -ForegroundColor Gray
Write-Host "  1. Close the individual terminal windows" -ForegroundColor Gray
Write-Host "  2. Or run: taskkill /F /IM powershell.exe" -ForegroundColor Gray

Write-Host "`nPress Ctrl+C to exit this window`n" -ForegroundColor Gray
while ($true) { Start-Sleep -Seconds 10 }

