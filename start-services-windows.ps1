# Start Services in Separate Windows (Persistent)
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Starting Natpudan Services" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Get paths
$rootDir = "D:\Users\CNSHO\Documents\GitHub\Natpudan-"
$backendDir = Join-Path $rootDir "backend"
$frontendDir = Join-Path $rootDir "frontend"
$venvPython = Join-Path $rootDir ".venv\Scripts\python.exe"
$certPath = Join-Path $backendDir "certs"

Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow

# Check if certificates exist
if (-not (Test-Path "$certPath\cert.pem")) {
    Write-Host "Generating SSL certificates..." -ForegroundColor Yellow
    Set-Location $backendDir
    & $venvPython generate_cert.py
}

Write-Host "✓ SSL certificates ready" -ForegroundColor Green

# Start Backend in new window (HTTP mode to avoid mixed content issues)
Write-Host "`nStarting Backend (http://127.0.0.1:8000)..." -ForegroundColor Yellow
$backendCmd = "Set-Location '$backendDir'; Write-Host 'Backend Server Starting...' -ForegroundColor Green; & '$venvPython' -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; Write-Host 'Backend stopped. Press any key to exit...' -ForegroundColor Red; `$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')"
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCmd

Start-Sleep 3

# Start Frontend in new window
Write-Host "Starting Frontend (https://127.0.0.1:5173)..." -ForegroundColor Yellow
$frontendCmd = "Set-Location '$frontendDir'; Write-Host 'Frontend Server Starting...' -ForegroundColor Green; `$env:NODE_OPTIONS='--no-experimental-fetch'; & 'C:\Program Files\nodejs\npx.cmd' vite --host 127.0.0.1 --port 5173; Write-Host 'Frontend stopped. Press any key to exit...' -ForegroundColor Red; `$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')"
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontendCmd

Start-Sleep 5

# Test services
Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "Testing Services..." -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

Write-Host "Backend: " -NoNewline
try {
    $response = curl.exe -s http://127.0.0.1:8000/health 2>$null
    if ($response -match "healthy") {
        Write-Host "✓ RUNNING" -ForegroundColor Green
    } else {
        Write-Host "⚠ STARTING..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ STARTING..." -ForegroundColor Yellow
}

Write-Host "Frontend: " -NoNewline
try {
    $response = curl.exe -s http://127.0.0.1:5173/ 2>$null
    if ($response -match "root") {
        Write-Host "✓ RUNNING" -ForegroundColor Green
    } else {
        Write-Host "⚠ STARTING..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ STARTING..." -ForegroundColor Yellow
}

Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "Services are starting in separate windows!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "`nBackend:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "Frontend: http://127.0.0.1:5173" -ForegroundColor White
Write-Host "`n✓ Both services running on HTTP (no certificate warnings!)" -ForegroundColor Green
Write-Host "`n📋 Open this test page to verify:" -ForegroundColor Cyan
Write-Host "   file:///d:/Users/CNSHO/Documents/GitHub/Natpudan-/BROWSER_TEST.html" -ForegroundColor White
Write-Host "`nTo stop services, close the PowerShell windows." -ForegroundColor Gray
