# Backend Startup Script with Debug Output
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Starting Backend Server with Debug Mode" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

$ErrorActionPreference = "Continue"

# Navigate to backend directory
Set-Location "D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend"

Write-Host "`n[1/5] Checking Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python found" -ForegroundColor Green

Write-Host "`n[2/5] Testing imports..." -ForegroundColor Yellow
$importTest = python -c "import sys; sys.path.insert(0, '.'); from app.main import app; print('SUCCESS')" 2>&1
Write-Host $importTest
if ($importTest -notlike "*SUCCESS*") {
    Write-Host "`n[ERROR] Import failed! Error above." -ForegroundColor Red
    Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
Write-Host "[OK] Imports successful" -ForegroundColor Green

Write-Host "`n[3/5] Checking database..." -ForegroundColor Yellow
if (Test-Path "natpudan.db") {
    Write-Host "[OK] Database file exists" -ForegroundColor Green
}
else {
    Write-Host "[WARNING]  Database will be created" -ForegroundColor Yellow
}

Write-Host "`n[4/5] Checking port 8001..." -ForegroundColor Yellow
$portCheck = Test-NetConnection -ComputerName 127.0.0.1 -Port 8001 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($portCheck) {
    Write-Host "[WARNING]  Port 8001 already in use - stopping existing process..." -ForegroundColor Yellow
    Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*Natpudan-*" } | Stop-Process -Force
    Start-Sleep -Seconds 2
}
Write-Host "[OK] Port 8001 available" -ForegroundColor Green

Write-Host "`n[5/5] Starting Uvicorn server..." -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Start server with unbuffered output
$env:PYTHONUNBUFFERED = "1"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
