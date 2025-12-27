#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Starts the Natpudan AI Medical Assistant backend on port 9000
.DESCRIPTION
    Starts FastAPI backend without Redis/Celery dependency.
    Use this when Redis is not available on your system.
#>

$BackendPath = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend"
$VenvPath = "D:\Users\CNSHO\Documents\GitHub\Natpudan-\.venv"
$PythonExe = "$VenvPath\Scripts\python.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Natpudan Backend Startup (Port 9000)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path $VenvPath)) {
    Write-Host "[ERROR] Virtual environment not found at: $VenvPath" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Using Python: $PythonExe" -ForegroundColor Green
Write-Host "[INFO] Backend path: $BackendPath" -ForegroundColor Green
Write-Host ""

# Set PYTHONPATH and start backend
$env:PYTHONPATH = $BackendPath
Write-Host "[INFO] Starting FastAPI backend on http://127.0.0.1:9000" -ForegroundColor Yellow
Write-Host "[INFO] Reload enabled - changes will auto-reload" -ForegroundColor Yellow
Write-Host ""

& $PythonExe -m uvicorn app.main:app `
    --host 127.0.0.1 `
    --port 9000 `
    --reload
