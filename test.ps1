# Test Script for Physician AI Assistant
# This script runs comprehensive tests to verify the installation

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Physician AI Assistant - Test Suite" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0
$WarningCount = 0

# Change to backend directory
Set-Location backend

# Test 1: Check if virtual environment exists
Write-Host "Test 1: Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "  ✓ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "  ✗ Virtual environment not found. Run setup.ps1 first!" -ForegroundColor Red
    $ErrorCount++
}

# Test 2: Activate virtual environment
Write-Host "`nTest 2: Activating virtual environment..." -ForegroundColor Yellow
try {
    & .\venv\Scripts\Activate.ps1
    Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to activate virtual environment: $_" -ForegroundColor Red
    $ErrorCount++
    exit 1
}

# Test 3: Check Python version
Write-Host "`nTest 3: Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  Found: $pythonVersion" -ForegroundColor White
if ($pythonVersion -match "Python 3\.([8-9]|1[0-9])") {
    Write-Host "  ✓ Python version is compatible" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python version may not be compatible (need 3.8+)" -ForegroundColor Red
    $ErrorCount++
}

# Test 4: Check required packages
Write-Host "`nTest 4: Checking installed packages..." -ForegroundColor Yellow
$requiredPackages = @("fastapi", "uvicorn", "sqlalchemy", "openai", "chromadb", "sentence-transformers", "pymupdf")

foreach ($package in $requiredPackages) {
    $installed = pip show $package 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $package installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $package not installed" -ForegroundColor Red
        $ErrorCount++
    }
}

# Test 5: Check .env file
Write-Host "`nTest 5: Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green
    
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "OPENAI_API_KEY=sk-") {
        Write-Host "  ✓ OpenAI API key configured" -ForegroundColor Green
    } elseif ($envContent -match "OPENAI_API_KEY=your-openai-api-key") {
        Write-Host "  ⚠ OpenAI API key not set (using fallback mode)" -ForegroundColor Yellow
        $WarningCount++
    } else {
        Write-Host "  ⚠ OpenAI API key format may be invalid" -ForegroundColor Yellow
        $WarningCount++
    }
} else {
    Write-Host "  ✗ .env file not found. Copy .env.example to .env" -ForegroundColor Red
    $ErrorCount++
}

# Test 6: Check directory structure
Write-Host "`nTest 6: Checking directory structure..." -ForegroundColor Yellow
$requiredDirs = @(
    "app",
    "app\api",
    "app\services",
    "app\models",
    "app\database",
    "data\knowledge_base",
    "data\medical_books",
    "data\logs"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "  ✓ $dir exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dir missing" -ForegroundColor Red
        $ErrorCount++
    }
}

# Test 7: Check database
Write-Host "`nTest 7: Checking database..." -ForegroundColor Yellow
if (Test-Path "physician_ai.db") {
    Write-Host "  ✓ Database file exists" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Database not initialized (will be created on first run)" -ForegroundColor Yellow
    $WarningCount++
}

# Test 8: Test Python imports
Write-Host "`nTest 8: Testing Python imports..." -ForegroundColor Yellow
$importTest = @"
import sys
sys.path.insert(0, '.')

try:
    # Test core imports
    import fastapi
    print('  ✓ FastAPI imported')
    
    import uvicorn
    print('  ✓ Uvicorn imported')
    
    import sqlalchemy
    print('  ✓ SQLAlchemy imported')
    
    from app.services.knowledge_base import KnowledgeBase
    print('  ✓ KnowledgeBase imported')
    
    from app.services.llm_service import LLMService
    print('  ✓ LLMService imported')
    
    from app.services.medical_assistant import MedicalAssistant
    print('  ✓ MedicalAssistant imported')
    
    from app.services.drug_checker import DrugChecker
    print('  ✓ DrugChecker imported')
    
    from app.services.icd_mapper import ICDMapper
    print('  ✓ ICDMapper imported')
    
    from app.main import app
    print('  ✓ FastAPI app imported')
    
    print('IMPORT_TEST_PASSED')
except Exception as e:
    print(f'  ✗ Import failed: {e}')
    print('IMPORT_TEST_FAILED')
"@

$importTest | python 2>&1 | ForEach-Object {
    if ($_ -match "✓") {
        Write-Host $_ -ForegroundColor Green
    } elseif ($_ -match "✗") {
        Write-Host $_ -ForegroundColor Red
        $ErrorCount++
    } elseif ($_ -match "IMPORT_TEST_PASSED") {
        # Success indicator
    } elseif ($_ -match "IMPORT_TEST_FAILED") {
        $ErrorCount++
    } else {
        Write-Host $_ -ForegroundColor White
    }
}

# Test 9: Test database connection
Write-Host "`nTest 9: Testing database connection..." -ForegroundColor Yellow
$dbTest = @"
import sys
sys.path.insert(0, '.')

try:
    from app.database.connection import engine, get_db, init_db
    from sqlalchemy import text
    
    # Try to connect
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('  ✓ Database connection successful')
        print('DB_TEST_PASSED')
except Exception as e:
    print(f'  ✗ Database connection failed: {e}')
    print('DB_TEST_FAILED')
"@

$dbTest | python 2>&1 | ForEach-Object {
    if ($_ -match "✓") {
        Write-Host $_ -ForegroundColor Green
    } elseif ($_ -match "✗") {
        Write-Host $_ -ForegroundColor Red
        $ErrorCount++
    } elseif ($_ -match "DB_TEST_PASSED") {
        # Success indicator
    } elseif ($_ -match "DB_TEST_FAILED") {
        $ErrorCount++
    } else {
        Write-Host $_ -ForegroundColor White
    }
}

# Test 10: Test service initialization
Write-Host "`nTest 10: Testing service initialization..." -ForegroundColor Yellow
$serviceTest = @"
import sys
import asyncio
sys.path.insert(0, '.')

async def test_services():
    try:
        from app.services.llm_service import LLMService
        llm = LLMService()
        print('  ✓ LLMService initialized')
        
        from app.services.drug_checker import DrugChecker
        drug_checker = DrugChecker()
        print('  ✓ DrugChecker initialized')
        
        from app.services.icd_mapper import ICDMapper
        icd_mapper = ICDMapper()
        print('  ✓ ICDMapper initialized')
        
        # Note: KnowledgeBase requires async initialization
        print('  ℹ KnowledgeBase requires async initialization (tested at runtime)')
        
        print('SERVICE_TEST_PASSED')
    except Exception as e:
        print(f'  ✗ Service initialization failed: {e}')
        print('SERVICE_TEST_FAILED')

asyncio.run(test_services())
"@

$serviceTest | python 2>&1 | ForEach-Object {
    if ($_ -match "✓") {
        Write-Host $_ -ForegroundColor Green
    } elseif ($_ -match "ℹ") {
        Write-Host $_ -ForegroundColor Cyan
    } elseif ($_ -match "✗") {
        Write-Host $_ -ForegroundColor Red
        $ErrorCount++
    } elseif ($_ -match "SERVICE_TEST_PASSED") {
        # Success indicator
    } elseif ($_ -match "SERVICE_TEST_FAILED") {
        $ErrorCount++
    } else {
        Write-Host $_ -ForegroundColor White
    }
}

# Test 11: Check medical books
Write-Host "`nTest 11: Checking medical knowledge base..." -ForegroundColor Yellow
$pdfFiles = Get-ChildItem -Path "data\medical_books" -Filter "*.pdf" -ErrorAction SilentlyContinue
if ($pdfFiles.Count -gt 0) {
    Write-Host "  ✓ Found $($pdfFiles.Count) medical PDF(s)" -ForegroundColor Green
    foreach ($pdf in $pdfFiles) {
        Write-Host "    - $($pdf.Name)" -ForegroundColor White
    }
} else {
    Write-Host "  ⚠ No medical PDFs found in data\medical_books\" -ForegroundColor Yellow
    Write-Host "    Add medical textbooks to enable knowledge base features" -ForegroundColor White
    $WarningCount++
}

# Test 12: Quick API test
Write-Host "`nTest 12: Testing API startup (quick check)..." -ForegroundColor Yellow
$apiTest = @"
import sys
sys.path.insert(0, '.')

try:
    from app.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get('/health')
    
    if response.status_code == 200:
        print('  ✓ API health check passed')
        print('API_TEST_PASSED')
    else:
        print(f'  ✗ API health check failed with status {response.status_code}')
        print('API_TEST_FAILED')
except Exception as e:
    print(f'  ✗ API test failed: {e}')
    print('API_TEST_FAILED')
"@

$apiTest | python 2>&1 | ForEach-Object {
    if ($_ -match "✓") {
        Write-Host $_ -ForegroundColor Green
    } elseif ($_ -match "✗") {
        Write-Host $_ -ForegroundColor Red
        $ErrorCount++
    } elseif ($_ -match "API_TEST_PASSED") {
        # Success indicator
    } elseif ($_ -match "API_TEST_FAILED") {
        $ErrorCount++
    } else {
        Write-Host $_ -ForegroundColor White
    }
}

# Summary
Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

if ($ErrorCount -eq 0 -and $WarningCount -eq 0) {
    Write-Host "✓ All tests passed! System is ready." -ForegroundColor Green
    Write-Host "`nTo start the server:" -ForegroundColor White
    Write-Host "  cd backend" -ForegroundColor Yellow
    Write-Host "  python run.py" -ForegroundColor Yellow
    Write-Host "`nThen visit: http://localhost:8000/docs" -ForegroundColor Cyan
} elseif ($ErrorCount -eq 0) {
    Write-Host "⚠ Tests passed with $WarningCount warning(s)" -ForegroundColor Yellow
    Write-Host "`nTo start the server:" -ForegroundColor White
    Write-Host "  cd backend" -ForegroundColor Yellow
    Write-Host "  python run.py" -ForegroundColor Yellow
} else {
    Write-Host "✗ Tests failed with $ErrorCount error(s) and $WarningCount warning(s)" -ForegroundColor Red
    Write-Host "`nPlease fix the errors above before starting the server." -ForegroundColor Yellow
    Write-Host "You may need to run: .\setup.ps1" -ForegroundColor Yellow
}

Write-Host ""

# Return to parent directory
Set-Location ..

# Exit with appropriate code
if ($ErrorCount -gt 0) {
    exit 1
} else {
    exit 0
}
