# Setup Script for Physician AI Assistant
# This script automates the complete setup process

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Physician AI Assistant - Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "Step 1: Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
    
    if ($pythonVersion -match "Python 3\.([8-9]|1[0-9])") {
        Write-Host "  ✓ Python version is compatible" -ForegroundColor Green
    }
    else {
        Write-Host "  ⚠ Warning: Python 3.8+ recommended" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "  ✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Step 2: Create directory structure
Write-Host "`nStep 2: Creating directory structure..." -ForegroundColor Yellow

$directories = @(
    "backend",
    "backend\app",
    "backend\app\api",
    "backend\app\services",
    "backend\app\models",
    "backend\app\database",
    "backend\data",
    "backend\data\knowledge_base",
    "backend\data\knowledge_base\chroma_db",
    "backend\data\medical_books",
    "backend\data\logs",
    "backend\tests"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
    else {
        Write-Host "  Exists: $dir" -ForegroundColor Gray
    }
}

# Step 3: Create virtual environment
Write-Host "`nStep 3: Setting up virtual environment..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path "venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor White
    python -m venv venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}
else {
    Write-Host "  Virtual environment already exists" -ForegroundColor Gray
}

# Step 4: Activate virtual environment
Write-Host "`nStep 4: Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green

# Step 5: Upgrade pip
Write-Host "`nStep 5: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "  ✓ pip upgraded" -ForegroundColor Green

# Step 6: Install requirements
Write-Host "`nStep 6: Installing Python packages..." -ForegroundColor Yellow
Write-Host "  This may take several minutes..." -ForegroundColor White

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt --quiet
    Write-Host "  ✓ All packages installed" -ForegroundColor Green
}
else {
    Write-Host "  ⚠ requirements.txt not found, installing core packages..." -ForegroundColor Yellow
    
    $packages = @(
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "openai==1.3.5",
        "chromadb==0.4.18",
        "sentence-transformers==2.2.2",
        "pymupdf==1.23.8",
        "python-dotenv==1.0.0",
        "pydantic==2.5.0",
        "python-multipart==0.0.6"
    )
    
    foreach ($package in $packages) {
        Write-Host "  Installing $package..." -ForegroundColor White
        pip install $package --quiet
    }
    
    Write-Host "  ✓ Core packages installed" -ForegroundColor Green
}

# Step 7: Create .env file
Write-Host "`nStep 7: Setting up configuration..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  ✓ Created .env from .env.example" -ForegroundColor Green
    }
    else {
        # Create basic .env
        @"
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./physician_ai.db

# Directories
KNOWLEDGE_BASE_DIR=data/knowledge_base
MEDICAL_BOOKS_DIR=data/medical_books
LOG_DIR=data/logs

# LLM Settings
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.3
MAX_TOKENS=800
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "  ✓ Created default .env file" -ForegroundColor Green
    }
    
    Write-Host "  ⚠ Please edit .env and add your OpenAI API key!" -ForegroundColor Yellow
}
else {
    Write-Host "  .env file already exists" -ForegroundColor Gray
}

# Step 8: Create __init__.py files
Write-Host "`nStep 8: Creating Python package files..." -ForegroundColor Yellow

$initFiles = @(
    "app\__init__.py",
    "app\api\__init__.py",
    "app\services\__init__.py",
    "app\models\__init__.py",
    "app\database\__init__.py"
)

foreach ($initFile in $initFiles) {
    if (-not (Test-Path $initFile)) {
        New-Item -ItemType File -Path $initFile -Force | Out-Null
        Write-Host "  Created: $initFile" -ForegroundColor Green
    }
}

# Step 9: Initialize database
Write-Host "`nStep 9: Initializing database..." -ForegroundColor Yellow

if (Test-Path "app\database\connection.py") {
    $dbInit = @"
import sys
sys.path.insert(0, '.')

try:
    from app.database.connection import init_db
    init_db()
    print('  ✓ Database initialized successfully')
except Exception as e:
    print(f'  ⚠ Database initialization: {e}')
    print('  (This is normal if files are not yet created)')
"@
    
    $dbInit | python 2>&1 | ForEach-Object {
        Write-Host $_
    }
}
else {
    Write-Host "  ⚠ Database connection module not found" -ForegroundColor Yellow
    Write-Host "    Will be initialized on first run" -ForegroundColor White
}

# Step 10: Download NLP models
Write-Host "`nStep 10: Downloading NLP models..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes on first run..." -ForegroundColor White

$modelDownload = @"
import sys
sys.path.insert(0, '.')

try:
    from sentence_transformers import SentenceTransformer
    print('  Downloading embedding model...')
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print('  ✓ NLP models downloaded')
except Exception as e:
    print(f'  ⚠ Model download: {e}')
"@

$modelDownload | python 2>&1 | ForEach-Object {
    Write-Host $_
}

# Summary
Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Edit .env file and add your OpenAI API key:" -ForegroundColor Yellow
Write-Host "     notepad .env" -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. (Optional) Add medical PDFs to:" -ForegroundColor Yellow
Write-Host "     $PWD\data\medical_books\" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3. Run tests to verify installation:" -ForegroundColor Yellow
Write-Host "     cd .." -ForegroundColor Yellow
Write-Host "     .\test.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "  4. Start the server:" -ForegroundColor Yellow
Write-Host "     cd backend" -ForegroundColor Yellow
Write-Host "     python run.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "  5. Access the API documentation:" -ForegroundColor Yellow
Write-Host "     http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Return to parent directory
Set-Location ..

Write-Host "Setup script completed successfully!" -ForegroundColor Green
Write-Host ""
