# Fast Install Script - Install packages in smaller batches
# Use if setup.ps1 package installation is too slow

Write-Host "Fast Package Installation" -ForegroundColor Cyan
Write-Host ""

Set-Location backend
& .\venv\Scripts\Activate.ps1

Write-Host "Installing packages in batches..." -ForegroundColor Yellow
Write-Host ""

# Batch 1: Core web framework
Write-Host "[1/5] Installing web framework..." -ForegroundColor White
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-multipart==0.0.6

# Batch 2: Database
Write-Host "[2/5] Installing database..." -ForegroundColor White
pip install sqlalchemy==2.0.23 pydantic==2.5.0

# Batch 3: OpenAI
Write-Host "[3/5] Installing OpenAI..." -ForegroundColor White
pip install openai==1.3.5 python-dotenv==1.0.0

# Batch 4: PDF processing
Write-Host "[4/5] Installing PDF processor..." -ForegroundColor White
pip install pymupdf==1.23.8

# Batch 5: AI/ML (this is the slow one)
Write-Host "[5/5] Installing AI/ML packages (this takes 3-5 minutes)..." -ForegroundColor White
pip install chromadb==0.4.18 sentence-transformers==2.2.2

Write-Host ""
Write-Host "✓ All packages installed!" -ForegroundColor Green

Set-Location ..
