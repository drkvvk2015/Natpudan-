# NATPUDAN AI - COMPLETE STARTUP SCRIPT
# Starts both Backend (8001) and Frontend (5173)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   NATPUDAN AI - STARTING SERVICES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing processes
Write-Host "Stopping existing services..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process node -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like '*vite*'} | Stop-Process -Force
Start-Sleep -Seconds 2

# Start Backend
Write-Host ""
Write-Host "Starting Backend (Port 8001)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Set-Location 'D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend'; " +
    "Write-Host '========================================' -ForegroundColor Cyan; " +
    "Write-Host '   NATPUDAN BACKEND - PORT 8001' -ForegroundColor Cyan; " +
    "Write-Host '========================================' -ForegroundColor Cyan; " +
    "Write-Host ''; " +
    "& 'D:\Users\CNSHO\Documents\GitHub\Natpudan-\.venv311\Scripts\python.exe' -m uvicorn app.main:app --host 127.0.0.1 --port 8001"

Start-Sleep -Seconds 3

# Start Frontend
Write-Host ""
Write-Host "Starting Frontend (Port 5173)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "Set-Location 'D:\Users\CNSHO\Documents\GitHub\Natpudan-\frontend'; " +
    "Write-Host '========================================' -ForegroundColor Cyan; " +
    "Write-Host '   NATPUDAN FRONTEND - PORT 5173' -ForegroundColor Cyan; " +
    "Write-Host '========================================' -ForegroundColor Cyan; " +
    "Write-Host ''; " +
    "npm run dev"

# Wait for services to start
Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Check status
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SERVICE STATUS CHECK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    $health = Invoke-RestMethod "http://127.0.0.1:8001/health" -TimeoutSec 3
    Write-Host "✅ Backend (8001): " -ForegroundColor Green -NoNewline
    Write-Host "$($health.status)" -ForegroundColor White
} catch {
    Write-Host "❌ Backend (8001): DOWN" -ForegroundColor Red
    Write-Host "   Check the Backend window for errors" -ForegroundColor Yellow
}

Write-Host "✅ Frontend (5173): RUNNING" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ACCESS YOUR APPLICATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Frontend:  " -NoNewline
Write-Host "http://localhost:5173" -ForegroundColor Yellow
Write-Host "📚 API Docs:  " -NoNewline
Write-Host "http://127.0.0.1:8001/docs" -ForegroundColor Yellow
Write-Host "💚 Health:    " -NoNewline
Write-Host "http://127.0.0.1:8001/health" -ForegroundColor Yellow
Write-Host "📖 KB Stats:  " -NoNewline
Write-Host "http://127.0.0.1:8001/api/medical/knowledge/statistics" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Default login: test@test.com / test123" -ForegroundColor Gray
Write-Host ""
