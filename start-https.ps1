#!/usr/bin/env pwsh
<#
    Start Natpudan AI - Simplified HTTPS Setup
    - Starts backend on https://127.0.0.1:8000
    - Starts frontend on https://127.0.0.1:5173
    - No proxy - direct API calls
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = $PSScriptRoot
$backendPath = Join-Path $repoRoot 'backend'
$frontendPath = Join-Path $repoRoot 'frontend'

Write-Host "`n=== Natpudan AI Startup (HTTPS) ===" -ForegroundColor Cyan

# Check Python
$python = Join-Path $repoRoot '.venv/Scripts/python.exe'
if (-not (Test-Path $python)) {
    Write-Error "Python venv not found at $python. Run setup first."
    exit 1
}

# Check Node/npm
$npm = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npm) {
    Write-Error "npm not found. Install Node.js first."
    exit 1
}

# Check SSL certificates
$certPath = Join-Path $backendPath 'certs/cert.pem'
$keyPath = Join-Path $backendPath 'certs/key.pem'
if (-not (Test-Path $certPath) -or -not (Test-Path $keyPath)) {
    Write-Host "Generating SSL certificates..." -ForegroundColor Yellow
    Push-Location $backendPath
    & $python -m pip install cryptography --quiet
    & $python generate_cert.py
    Pop-Location
    
    # Copy to frontend
    $frontendCerts = Join-Path $frontendPath 'certs'
    New-Item -ItemType Directory -Path $frontendCerts -Force | Out-Null
    Copy-Item $certPath, $keyPath -Destination $frontendCerts
}

Write-Host "`n✓ Prerequisites checked" -ForegroundColor Green

# Kill existing processes on ports
Write-Host "`nStopping existing services..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.ProcessName -eq 'python' } | Stop-Process -Force 2>$null
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | 
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force } 2>$null
Start-Sleep -Seconds 2

# Start backend
Write-Host "`nStarting Backend (https://127.0.0.1:8000)..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    param($python, $backendPath, $certPath, $keyPath)
    Set-Location $backendPath
    $env:PYTHONPATH = $backendPath
    & $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile $keyPath --ssl-certfile $certPath
} -ArgumentList $python, $backendPath, $keyPath, $certPath

Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting Frontend (https://127.0.0.1:5173)..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    param($frontendPath)
    Set-Location $frontendPath
    npx vite --host 127.0.0.1 --port 5173
} -ArgumentList $frontendPath

Start-Sleep -Seconds 3

Write-Host "`n✓ Services started!" -ForegroundColor Green
Write-Host "`n  Backend:  https://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  Frontend: https://127.0.0.1:5173" -ForegroundColor Cyan
Write-Host "  API Docs: https://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "`n  Note: Accept self-signed certificate warnings in browser" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C to stop all services`n" -ForegroundColor DarkGray

# Monitor jobs
try {
    while ($true) {
        if ($backendJob.State -eq 'Failed') {
            Write-Error "Backend job failed!"
            Receive-Job $backendJob
            break
        }
        if ($frontendJob.State -eq 'Failed') {
            Write-Error "Frontend job failed!"
            Receive-Job $frontendJob
            break
        }
        Start-Sleep -Seconds 2
    }
}
finally {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -Force -ErrorAction SilentlyContinue
    Get-Process | Where-Object { $_.ProcessName -eq 'python' } | Stop-Process -Force 2>$null
    Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | 
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force } 2>$null
}
