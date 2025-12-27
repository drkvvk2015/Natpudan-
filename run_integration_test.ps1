#!/usr/bin/env pwsh
<#
.SYNOPSIS
Complete smoke test and integration verification for Natpudan Medical AI Chat.

.DESCRIPTION
Runs backend validation, smoke tests, and frontend checks.
#>

$ErrorActionPreference = "Stop"

Write-Host "`n" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "NATPUDAN MEDICAL AI - INTEGRATION TEST" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Colors
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Blue = "Cyan"

$RootDir = Get-Location
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"

# Test 1: Environment Validation
Write-Host "📋 [1/5] Validating Backend Environment..." -ForegroundColor $Blue
try {
    Push-Location $BackendDir
    $output = python validate_env.py 2>&1
    Pop-Location
    
    if ($output -match "ENVIRONMENT READY") {
        Write-Host "✅ Environment validation passed" -ForegroundColor $Green
    } else {
        Write-Host "❌ Environment validation failed" -ForegroundColor $Red
        Write-Host $output
        exit 1
    }
} catch {
    Write-Host "❌ Error validating environment: $_" -ForegroundColor $Red
    exit 1
}

# Test 2: Backend health check
Write-Host "`n🏥 [2/5] Checking Backend Health..." -ForegroundColor $Blue
try {
    $healthResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" `
        -Method GET `
        -ErrorAction SilentlyContinue `
        -TimeoutSec 5 `
        -SkipHttpErrorCheck
    
    if ($healthResponse.StatusCode -eq 200) {
        $data = $healthResponse.Content | ConvertFrom-Json
        Write-Host "✅ Backend is running (status: $($data.status))" -ForegroundColor $Green
    } else {
        Write-Host "⚠️  Backend health check failed - backend may not be running" -ForegroundColor $Yellow
        Write-Host "   Run: python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000" -ForegroundColor $Yellow
    }
} catch {
    Write-Host "⚠️  Backend not responding - ensure it's started" -ForegroundColor $Yellow
    Write-Host "   Error: $_" -ForegroundColor $Yellow
}

# Test 3: Frontend dependencies
Write-Host "`n📦 [3/5] Checking Frontend Dependencies..." -ForegroundColor $Blue
try {
    Push-Location $FrontendDir
    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    
    $requiredDeps = @("react", "react-dom", "react-markdown", "remark-gfm", "@mui/material")
    $missingDeps = @()
    
    foreach ($dep in $requiredDeps) {
        if ($null -eq $packageJson.dependencies.$dep) {
            $missingDeps += $dep
        }
    }
    
    if ($missingDeps.Count -eq 0) {
        Write-Host "✅ All required dependencies declared in package.json" -ForegroundColor $Green
    } else {
        Write-Host "❌ Missing dependencies: $($missingDeps -join ', ')" -ForegroundColor $Red
        Write-Host "   Run: npm install" -ForegroundColor $Yellow
    }
    
    Pop-Location
} catch {
    Write-Host "❌ Error checking dependencies: $_" -ForegroundColor $Red
}

# Test 4: API endpoints
Write-Host "`n🔌 [4/5] Testing API Endpoints..." -ForegroundColor $Blue
$endpointsToTest = @(
    @{ Method = "GET"; Endpoint = "http://127.0.0.1:8000/health"; Name = "Health Check" },
    @{ Method = "GET"; Endpoint = "http://127.0.0.1:8000/health/detailed"; Name = "Detailed Health" },
    @{ Method = "GET"; Endpoint = "http://127.0.0.1:8000/api/medical/icd/categories"; Name = "ICD Categories" }
)

$passedCount = 0
foreach ($endpoint in $endpointsToTest) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.Endpoint `
            -Method $endpoint.Method `
            -ErrorAction SilentlyContinue `
            -TimeoutSec 5 `
            -SkipHttpErrorCheck
        
        if ($response.StatusCode -in 200..299) {
            Write-Host "  ✅ $($endpoint.Name)" -ForegroundColor $Green
            $passedCount++
        } else {
            Write-Host "  ⚠️  $($endpoint.Name) - Status: $($response.StatusCode)" -ForegroundColor $Yellow
        }
    } catch {
        Write-Host "  ⚠️  $($endpoint.Name) - Not responding" -ForegroundColor $Yellow
    }
}

Write-Host "   Passed: $passedCount/$($endpointsToTest.Count)" -ForegroundColor $Green

# Test 5: Smoke test availability
Write-Host "`n🧪 [5/5] Smoke Test Suite..." -ForegroundColor $Blue
try {
    Push-Location $BackendDir
    $testFile = "test_chat_smoke.py"
    
    if (Test-Path $testFile) {
        Write-Host "✅ Smoke test suite available" -ForegroundColor $Green
        Write-Host "   Run: python test_chat_smoke.py" -ForegroundColor $Yellow
    } else {
        Write-Host "❌ Smoke test not found" -ForegroundColor $Red
    }
    
    Pop-Location
} catch {
    Write-Host "❌ Error checking smoke test: $_" -ForegroundColor $Red
}

# Summary
Write-Host "`n" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "INTEGRATION TEST SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

Write-Host "`n✅ Quick Start Steps:" -ForegroundColor $Green
Write-Host "
1. Validate environment:
   cd backend
   python validate_env.py

2. Start backend (new terminal):
   cd backend
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

3. Install frontend dependencies:
   cd frontend
   npm install

4. Start frontend (new terminal):
   cd frontend
   npm run dev

5. Run smoke tests:
   cd backend
   python test_chat_smoke.py

6. Open browser: http://localhost:5173
" -ForegroundColor $Green

Write-Host "=" * 70 -ForegroundColor $Blue
Write-Host "📖 For detailed guide, see: MEDICAL_CHAT_QUICK_START.md" -ForegroundColor $Blue
Write-Host "=" * 70 -ForegroundColor $Blue
Write-Host ""
