#!/usr/bin/env pwsh
# Upgrade Backend to Python 3.12.10
# This fixes scipy compatibility issues with Python 3.14

Write-Host "`n🔧 Upgrading Backend to Python 3.12.10" -ForegroundColor Cyan
Write-Host "=" * 60

# 1. Stop any running backend servers
Write-Host "`n1️⃣ Stopping backend servers..." -ForegroundColor Yellow
Get-Process | Where-Object {
    ($_.ProcessName -like "*python*" -or $_.ProcessName -like "*uvicorn*") -and
    $_.Path -like "*Natpudan*"
} | ForEach-Object {
    Write-Host "   Stopping $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor Gray
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

# 2. Backup old venv (optional)
Write-Host "`n2️⃣ Backing up old venv..." -ForegroundColor Yellow
if (Test-Path "backend\.venv") {
    if (Test-Path "backend\.venv.old") {
        Remove-Item "backend\.venv.old" -Recurse -Force
    }
    Rename-Item "backend\.venv" ".venv.old"
    Write-Host "   ✅ Old venv backed up to .venv.old" -ForegroundColor Green
}

# 3. Create new venv with Python 3.12
Write-Host "`n3️⃣ Creating new venv with Python 3.12..." -ForegroundColor Yellow
cd backend
python -m venv .venv
Write-Host "   ✅ New venv created" -ForegroundColor Green

# 4. Activate and upgrade pip
Write-Host "`n4️⃣ Upgrading pip..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
Write-Host "   ✅ Pip upgraded" -ForegroundColor Green

# 5. Install dependencies
Write-Host "`n5️⃣ Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    Write-Host "   ✅ Dependencies installed from requirements.txt" -ForegroundColor Green
} else {
    Write-Host "   ⚠️ requirements.txt not found - installing core packages..." -ForegroundColor Yellow
    pip install fastapi uvicorn sqlalchemy pydantic openai faiss-cpu sentence-transformers apscheduler pytesseract pdf2image
    Write-Host "   ✅ Core packages installed" -ForegroundColor Green
}

# 6. Verify installation
Write-Host "`n6️⃣ Verifying installation..." -ForegroundColor Yellow
$pythonVersion = python --version
Write-Host "   Python: $pythonVersion" -ForegroundColor Cyan

# Check critical packages
$packages = @("fastapi", "uvicorn", "sqlalchemy", "openai", "scipy")
foreach ($pkg in $packages) {
    $installed = pip show $pkg 2>$null
    if ($installed) {
        $version = ($installed | Select-String "Version:").ToString().Split(":")[1].Trim()
        Write-Host "   ✅ $pkg $version" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $pkg NOT INSTALLED" -ForegroundColor Red
    }
}

Write-Host "`n" + ("=" * 60)
Write-Host "✨ Upgrade Complete!" -ForegroundColor Green
Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Start backend: .\start-backend.ps1" -ForegroundColor White
Write-Host "   2. Verify no scipy errors" -ForegroundColor White
Write-Host "   3. Re-enable knowledge base in main.py" -ForegroundColor White
Write-Host "`n"
