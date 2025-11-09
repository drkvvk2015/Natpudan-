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
        Write-Error "Python not found. Install Python 3.10+ and ensure it's in PATH, or create a venv in $repoRoot/.venv"
        exit 1
    }
    $python = $pyCmd.Path
}

Write-Host ("Python: {0}" -f (& $python -V))

# Install dependencies
$reqFile = Join-Path $backendPath 'requirements.txt'
if (Test-Path $reqFile) {
    Write-Host "Installing backend dependencies (if needed)..." -ForegroundColor Yellow
    & $python -m pip install --disable-pip-version-check -r $reqFile | Out-Host
}
else {
    Write-Warning "requirements.txt not found; attempting minimal deps install."
    & $python -m pip install --disable-pip-version-check fastapi uvicorn[standard] python-multipart pydantic PyMuPDF python-dotenv | Out-Host
}

# Pick port 8000 with fallback to 8001
$desiredPort = 8000
$fallbackPort = 8001
$portToUse = $desiredPort
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
    Write-Host "Starting FastAPI (uvicorn) from: $backendPath on port $portToUse" -ForegroundColor Green
    $env:PYTHONPATH = $backendPath
    & $python -m uvicorn app.main:app --host 0.0.0.0 --port $portToUse
}
finally {
    Pop-Location
}
