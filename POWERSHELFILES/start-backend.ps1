#!/usr/bin/env pwsh
<#!
    Start FastAPI backend with uvicorn.
    - Activates repo venv if present
    - Installs backend requirements if needed
    - Chooses port 8000 (fallback 8001 if in use)
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = $PSScriptRoot
$backendPath = Join-Path $repoRoot 'backend'
if (-not (Test-Path $backendPath)) {
    Write-Error "Backend folder not found: $backendPath"
    exit 1
}

# Resolve Python interpreter (prefer repo venv)
$python = $null
$repoVenvPython = Join-Path $repoRoot '.venv/Scripts/python.exe'
$backendVenvPython = Join-Path $backendPath '.venv/Scripts/python.exe'
if (Test-Path $repoVenvPython) { $python = $repoVenvPython }
elseif (Test-Path $backendVenvPython) { $python = $backendVenvPython }
else {
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pyCmd) {
        Write-Error "Python not found. Install Python 3.10+ and ensure it's in PATH, or create a venv in $repoRoot/.venv or $backendPath/.venv"
        exit 1
    }
    $python = $pyCmd.Path
}

# Verify Python version >= 3.10
try {
    $versionOutput = & $python -c "import sys; print(sys.version_info[:3])" 2>$null
    if ($versionOutput -match "\((\d+),\s*(\d+),\s*(\d+)\)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Error "Python $major.$minor detected. Python 3.10+ is required. Please install a newer Python or create a virtualenv with a suitable interpreter."
            exit 1
        }
    }
} catch {
    Write-Warning "Unable to determine Python version. Proceeding but you may encounter runtime errors."
}

Write-Host ("Python: {0}" -f (& $python -V))

# If we started with a system python (not a repo venv), create a backend venv for isolation
if (-not (Test-Path $repoVenvPython) -and -not (Test-Path $backendVenvPython)) {
    try {
        Write-Host "Creating backend virtual environment at $backendPath\.venv" -ForegroundColor Yellow
        & $python -m venv (Join-Path $backendPath '.venv')
        $backendVenvPython = Join-Path $backendPath '.venv/Scripts/python.exe'
        if (Test-Path $backendVenvPython) {
            $python = $backendVenvPython
            Write-Host "Activated backend venv python: $python" -ForegroundColor Green
        } else {
            Write-Warning "Failed to create backend venv. Will continue using system Python."
        }
    } catch {
        Write-Warning "Error creating venv: $_. Exception.Message"
    }
}

# Upgrade pip in chosen interpreter
try {
    & $python -m pip install --upgrade pip --disable-pip-version-check | Out-Host
} catch {
    Write-Warning "pip upgrade failed; pip may be missing in the selected Python environment. Attempting to continue."
}

# Install dependencies
$reqFile = Join-Path $backendPath 'requirements.txt'
if (Test-Path $reqFile) {
    Write-Host "Installing backend dependencies from requirements.txt..." -ForegroundColor Yellow
    try {
        & $python -m pip install --disable-pip-version-check -r $reqFile | Out-Host
    } catch {
        Write-Warning "Failed to install from requirements.txt: $_. Exception.Message"
        Write-Host "You can try: & $python -m pip install -r $reqFile" -ForegroundColor Cyan
    }
}
else {
    Write-Warning "requirements.txt not found; attempting minimal deps install."
    try {
        & $python -m pip install --disable-pip-version-check fastapi uvicorn[standard] python-multipart pydantic PyMuPDF python-dotenv psutil | Out-Host
    } catch {
        Write-Warning "Minimal dependency install failed: $_. Exception.Message"
        Write-Host "Install dependencies manually or create backend/requirements.txt. Example: fastapi>=0.95 uvicorn[standard]" -ForegroundColor Cyan
    }
}

# Pick port 8000 with fallback to 8001
$desiredPort = 8000
$fallbackPort = 8001
$portToUse = $desiredPort
$useHttps = $false
try {
    $inUse = Get-NetTCPConnection -LocalPort $desiredPort -State Listen -ErrorAction Stop
    if ($inUse) { $portToUse = $fallbackPort }
}
catch {
    $tnc = Test-NetConnection -ComputerName 'localhost' -Port $desiredPort -WarningAction SilentlyContinue
    if ($tnc.TcpTestSucceeded) { $portToUse = $fallbackPort }
}

# Start uvicorn
Push-Location $backendPath
try {
    $protocol = if ($useHttps) { "https" } else { "http" }
    Write-Host "Starting FastAPI (uvicorn) from: $backendPath on port $portToUse ($protocol)" -ForegroundColor Green
    Write-Host "API Docs: ${protocol}://localhost:$portToUse/docs" -ForegroundColor Cyan
    Write-Host "Health Check: ${protocol}://localhost:$portToUse/health" -ForegroundColor Cyan
    $env:PYTHONPATH = $backendPath
    
    # Show the exact command about to run
    $uvicornCmd = "& `"$python`" -m uvicorn app.main:app --reload --host 0.0.0.0 --port $portToUse"
    Write-Host "Running: $uvicornCmd" -ForegroundColor DarkCyan

    if ($useHttps) {
        $certPath = Join-Path $backendPath 'certs/cert.pem'
        $keyPath = Join-Path $backendPath 'certs/key.pem'
        if ((Test-Path $certPath) -and (Test-Path $keyPath)) {
            & $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $portToUse --ssl-keyfile $keyPath --ssl-certfile $certPath
        } else {
            Write-Warning "SSL certificates not found. Falling back to HTTP."
            & $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $portToUse
        }
    } else {
        & $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $portToUse
    }
}
catch {
    Write-Error "Failed to start uvicorn: $_"
    Write-Host "Suggestion: Ensure dependencies are installed and that Python interpreter ($python) is valid." -ForegroundColor Yellow
    exit 1
}
finally {
    Pop-Location
}
