# Physician AI Assistant - Complete Setup Script
# This script sets up the entire backend environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Physician AI Assistant - Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "1. Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   Found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "   ERROR: Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Navigate to backend directory
$backendPath = Join-Path $PSScriptRoot "backend"
Set-Location $backendPath

# Create virtual environment
Write-Host ""
Write-Host "2. Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   Virtual environment already exists." -ForegroundColor Green
}
else {
    python -m venv venv
    Write-Host "   Virtual environment created." -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "3. Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path "venv" "Scripts" "Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "   Virtual environment activated." -ForegroundColor Green
}
else {
    Write-Host "   ERROR: Could not find activation script." -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host ""
Write-Host "4. Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "   Pip upgraded." -ForegroundColor Green

# Install requirements
Write-Host ""
Write-Host "5. Installing dependencies..." -ForegroundColor Yellow
Write-Host "   This may take several minutes..." -ForegroundColor Cyan
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Dependencies installed successfully." -ForegroundColor Green
}
else {
    Write-Host "   WARNING: Some dependencies may have failed to install." -ForegroundColor Yellow
}

# Create .env file if it doesn't exist
Write-Host ""
Write-Host "6. Setting up environment variables..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   .env file already exists." -ForegroundColor Green
}
else {
    Copy-Item ".env.example" ".env"
    Write-Host "   Created .env file from template." -ForegroundColor Green
    Write-Host "   IMPORTANT: Edit .env file and add your OpenAI API key!" -ForegroundColor Yellow
}

# Create data directories
Write-Host ""
Write-Host "7. Creating data directories..." -ForegroundColor Yellow
$dataDirs = @(
    "data",
    "data/medical_books",
    "data/knowledge_base",
    "data/icd_codes"
)

foreach ($dir in $dataDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "   Created: $dir" -ForegroundColor Green
    }
    else {
        Write-Host "   Exists: $dir" -ForegroundColor Gray
    }
}

# Initialize database
Write-Host ""
Write-Host "8. Initializing database..." -ForegroundColor Yellow
python -c "from app.database.schemas import init_db; init_db()"
Write-Host "   Database initialized." -ForegroundColor Green

# Download NLTK data (if needed)
Write-Host ""
Write-Host "9. Downloading NLP models..." -ForegroundColor Yellow
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"
Write-Host "   NLP models downloaded." -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit backend/.env and add your OpenAI API key" -ForegroundColor White
Write-Host "2. Place medical PDF books in backend/data/medical_books/" -ForegroundColor White
Write-Host "3. Run: python run.py" -ForegroundColor White
Write-Host "4. API will be available at: http://localhost:8000" -ForegroundColor White
Write-Host "5. API docs at: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "For testing without OpenAI API key:" -ForegroundColor Yellow
Write-Host "- The system will work with limited AI features" -ForegroundColor White
Write-Host "- PDF processing and knowledge base will still function" -ForegroundColor White
Write-Host ""
