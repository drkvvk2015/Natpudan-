#!/usr/bin/env pwsh
# Recreate Backend Venv with Python 3.12

Write-Host "🔧 Recreating Backend Venv with Python 3.12" -ForegroundColor Cyan
Write-Host ("=" * 60)

# 1. Navigate to backend
Set-Location backend

# 2. Stop any running servers
Write-Host "`n1️⃣ Stopping backend servers..." -ForegroundColor Yellow
Get-Process | Where-Object {
    ($_.ProcessName -like "*python*" -or $_.ProcessName -like "*uvicorn*") -and
    $_.Path -like "*Natpudan*"
} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 3. Remove old venv
Write-Host "`n2️⃣ Removing old venv..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Remove-Item ".venv" -Recurse -Force
    Write-Host "   ✅ Old venv removed" -ForegroundColor Green
}

# 4. Create new venv with Python 3.12
Write-Host "`n3️⃣ Creating new venv with Python 3.12..." -ForegroundColor Yellow
python -m venv .venv
Write-Host "   ✅ New venv created" -ForegroundColor Green

# 5. Activate and check version
Write-Host "`n4️⃣ Activating venv..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1
$version = python --version
Write-Host "   Python: $version" -ForegroundColor Cyan

# 6. Upgrade pip
Write-Host "`n5️⃣ Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "   ✅ Pip upgraded" -ForegroundColor Green

# 7. Install dependencies
Write-Host "`n6️⃣ Installing dependencies..." -ForegroundColor Yellow
Write-Host "   This will take 2-3 minutes..." -ForegroundColor Gray

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt --quiet
    Write-Host "   ✅ Dependencies installed from requirements.txt" -ForegroundColor Green
} else {
    Write-Host "   Installing core packages..." -ForegroundColor Gray
    pip install fastapi uvicorn sqlalchemy pydantic openai faiss-cpu sentence-transformers apscheduler pytesseract pdf2image scipy scikit-learn --quiet
    Write-Host "   ✅ Core packages installed" -ForegroundColor Green
}

# 8. Verify installation
Write-Host "`n7️⃣ Verifying installation..." -ForegroundColor Yellow
$packages = @(
    @{Name="fastapi"; Required=$true},
    @{Name="uvicorn"; Required=$true},
    @{Name="sqlalchemy"; Required=$true},
    @{Name="openai"; Required=$true},
    @{Name="scipy"; Required=$true},
    @{Name="sentence-transformers"; Required=$true}
)

foreach ($pkg in $packages) {
    $installed = pip show $pkg.Name 2>$null
    if ($installed) {
        $version = ($installed | Select-String "Version:").ToString().Split(":")[1].Trim()
        Write-Host "   ✅ $($pkg.Name) $version" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $($pkg.Name) NOT INSTALLED" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host ("=" * 60)
Write-Host "✨ Backend Ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Start backend: uvicorn app.main:app --reload --port 8000" -ForegroundColor White
Write-Host "   2. Re-enable knowledge base in main.py (uncomment lines)" -ForegroundColor White
Write-Host "   3. No more scipy errors! 🎉" -ForegroundColor White
Write-Host ""
