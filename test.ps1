# Test Script for Physician AI Assistant
# Run this after setup to verify everything works

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Physician AI Assistant - System Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = Join-Path $PSScriptRoot "backend"
Set-Location $backendPath

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path "venv" "Scripts" "Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
}
else {
    Write-Host "ERROR: Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

$allPassed = $true

# Test 1: Import core modules
Write-Host ""
Write-Host "Test 1: Checking Python modules..." -ForegroundColor Yellow
$imports = @"
import sys
try:
    import fastapi
    import uvicorn
    import fitz
    import chromadb
    import sentence_transformers
    import openai
    print('✓ All core modules imported successfully')
except Exception as e:
    print(f'✗ Import error: {str(e)}')
    sys.exit(1)
"@

python -c $imports
if ($LASTEXITCODE -eq 0) {
    Write-Host "   PASSED" -ForegroundColor Green
}
else {
    Write-Host "   FAILED" -ForegroundColor Red
    $allPassed = $false
}

# Test 2: Database initialization
Write-Host ""
Write-Host "Test 2: Testing database..." -ForegroundColor Yellow
$dbTest = @"
from app.database.schemas import init_db
from app.database.connection import test_connection
try:
    if test_connection():
        print('✓ Database connection successful')
    init_db()
    print('✓ Database tables created')
except Exception as e:
    print(f'✗ Database error: {str(e)}')
"@

python -c $dbTest
if ($LASTEXITCODE -eq 0) {
    Write-Host "   PASSED" -ForegroundColor Green
}
else {
    Write-Host "   FAILED" -ForegroundColor Red
    $allPassed = $false
}

# Test 3: Knowledge Base
Write-Host ""
Write-Host "Test 3: Testing Knowledge Base..." -ForegroundColor Yellow
$kbTest = @"
import asyncio
from app.services.knowledge_base import KnowledgeBase
try:
    async def test():
        kb = KnowledgeBase()
        await kb.initialize()
        stats = kb.get_statistics()
        print(f'✓ Knowledge Base initialized')
        print(f'  Documents: {stats.get(\"total_documents\", 0)}')
        print(f'  Processed files: {stats.get(\"processed_files\", 0)}')
        await kb.close()
    asyncio.run(test())
except Exception as e:
    print(f'✗ Knowledge Base error: {str(e)}')
"@

python -c $kbTest
if ($LASTEXITCODE -eq 0) {
    Write-Host "   PASSED" -ForegroundColor Green
}
else {
    Write-Host "   FAILED" -ForegroundColor Red
    $allPassed = $false
}

# Test 4: LLM Service
Write-Host ""
Write-Host "Test 4: Testing LLM Service..." -ForegroundColor Yellow
$llmTest = @"
import asyncio
from app.services.llm_service import LLMService
try:
    async def test():
        llm = LLMService()
        await llm.initialize()
        if llm.use_local_fallback:
            print('⚠ LLM running in fallback mode (no API key)')
        else:
            print('✓ LLM Service initialized with OpenAI')
    asyncio.run(test())
except Exception as e:
    print(f'✗ LLM Service error: {str(e)}')
"@

python -c $llmTest
if ($LASTEXITCODE -eq 0) {
    Write-Host "   PASSED (check warnings)" -ForegroundColor Green
}
else {
    Write-Host "   FAILED" -ForegroundColor Red
    $allPassed = $false
}

# Test 5: API Server (quick test)
Write-Host ""
Write-Host "Test 5: Testing API..." -ForegroundColor Yellow
Write-Host "   Starting server (5 seconds)..." -ForegroundColor Cyan

# Start server in background
$serverJob = Start-Job -ScriptBlock {
    Set-Location $using:backendPath
    & "venv/Scripts/Activate.ps1"
    python run.py
}

Start-Sleep -Seconds 5

# Test health endpoint
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ API server responding" -ForegroundColor Green
        Write-Host "   PASSED" -ForegroundColor Green
        $content = $response.Content | ConvertFrom-Json
        Write-Host "   Status: $($content.status)" -ForegroundColor Cyan
    }
}
catch {
    Write-Host "   ✗ API server not responding" -ForegroundColor Red
    Write-Host "   FAILED" -ForegroundColor Red
    $allPassed = $false
}

# Stop server
Stop-Job -Job $serverJob
Remove-Job -Job $serverJob

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "All Tests PASSED! ✓" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your Physician AI Assistant is ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start the server:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor White
    Write-Host "  python run.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Then visit:" -ForegroundColor Yellow
    Write-Host "  http://localhost:8000/docs" -ForegroundColor White
}
else {
    Write-Host "Some Tests FAILED ✗" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the errors above and:" -ForegroundColor Yellow
    Write-Host "1. Ensure all dependencies are installed" -ForegroundColor White
    Write-Host "2. Check your .env configuration" -ForegroundColor White
    Write-Host "3. Review logs in backend/physician_ai.log" -ForegroundColor White
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
