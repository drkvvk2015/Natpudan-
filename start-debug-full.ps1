# ============================================================================
# Natpudan AI Medical Assistant - COMPLETE DEBUG SETUP
# ============================================================================
# Orchestrates full stack debugging with:
#   - Docker containers (Redis, PostgreSQL via docker-compose)
#   - FastAPI Backend (Port 8000)
#   - React Frontend (Port 5173)
#   - Celery Worker (background tasks)
#   - Flower Dashboard (monitoring at http://localhost:5555)
#   - Redis Broker (message broker at localhost:6379)
# ============================================================================

param(
    [switch]$DockerOnly,     # Only run Docker services
    [switch]$NoFrontend,     # Skip frontend startup
    [switch]$SkipRedis,      # Use Docker Redis instead of local
    [switch]$Help            # Show help
)

# ============================================================================
# CONFIGURATION
# ============================================================================
$ErrorActionPreference = "Continue"
$global:RootDir = "D:\Users\CNSHO\Documents\GitHub\Natpudan-"
$global:BackendDir = Join-Path $global:RootDir "backend"
$global:FrontendDir = Join-Path $global:RootDir "frontend"
$global:VenvPath = Join-Path $global:BackendDir "venv"

# Service URLs
$global:BackendUrl = "http://127.0.0.1:8000"
$global:FrontendUrl = "http://127.0.0.1:5173"
$global:FlowerUrl = "http://localhost:5555"
$global:RedisUrl = "redis://localhost:6379"

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

function Show-Help {
    Write-Host @"
╔════════════════════════════════════════════════════════════════════════════╗
║         NATPUDAN AI - COMPLETE DEBUG STARTUP SCRIPT                        ║
╚════════════════════════════════════════════════════════════════════════════╝

USAGE:
  .\start-debug-full.ps1 [OPTIONS]

OPTIONS:
  -DockerOnly    Run only Docker services (Redis, PostgreSQL, Nginx)
  -NoFrontend    Skip React frontend startup
  -SkipRedis     Skip local Redis, use Docker Redis instead
  -Help          Show this help message

EXAMPLES:
  # Full stack with all services
  .\start-debug-full.ps1

  # Only Docker services
  .\start-debug-full.ps1 -DockerOnly

  # Without frontend
  .\start-debug-full.ps1 -NoFrontend

ARCHITECTURE:
  ┌─────────────────────────────────────────────────────┐
  │ Frontend (React + TypeScript)                       │
  │ http://localhost:5173                              │
  └────────────────┬────────────────────────────────────┘
                   │
  ┌────────────────▼────────────────────────────────────┐
  │ Backend (FastAPI)                                   │
  │ http://localhost:8000                              │
  │ - RESTful API endpoints                            │
  │ - WebSocket support                                │
  │ - Database operations (PostgreSQL)                 │
  └────────────────┬────────────────────────────────────┘
                   │
  ┌────────────────▼────────────────────────────────────┐
  │ Celery Worker                                       │
  │ - Background task processing                       │
  │ - Scheduled jobs                                   │
  └────────────────┬────────────────────────────────────┘
                   │
  ┌────────────────▼────────────────────────────────────┐
  │ Message Broker & Cache                              │
  │ - Redis (localhost:6379)                            │
  │ - Docker PostgreSQL (localhost:5432)                │
  └─────────────────────────────────────────────────────┘

MONITORING DASHBOARDS:
  Flower (Celery):     $FlowerUrl           (admin/admin)
  Backend Health:      $BackendUrl/health
  Backend Docs:        $BackendUrl/docs
  Backend ReDoc:       $BackendUrl/redoc

"@ -ForegroundColor Cyan
    exit 0
}

function Write-Section {
    param([string]$Title, [string]$Type = "Info")
    $Width = 80
    $Padding = [math]::Floor(($Width - $Title.Length - 2) / 2)
    Write-Host "`n" + ("=" * $Width) -ForegroundColor $Colors[$Type]
    Write-Host ("  " + $Title) -ForegroundColor $Colors[$Type]
    Write-Host ("=" * $Width) -ForegroundColor $Colors[$Type]
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

function Test-Port {
    param([int]$Port, [string]$Service = "Service")
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("127.0.0.1", $Port)
        $tcp.Close()
        return $true
    } catch {
        return $false
    }
}

function Wait-ForService {
    param([int]$Port, [string]$Service, [int]$MaxWait = 60)
    Write-Status "Waiting for $Service on port $Port (max $MaxWait sec)..." "Info" "[WAIT]"
    
    $startTime = Get-Date
    while ((Get-Date) - $startTime -lt [TimeSpan]::FromSeconds($MaxWait)) {
        if (Test-Port -Port $Port) {
            Write-Status "$Service is ready!" "Success" "OK"
            return $true
        }
        Start-Sleep -Milliseconds 500
    }
    
    Write-Status "$Service failed to start within ${MaxWait}s" "Error" "FAIL"
    return $false
}

function Test-Docker {
    Write-Status "Checking Docker installation..." "Info" "[DOCKER]"
    try {
        $version = docker --version 2>$null
        if ($version) {
            Write-Status "Docker found: $version" "Success" "OK"
            
            # Check if Docker daemon is running
            docker ps >$null 2>&1
            if ($?) {
                Write-Status "Docker daemon is running" "Success" "OK"
                return $true
            } else {
                Write-Status "Docker daemon not responding. Starting Docker Desktop..." "Warning" "WARN"
                Start-Process "Docker Desktop"
                Start-Sleep -Seconds 10
                return $true
            }
        }
    } catch {
        Write-Status "Docker not found!" "Error" "ERROR"
        Write-Host ""
        Write-Host "Please install Docker Desktop:" -ForegroundColor Yellow
        Write-Host "  Option 1: https://www.docker.com/products/docker-desktop" -ForegroundColor Gray
        Write-Host "  Option 2: choco install docker-desktop (as Administrator)" -ForegroundColor Gray
        Write-Host "  Option 3: winget install Docker.DockerDesktop" -ForegroundColor Gray
        Write-Host ""
        Write-Host "After installation, restart your terminal and try again." -ForegroundColor Yellow
        Write-Host ""
        return $false
    }
}

function Test-Python {
    Write-Status "Checking Python installation..." "Info" "[PYTHON]"
    try {
        $version = python --version 2>&1
        Write-Status "Python found: $version" "Success" "OK"
        return $true
    } catch {
        Write-Status "Python not found!" "Error" "ERROR"
        return $false
    }
}

function Setup-Venv {
    Write-Status "Setting up Python virtual environment..." "Info" "📦"
    
    if (Test-Path $global:VenvPath) {
        Write-Status "Virtual environment already exists" "Info" "OK"
    } else {
        Write-Status "Creating virtual environment..." "Warning" "[WAIT]"
        python -m venv $global:VenvPath
        Write-Status "Virtual environment created" "Success" "OK"
    }
    
    Write-Status "Activating virtual environment..." "Info" "[SETUP]"
    & "$global:VenvPath\Scripts\Activate.ps1"
    
    Write-Status "Upgrading pip..." "Info" "[SETUP]"
    python -m pip install --upgrade pip -q
    
    Write-Status "Installing dependencies..." "Info" "[SETUP]"
    pip install -r "$global:BackendDir\requirements.txt" -q
    
    Write-Status "Virtual environment ready" "Success" "OK"
}

function Start-DockerServices {
    Write-Section "STARTING DOCKER SERVICES" "Info"
    
    if (-not (Test-Docker)) {
        Write-Status "Docker is not available, skipping Docker services" "Error" "ERROR"
        return $false
    }
    
    Write-Status "Starting docker-compose services..." "Info" "[DOCKER]"
    
    Push-Location $global:RootDir
    try {
        # Stop existing containers
        docker-compose down -v 2>$null
        Start-Sleep -Seconds 2
        
        # Start new containers
        docker-compose up -d
        
        Write-Status "Docker services started" "Success" "OK"
        
        # Wait for services
        Write-Status "Waiting for PostgreSQL..." "Info" "[WAIT]"
        Start-Sleep -Seconds 10
        
        return $true
    } catch {
        Write-Status "Failed to start Docker services: $_" "Error" "ERROR"
        return $false
    } finally {
        Pop-Location
    }
}

function Start-Backend {
    Write-Section "STARTING FASTAPI BACKEND" "Info"
    
    Setup-Venv
    
    Write-Status "Starting FastAPI backend on port 8000..." "Info" "[STARTUP]"
    
    Push-Location $global:BackendDir
    try {
        # Start backend in new terminal - using single quotes to prevent ampersand issues
        $psCommand = '& "' + $global:VenvPath + '\Scripts\Activate.ps1"; cd "' + $global:BackendDir + '"; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload'
        
        Start-Process powershell -ArgumentList @('-NoExit', '-Command', $psCommand)
        
        if (Wait-ForService -Port 8000 -Service "FastAPI Backend" -MaxWait 30) {
            Write-Status "Backend API: $($global:BackendUrl)" "Success" "OK"
            Write-Status "API Docs: $($global:BackendUrl)/docs" "Info" "[DOCS]"
            Write-Status "Health check: $($global:BackendUrl)/health" "Info" "[HEALTH]"
            return $true
        } else {
            return $false
        }
    } catch {
        Write-Status "Failed to start backend: $_" "Error" "ERROR"
        return $false
    } finally {
        Pop-Location
    }
}

function Start-Redis {
    Write-Section "STARTING REDIS BROKER" "Info"
    
    if ($SkipRedis) {
        Write-Status "Skipping local Redis (using Docker)" "Info" "[SKIP]"
        return $true
    }
    
    Write-Status "Checking if Redis is available locally..." "Info" "[CHECK]"
    
    if (Get-Command redis-server -ErrorAction SilentlyContinue) {
        Write-Status "Starting Redis server..." "Info" "[STARTUP]"
        
        # Start in new terminal
        Start-Process powershell -ArgumentList @('-NoExit', '-Command', 'redis-server')
        
        if (Wait-ForService -Port 6379 -Service "Redis" -MaxWait 20) {
            Write-Status "Redis Broker: $($global:RedisUrl)" "Success" "OK"
            return $true
        } else {
            Write-Status "Redis not available, tasks may fail" "Warning" "[WARN]"
            return $false
        }
    } else {
        Write-Status "Redis not installed locally, trying Docker..." "Warning" "[WAIT]"
        
        # Try Docker
        docker run -d --name redis-debug -p 6379:6379 redis:latest 2>$null
        
        if (Wait-ForService -Port 6379 -Service "Redis (Docker)" -MaxWait 20) {
            Write-Status "Redis (Docker): $($global:RedisUrl)" "Success" "OK"
            return $true
        } else {
            Write-Status "Could not start Redis" "Error" "ERROR"
            return $false
        }
    }
}

function Start-CeleryWorker {
    Write-Section "STARTING CELERY WORKER" "Info"
    
    Write-Status "Starting Celery worker..." "Info" "[SETUP]"
    
    Setup-Venv
    
    $psCommand = @'
cd "$global:BackendDir"
. "$global:VenvPath\Scripts\Activate.ps1"
Write-Host "Celery Worker Starting..." -ForegroundColor Cyan
celery -A app.celery_config worker --loglevel=info --concurrency=4 --max-tasks-per-child=1000
'@ -replace '\$global:BackendDir', $global:BackendDir -replace '\$global:VenvPath', $global:VenvPath
    
    Start-Process powershell -ArgumentList @('-NoExit', '-Command', $psCommand)
    
    Write-Status "Celery worker started (check separate terminal)" "Success" "OK"
    Write-Status "Worker: Celery worker listening for tasks" "Info" "[QUEUE]"
    return $true
}

function Start-FlowerDashboard {
    Write-Section "STARTING FLOWER MONITORING DASHBOARD" "Info"
    
    Write-Status "Starting Flower dashboard..." "Info" "[SETUP]"
    
    Setup-Venv
    
    $psCommand = @'
cd "$global:BackendDir"
. "$global:VenvPath\Scripts\Activate.ps1"
Write-Host "Flower Dashboard Starting..." -ForegroundColor Cyan
celery -A app.celery_config flower --port=5555 --basic_auth=admin:admin
'@ -replace '\$global:BackendDir', $global:BackendDir -replace '\$global:VenvPath', $global:VenvPath
    
    Start-Process powershell -ArgumentList @('-NoExit', '-Command', $psCommand)
    
    Start-Sleep -Seconds 3
    
    if (Test-Port -Port 5555) {
        Write-Status "Flower Dashboard: $($global:FlowerUrl)" "Success" "OK"
        Write-Status "Username: admin" "Info" "[USER]"
        Write-Status "Password: admin" "Info" "[PASS]"
        Write-Status "Opening in browser..." "Info" "[OPEN]"
        Start-Process $global:FlowerUrl
        return $true
    } else {
        Write-Status "Flower may not be available yet" "Warning" "WAIT"
        return $true
    }
}

function Start-Frontend {
    if ($NoFrontend) {
        Write-Status "Frontend startup skipped (-NoFrontend)" "Info" "SKIP"
        return $true
    }
    
    Write-Section "STARTING REACT FRONTEND" "Info"
    
    Write-Status "Starting Vite dev server on port 5173..." "Info" "[VITE]"
    
    Push-Location $global:FrontendDir
    try {
        # Check if node_modules exists
        if (-not (Test-Path "node_modules")) {
            Write-Status "Installing npm dependencies..." "Warning" "[WAIT]"
            npm install -q
        }
        
        $psCommand = @'
cd "$global:FrontendDir"
npm run dev
'@ -replace '\$global:FrontendDir', $global:FrontendDir
        
        Start-Process powershell -ArgumentList @('-NoExit', '-Command', $psCommand)
        
        if (Wait-ForService -Port 5173 -Service "Frontend Dev Server" -MaxWait 30) {
            Write-Status "Frontend: $($global:FrontendUrl)" "Success" "OK"
            Write-Status "Opening in browser..." "Info" "[OPEN]"
            Start-Process $global:FrontendUrl
            return $true
        } else {
            return $false
        }
    } catch {
        Write-Status "Failed to start frontend: $_" "Error" "ERROR"
        return $false
    } finally {
        Pop-Location
    }
}

function Show-Summary {
    Write-Section "DEBUG SETUP COMPLETE" "Success"
    
    Write-Host @"
╔════════════════════════════════════════════════════════════════════════════╗
║                       SERVICE ENDPOINTS                                    ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  [WEB] Frontend (React)                                                    ║
║     → http://localhost:5173                                               ║
║                                                                            ║
║  [API] Backend API (FastAPI)                                              ║
║     → http://localhost:8000                                               ║
║     → Documentation: http://localhost:8000/docs                           ║
║     → ReDoc: http://localhost:8000/redoc                                  ║
║     → Health: http://localhost:8000/health                                ║
║                                                                            ║
║  [FLOWER] Flower Dashboard (Celery Monitoring)                            ║
║     → http://localhost:5555                                               ║
║     → Username: admin                                                     ║
║     → Password: admin                                                     ║
║                                                                            ║
║  [REDIS] Redis Broker                                                     ║
║     → redis://localhost:6379                                              ║
║                                                                            ║
║  [DB] PostgreSQL Database (Docker)                                        ║
║     → postgresql://physician_user:secure_password@localhost:5432          ║
║                                                                            ║
╠════════════════════════════════════════════════════════════════════════════╣
║                    DEBUGGING TIPS                                          ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  1. Monitor Backend Logs                                                  ║
║     → Check the FastAPI terminal for request logs                         ║
║     → Available at http://localhost:8000/docs                             ║
║                                                                            ║
║  2. Monitor Celery Tasks                                                  ║
║     → Open Flower Dashboard: http://localhost:5555                        ║
║     → Real-time task execution tracking                                   ║
║     → Worker status and performance metrics                               ║
║                                                                            ║
║  3. Check Redis Connection                                                ║
║     → Redis should be running on port 6379                                ║
║     → Check backend logs for connection errors                            ║
║                                                                            ║
║  4. Monitor Database                                                      ║
║     → PostgreSQL running in Docker on port 5432                           ║
║     → Run 'docker logs physician-ai-db' for DB logs                       ║
║                                                                            ║
║  5. Frontend Development                                                  ║
║     → Hot reload enabled at port 5173                                     ║
║     → Check browser console for errors (F12)                              ║
║     → Network tab shows API calls to backend                              ║
║                                                                            ║
║  6. Test API Endpoints                                                    ║
║     → Use Swagger UI at http://localhost:8000/docs                        ║
║     → Try example requests directly from browser                          ║
║     → Monitor response times and errors                                   ║
║                                                                            ║
╠════════════════════════════════════════════════════════════════════════════╣
║                    STOPPING SERVICES                                       ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Close individual service terminals (Ctrl+C in each terminal)            ║
║  Or run: docker-compose down                                              ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

# ============================================================================
# MAIN EXECUTION LOGIC
# ============================================================================

# Handle help flag
if ($Help) {
    Show-Help
    exit 0
}

# Check prerequisites
Write-Section "PRE-FLIGHT CHECKS" "Info"

if (-not (Test-Python)) {
    Write-Status "Python is required!" "Error" "ERROR"
    exit 1
}

if (-not (Test-Docker)) {
    Write-Status "Docker is required for this debug setup!" "Error" "ERROR"
    exit 1
}

Write-Status "All prerequisites met" "Success" "OK"

# Execute based on parameters
if ($DockerOnly) {
    Write-Section "DOCKER-ONLY MODE" "Info"
    Start-DockerServices
} else {
    # Full stack debug setup
    Write-Host "`n"
    Write-Section "NATPUDAN AI - COMPLETE DEBUG SETUP" "Success"
    
    # Start services in order
    Start-DockerServices | Out-Null
    Start-Redis | Out-Null
    Start-Backend | Out-Null
    Start-CeleryWorker | Out-Null
    Start-FlowerDashboard | Out-Null
    Start-Frontend | Out-Null
    
    # Show summary
    Show-Summary
}

Write-Status "Press Ctrl+C in any terminal to stop services" "Info" "[STOP]"
Write-Status "Setup complete! Check the dashboards above for monitoring" "Success" "OK"

# Keep script running
while ($true) { Start-Sleep -Seconds 10 }
