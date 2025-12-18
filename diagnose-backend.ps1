# Quick Backend Diagnostics
Write-Host "`n=== BACKEND DIAGNOSTICS ===" -ForegroundColor Cyan

# 1. Check if port is listening
Write-Host "`n[1] Checking port 8000..." -ForegroundColor Yellow
$port = netstat -ano | Select-String ":8000" | Select-String "LISTENING"
if ($port) {
    Write-Host "✅ Port 8000 is LISTENING" -ForegroundColor Green
    $port
} else {
    Write-Host "❌ Port 8000 is NOT listening" -ForegroundColor Red
    exit 1
}

# 2. Check OpenAI API key in .env
Write-Host "`n[2] Checking OPENAI_API_KEY..." -ForegroundColor Yellow
$envFile = "d:\Users\CNSHO\Documents\GitHub\Natpudan-\backend\.env"
if (Test-Path $envFile) {
    $apiKey = Get-Content $envFile | Select-String "OPENAI_API_KEY"
    if ($apiKey) {
        $keyValue = ($apiKey -split "=")[1].Trim()
        if ($keyValue -match "^sk-") {
            Write-Host "✅ Valid API key format detected" -ForegroundColor Green
        } else {
            Write-Host "❌ Invalid API key format: $($keyValue.Substring(0, [Math]::Min(15, $keyValue.Length)))..." -ForegroundColor Red
            Write-Host "   API key must start with 'sk-'" -ForegroundColor Yellow
            Write-Host "   Fix: Edit backend/.env and set a valid OpenAI API key" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  OPENAI_API_KEY not found in .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ .env file not found at $envFile" -ForegroundColor Red
}

# 3. Try to connect to backend
Write-Host "`n[3] Testing backend connection..." -ForegroundColor Yellow
Write-Host "Attempting to reach http://localhost:8000/health (5 second timeout)..." -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "✅ Backend is responding!" -ForegroundColor Green
    Write-Host "Response: $response" -ForegroundColor White
} catch {
    Write-Host "❌ Backend not responding (timeout)" -ForegroundColor Red
    Write-Host "   This usually means the backend is stuck during startup" -ForegroundColor Yellow
    Write-Host "   Common causes:" -ForegroundColor Yellow
    Write-Host "   - Invalid OpenAI API key validation hanging" -ForegroundColor Gray
    Write-Host "   - Database initialization stuck" -ForegroundColor Gray
    Write-Host "   - Long-running startup tasks" -ForegroundColor Gray
}

# 4. Suggest fixes
Write-Host "`n=== SUGGESTED FIXES ===" -ForegroundColor Cyan
Write-Host "1. Check backend terminal for error messages" -ForegroundColor White
Write-Host "2. If OpenAI key is invalid, update backend/.env:" -ForegroundColor White
Write-Host "   OPENAI_API_KEY=sk-your-real-key-here" -ForegroundColor Gray
Write-Host "3. Restart backend: Press Ctrl+C in backend terminal, then:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .\\venv\\Scripts\\Activate.ps1" -ForegroundColor Gray
Write-Host "   python -m uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "4. Or kill all and restart: taskkill /F /IM python.exe; .\\start-all.ps1" -ForegroundColor White

Write-Host "`n"
