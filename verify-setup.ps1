#!/usr/bin/env pwsh
<#
.SYNOPSIS
Verification Checklist - APScheduler + Celery Setup

.DESCRIPTION
Verify all components are properly installed and configured.

.EXAMPLE
.\verify-setup.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

$Green = @{ ForegroundColor = "Green" }
$Red = @{ ForegroundColor = "Red" }
$Yellow = @{ ForegroundColor = "Yellow" }

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        APScheduler + Celery Setup Verification               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$RootDir = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RootDir "backend"
$passed = 0
$failed = 0

# Check 1: Backend directory
Write-Host "1. Checking backend directory..." -ForegroundColor Yellow
if (Test-Path $BackendDir) {
    Write-Host "   ✅ Backend directory found" @Green
    $passed++
} else {
    Write-Host "   ❌ Backend directory not found" @Red
    $failed++
}

# Check 2: Python
Write-Host "`n2. Checking Python installation..." -ForegroundColor Yellow
try {
    $PythonVer = python --version 2>&1
    Write-Host "   ✅ Python found: $PythonVer" @Green
    $passed++
} catch {
    Write-Host "   ❌ Python not found or not in PATH" @Red
    $failed++
}

# Check 3: Requirements file
Write-Host "`n3. Checking requirements.txt..." -ForegroundColor Yellow
$ReqFile = Join-Path $BackendDir "requirements.txt"
if (Test-Path $ReqFile) {
    $hasAPScheduler = Select-String -Path $ReqFile -Pattern "apscheduler" -Quiet
    $hasCelery = Select-String -Path $ReqFile -Pattern "celery" -Quiet
    $hasRedis = Select-String -Path $ReqFile -Pattern "redis" -Quiet
    
    if ($hasAPScheduler -and $hasCelery -and $hasRedis) {
        Write-Host "   ✅ All required packages in requirements.txt" @Green
        Write-Host "      ✓ apscheduler"
        Write-Host "      ✓ celery"
        Write-Host "      ✓ redis"
        $passed++
    } else {
        Write-Host "   ❌ Missing packages in requirements.txt" @Red
        if (-not $hasAPScheduler) { Write-Host "      ✗ apscheduler" }
        if (-not $hasCelery) { Write-Host "      ✗ celery" }
        if (-not $hasRedis) { Write-Host "      ✗ redis" }
        $failed++
    }
} else {
    Write-Host "   ❌ requirements.txt not found" @Red
    $failed++
}

# Check 4: Core files
Write-Host "`n4. Checking core implementation files..." -ForegroundColor Yellow
$FilesToCheck = @(
    @{ Path = "$BackendDir/celery_config.py"; Name = "celery_config.py" },
    @{ Path = "$BackendDir/app/tasks.py"; Name = "tasks.py" },
    @{ Path = "$BackendDir/kb_update_config.json"; Name = "kb_update_config.json" }
)

$filesOK = $true
foreach ($file in $FilesToCheck) {
    if (Test-Path $file.Path) {
        Write-Host "   ✅ $($file.Name)" @Green
    } else {
        Write-Host "   ❌ $($file.Name) not found" @Red
        $filesOK = $false
    }
}

if ($filesOK) { $passed++ } else { $failed++ }

# Check 5: PowerShell scripts
Write-Host "`n5. Checking startup scripts..." -ForegroundColor Yellow
$ScriptsToCheck = @(
    @{ Path = "$RootDir/start-celery-worker.ps1"; Name = "start-celery-worker.ps1" },
    @{ Path = "$RootDir/start-redis.ps1"; Name = "start-redis.ps1" },
    @{ Path = "$RootDir/start-flower.ps1"; Name = "start-flower.ps1" }
)

$scriptsOK = $true
foreach ($script in $ScriptsToCheck) {
    if (Test-Path $script.Path) {
        Write-Host "   ✅ $($script.Name)" @Green
    } else {
        Write-Host "   ❌ $($script.Name) not found" @Red
        $scriptsOK = $false
    }
}

if ($scriptsOK) { $passed++ } else { $failed++ }

# Check 6: Documentation
Write-Host "`n6. Checking documentation files..." -ForegroundColor Yellow
$DocsToCheck = @(
    @{ Path = "$RootDir/QUICK_START_APSCHEDULER_CELERY.md"; Name = "Quick Start Guide" },
    @{ Path = "$RootDir/APSCHEDULER_CELERY_SETUP_GUIDE.md"; Name = "Setup Guide" },
    @{ Path = "$RootDir/APSCHEDULER_CELERY_API_DOCS.md"; Name = "API Documentation" }
)

$docsOK = $true
foreach ($doc in $DocsToCheck) {
    if (Test-Path $doc.Path) {
        Write-Host "   ✅ $($doc.Name)" @Green
    } else {
        Write-Host "   ❌ $($doc.Name) not found" @Red
        $docsOK = $false
    }
}

if ($docsOK) { $passed++ } else { $failed++ }

# Check 7: Redis availability
Write-Host "`n7. Checking Redis (optional)..." -ForegroundColor Yellow
try {
    $RedisCheck = redis-cli ping 2>&1
    if ($RedisCheck -eq "PONG") {
        Write-Host "   ✅ Redis is running and accessible" @Green
        $passed++
    } else {
        Write-Host "   ⚠️  Redis not accessible (start with .\start-redis.ps1)" @Yellow
    }
} catch {
    Write-Host "   ⚠️  Redis not installed (optional, can use .\start-redis.ps1)" @Yellow
}

# Check 8: APScheduler integration in main.py
Write-Host "`n8. Checking APScheduler integration in main.py..." -ForegroundColor Yellow
$MainFile = Join-Path $BackendDir "app/main.py"
if (Test-Path $MainFile) {
    $hasScheduler = Select-String -Path $MainFile -Pattern "APScheduler|BackgroundScheduler" -Quiet
    if ($hasScheduler) {
        Write-Host "   ✅ APScheduler code found in main.py" @Green
        $passed++
    } else {
        Write-Host "   ❌ APScheduler not integrated in main.py" @Red
        $failed++
    }
} else {
    Write-Host "   ❌ main.py not found" @Red
    $failed++
}

# Summary
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                        VERIFICATION SUMMARY                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$total = $passed + $failed
Write-Host "✅ Passed: $passed" @Green
Write-Host "❌ Failed: $failed" @Red
Write-Host "📊 Total:  $total`n"

if ($failed -eq 0) {
    Write-Host "🎉 All checks passed! You're ready to go!" @Green
    Write-Host "`nNext steps:" @Yellow
    Write-Host "1. Read: QUICK_START_APSCHEDULER_CELERY.md"
    Write-Host "2. Run: pip install -r backend/requirements.txt"
    Write-Host "3. Start 4 terminals:"
    Write-Host "   - .\start-redis.ps1"
    Write-Host "   - .\start-backend.ps1"
    Write-Host "   - .\start-celery-worker.ps1"
    Write-Host "   - .\start-flower.ps1 (optional)"
} else {
    Write-Host "⚠️  Some checks failed. Please fix the issues above." @Red
    Write-Host "`nCommon solutions:" @Yellow
    Write-Host "- Missing packages: pip install -r requirements.txt"
    Write-Host "- Missing files: Check file creation completed successfully"
    Write-Host "- Python not found: Add Python to PATH or reinstall"
}

Write-Host ""
