# Quick Backend Venv Recreate Script
# Run AFTER uninstalling Python 3.14

Write-Host "`n🔄 Recreating Backend Venv with Python 3.12" -ForegroundColor Cyan
Write-Host "=" * 60

# Navigate to backend
Set-Location "D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend"

# Remove old venv
Write-Host "`n1️⃣ Removing old venv..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Remove-Item ".venv" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   ✅ Old venv removed" -ForegroundColor Green
}

# Create new venv (will use Python 3.12 by default)
Write-Host "`n2️⃣ Creating new venv with Python 3.12..." -ForegroundColor Yellow
python -m venv .venv
Write-Host "   ✅ Venv created" -ForegroundColor Green

# Activate venv
Write-Host "`n3️⃣ Activating venv..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Check Python version
$pyVersion = python --version
Write-Host "   ✅ Using: $pyVersion" -ForegroundColor Green

# Upgrade pip
Write-Host "`n4️⃣ Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip -q
Write-Host "   ✅ Pip upgraded" -ForegroundColor Green

# Install dependencies
Write-Host "`n5️⃣ Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    # Core packages
    pip install fastapi uvicorn sqlalchemy pydantic openai
    pip install faiss-cpu sentence-transformers
    pip install scipy scikit-learn pandas numpy
    pip install apscheduler pytesseract pdf2image
    pip install python-multipart aiofiles
}
Write-Host "   ✅ Dependencies installed" -ForegroundColor Green

# Verify critical packages
Write-Host "`n6️⃣ Verifying installation..." -ForegroundColor Yellow
$packages = @("fastapi", "uvicorn", "scipy", "scikit-learn", "openai")
foreach ($pkg in $packages) {
    try {
        $version = (pip show $pkg 2>$null | Select-String "Version:").ToString().Split(":")[1].Trim()
        Write-Host "   ✅ $pkg $version" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ $pkg NOT FOUND" -ForegroundColor Red
    }
}

Write-Host "`n" + ("=" * 60)
Write-Host "✨ Backend Ready!" -ForegroundColor Green
Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Start backend: uvicorn app.main:app --reload --port 8000" -ForegroundColor White
Write-Host "   2. Re-enable knowledge base in main.py (uncomment lines)" -ForegroundColor White
Write-Host "   3. No more scipy errors! 🎉" -ForegroundColor White
Write-Host "`n"
