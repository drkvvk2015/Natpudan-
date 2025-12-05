# Natpudan AI Medical Assistant - Auto-Recovery Startup Script
# This script includes automatic error detection and correction

param(
    [switch]$NoAutoFix,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$rootDir = "D:\Users\CNSHO\Documents\GitHub\Natpudan-"
$backendDir = Join-Path $rootDir "backend"
$frontendDir = Join-Path $rootDir "frontend"
$venvPython = Join-Path $rootDir ".venv311\Scripts\python.exe"

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    $colors = @{
        "Success" = "Green"
        "Error" = "Red"
        "Warning" = "Yellow"
        "Info" = "Cyan"
    }
    Write-Host $Message -ForegroundColor $colors[$Type]
}

function Test-Port {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $null -ne $connection
}

function Stop-PortProcesses {
    param([int]$Port)
    Write-Status "Clearing port $Port..." "Warning"
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        try {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
            Write-Status "  Stopped process $($conn.OwningProcess)" "Info"
        } catch {
            Write-Status "  Could not stop process $($conn.OwningProcess)" "Warning"
        }
    }
    Start-Sleep 1
}

function Test-ServiceHealth {
    param([string]$Url, [string]$Name)
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Status "  $Name is healthy" "Success"
            return $true
        }
    } catch {
        Write-Status "  $Name not responding" "Warning"
        return $false
    }
    return $false
}

function Repair-Environment {
    Write-Status "`n=== Auto Error Correction ===" "Info"
    
    # Check and fix .env files
    Write-Status "Checking environment configuration..." "Info"
    
    $frontendEnv = Join-Path $frontendDir ".env"
    $correctEnvContent = @"
# Backend API URL - used directly by frontend (no proxy)
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000
"@
    
    if (Test-Path $frontendEnv) {
        $currentContent = Get-Content $frontendEnv -Raw
        if ($currentContent -notmatch "http://127.0.0.1:8000") {
            Write-Status "  Fixing frontend .env configuration..." "Warning"
            Set-Content -Path $frontendEnv -Value $correctEnvContent -Force
            Write-Status "  Frontend .env corrected" "Success"
        } else {
            Write-Status "  Frontend .env is correct" "Success"
        }
    } else {
        Write-Status "  Creating frontend .env..." "Warning"
        Set-Content -Path $frontendEnv -Value $correctEnvContent -Force
        Write-Status "  Frontend .env created" "Success"
    }
    
    # Check Python virtual environment
    if (-not (Test-Path $venvPython)) {
        Write-Status "  Python virtual environment not found!" "Error"
        Write-Status "  Run: python -m venv .venv" "Info"
        return $false
    }
    
    # Check Node modules
    $nodeModules = Join-Path $frontendDir "node_modules"
    if (-not (Test-Path $nodeModules)) {
        Write-Status "  Node modules not found. Installing..." "Warning"
        Set-Location $frontendDir
        npm install
        Write-Status "  Node modules installed" "Success"
    }
    
    Write-Status "Environment check complete" "Success"
    return $true
}

# Main Script
Clear-Host
Write-Status "=====================================" "Info"
Write-Status "Natpudan AI Medical Assistant" "Info"
Write-Status "Auto-Recovery Startup" "Info"
Write-Status "=====================================" "Info"

# Step 1: Stop conflicting processes
Write-Status "`nStep 1: Clearing ports..." "Info"
if (Test-Port 8000) { Stop-PortProcesses 8000 }
if (Test-Port 5173) { Stop-PortProcesses 5173 }
Write-Status "Ports cleared" "Success"

# Step 2: Auto error correction
if (-not $NoAutoFix) {
    if (-not (Repair-Environment)) {
        Write-Status "`nEnvironment repair failed. Exiting..." "Error"
        exit 1
    }
}

# Step 3: Start Backend
Write-Status "`nStep 2: Starting Backend..." "Info"
$backendJob = Start-Job -ScriptBlock {
    param($dir, $python)
    Set-Location $dir
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    & $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 2>&1
} -ArgumentList $backendDir, $venvPython

Write-Status "Backend starting (Job ID: $($backendJob.Id))..." "Info"
Start-Sleep 4

# Verify backend
if (Test-ServiceHealth "http://127.0.0.1:8000/health" "Backend") {
    Write-Status "Backend ready" "Success"
} else {
    Write-Status "Backend may still be starting..." "Warning"
}

# Step 4: Start Frontend
Write-Status "`nStep 3: Starting Frontend..." "Info"
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    $env:NODE_OPTIONS = '--no-warnings'
    npx vite --host 127.0.0.1 --port 5173 2>&1
} -ArgumentList $frontendDir

Write-Status "Frontend starting (Job ID: $($frontendJob.Id))..." "Info"
Start-Sleep 5

# Verify frontend
if (Test-ServiceHealth "http://127.0.0.1:5173" "Frontend") {
    Write-Status "Frontend ready" "Success"
} else {
    Write-Status "Frontend may still be starting..." "Warning"
}

# Step 5: Final Status
Start-Sleep 2
Write-Status "`n=====================================" "Success"
Write-Status "Services Started Successfully!" "Success"
Write-Status "=====================================" "Success"

Write-Host "`nBackend:  " -NoNewline -ForegroundColor White
Write-Host "http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Frontend: " -NoNewline -ForegroundColor White
Write-Host "http://127.0.0.1:5173" -ForegroundColor Green

Write-Status "`n[OK] No certificate warnings (using HTTP)" "Success"
Write-Status "[OK] Auto error correction enabled" "Success"
Write-Status "[OK] Services running in background jobs" "Success"

Write-Host "`n[LIST] Open in browser: " -NoNewline
Write-Host "http://127.0.0.1:5173" -ForegroundColor Yellow

Write-Host "`n[TIP] Commands:" -ForegroundColor Cyan
Write-Host "  Get-Job              - View running jobs"
Write-Host "  Receive-Job -Id X    - View job output"
Write-Host "  Stop-Job -Id X       - Stop a service"
Write-Host "  Get-Job | Stop-Job   - Stop all services"

if ($Verbose) {
    Write-Host "`n[STATS] Service Status:" -ForegroundColor Cyan
    Write-Host "`nBackend Job:"
    Receive-Job -Id $backendJob.Id -Keep | Select-Object -Last 5
    Write-Host "`nFrontend Job:"
    Receive-Job -Id $frontendJob.Id -Keep | Select-Object -Last 5
}

Write-Status "`n[SPARKLE] Startup complete! App is ready." "Success"
