#requires -version 5.1
<#!
Setup All Features for Natpudan AI Medical Assistant
- Validates prerequisites (Python, Node, Redis/Memurai)
- Installs backend and frontend dependencies
- Initializes database and knowledge base index
- Optionally starts Redis, Celery worker/beat, backend (uvicorn), and frontend (Vite)

Run this script from the repository root.
#>

param(
    [switch]$StartServices = $true,
    [int]$ApiPort = 9000,
    [int]$FrontendPort = 5173
)

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[ERR]  $msg" -ForegroundColor Red }

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $repoRoot

# 1) Python venv and backend deps
Write-Info "Ensuring Python virtual environment (.venv)"
$venvPath = Join-Path $repoRoot ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Info "Creating virtual environment at $venvPath"
    python -m venv $venvPath
}
# Activate
& "$venvPath\Scripts\Activate.ps1"

Write-Info "Installing backend dependencies"
Push-Location "$repoRoot\backend"
if (Test-Path "$repoRoot\backend\requirements.txt") {
    pip install -r requirements.txt | Out-String | Write-Host
    Write-Ok "Backend dependencies installed"
} else {
    Write-Warn "requirements.txt not found under backend/"
}
Pop-Location

# 2) Frontend deps
Write-Info "Installing frontend dependencies"
Push-Location "$repoRoot\frontend"
if (Test-Path "$repoRoot\frontend\package.json") {
    npm ci | Out-String | Write-Host
    Write-Ok "Frontend dependencies installed"
} else {
    Write-Warn "package.json not found under frontend/"
}
Pop-Location

# 3) Redis/Memurai check
Write-Info "Checking Redis/Memurai availability"
$redisService = Get-Service -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "memurai|redis" }
if ($redisService) {
    if ($redisService.Status -ne 'Running') {
        Write-Info "Starting service: $($redisService.Name)"
        Start-Service $redisService.Name
        Start-Sleep -Seconds 2
    }
    Write-Ok "Redis service running: $($redisService.Name)"
} else {
    $memuraiExe = "C:\Program Files\Memurai\memurai.exe"
    if (Test-Path $memuraiExe) {
        Write-Info "Starting Memurai executable"
        Start-Process -FilePath $memuraiExe -ArgumentList "--port 6379" -WindowStyle Minimized
        Start-Sleep -Seconds 2
        Write-Ok "Memurai started via executable"
    } else {
        Write-Warn "Redis/Memurai not found; install Memurai or Redis for full features"
    }
}

# 4) Ensure backend .env has placeholders
Write-Info "Ensuring backend .env contains required keys"
$envPath = "$repoRoot\backend\.env"
if (-not (Test-Path $envPath)) {
    @"
DATABASE_URL=sqlite:///./natpudan.db
SECRET_KEY=your-secret-key-change-in-production
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
API_HOST=127.0.0.1
API_PORT=$ApiPort
"@ | Set-Content -Path $envPath -Encoding UTF8
    Write-Ok "Created backend .env with placeholders"
} else {
    Write-Info "Backend .env already present"
}

# 5) Initialize database
Write-Info "Initializing database schema"
Push-Location "$repoRoot\backend"
if (Test-Path "$repoRoot\backend\init_db_manual.py") {
    python .\init_db_manual.py | Out-String | Write-Host
    Write-Ok "Database initialized"
} else {
    Write-Warn "init_db_manual.py not found; relying on app startup to init DB"
}
Pop-Location

# 6) Build knowledge base index (optional)
Write-Info "Building knowledge base index if content present"
if (Test-Path "$repoRoot\init_kb_direct.py") {
    python .\init_kb_direct.py | Out-String | Write-Host
    Write-Ok "Knowledge base initialization attempted"
} else {
    Write-Warn "init_kb_direct.py not found; skipping KB init"
}

# 7) Optionally start services
if ($StartServices) {
    Write-Info "Starting Celery worker and beat"
    Push-Location "$repoRoot\backend"
    $celeryWorker = Start-Process -FilePath "$venvPath\Scripts\python.exe" -ArgumentList "-m celery -A app.tasks worker -l info" -PassThru -WindowStyle Minimized
    $celeryBeat = Start-Process -FilePath "$venvPath\Scripts\python.exe" -ArgumentList "-m celery -A app.tasks beat -l info" -PassThru -WindowStyle Minimized
    Write-Ok "Celery worker PID=$($celeryWorker.Id), beat PID=$($celeryBeat.Id)"
    Pop-Location

    Write-Info "Starting backend (uvicorn) on port $ApiPort"
    Push-Location "$repoRoot\backend"
    $backendProc = Start-Process -FilePath "$venvPath\Scripts\python.exe" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port $ApiPort --reload" -PassThru
    Pop-Location

    Write-Info "Starting frontend (Vite) on port $FrontendPort"
    Push-Location "$repoRoot\frontend"
    $frontendProc = Start-Process -FilePath "npm" -ArgumentList "run dev -- --port $FrontendPort" -PassThru
    Pop-Location

    Write-Ok "Services started: backend PID=$($backendProc.Id), frontend PID=$($frontendProc.Id)"
}

# 8) Feature health endpoint quick check
Write-Info "Quick health check: /api/health/features"
try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$ApiPort/api/health/features" -TimeoutSec 5
    Write-Ok "Health features: $($resp.StatusCode)"
} catch {
    Write-Warn "Health features check skipped or server not yet up"
}

Pop-Location
Write-Ok "Setup complete"
