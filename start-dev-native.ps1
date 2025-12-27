# Simple Podman/Docker Development Launcher
# Run both backend and frontend without container complexity

$RootDir = Get-Location
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Natpudan AI - Simple Development Mode" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "[Setup] Checking environment..." -ForegroundColor Yellow

# Check Python
$pythonVersion = python --version 2>&1
Write-Host "[Setup] Python: $pythonVersion" -ForegroundColor Green

# Check Node
$nodeVersion = node --version 2>&1
Write-Host "[Setup] Node: $nodeVersion" -ForegroundColor Green

# Check npm
$npmVersion = npm --version 2>&1
Write-Host "[Setup] npm: $npmVersion" -ForegroundColor Green

Write-Host ""

# Backend
Write-Host "[1/2] Starting Backend on http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "      (Opening in new window...)" -ForegroundColor Gray

$backendCmd = @"
cd '$BackendDir'
Write-Host 'Activating virtual environment...' -ForegroundColor Yellow
& '.\\.venv\\Scripts\\Activate.ps1'
Write-Host 'Starting FastAPI server...' -ForegroundColor Green
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Start-Sleep -Seconds 3

# Frontend
Write-Host "[2/2] Starting Frontend on http://127.0.0.1:5173" -ForegroundColor Cyan
Write-Host "      (Opening in new window...)" -ForegroundColor Gray

$frontendCmd = @"
cd '$FrontendDir'
Write-Host 'Installing dependencies (if needed)...' -ForegroundColor Yellow
npm install --legacy-peer-deps
Write-Host 'Starting Vite dev server...' -ForegroundColor Green
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Start-Sleep -Seconds 2

# Display info
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API:       http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Frontend Web:      http://127.0.0.1:5173" -ForegroundColor Yellow
Write-Host "API Docs:          http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "Swagger UI:        http://127.0.0.1:8000/redoc" -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend window: Check for uvicorn startup messages" -ForegroundColor Gray
Write-Host "Frontend window: Check for Vite dev server messages" -ForegroundColor Gray
Write-Host ""
Write-Host "Close either window to stop that service" -ForegroundColor Gray
Write-Host ""
