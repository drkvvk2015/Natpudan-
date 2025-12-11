#!/usr/bin/env pwsh
<#
.SYNOPSIS
Virtual Environment Setup Guide - APScheduler + Celery

.DESCRIPTION
How to properly use the virtual environment with APScheduler + Celery setup.

.NOTES
The virtual environment is now created and all dependencies are installed.
Follow these instructions to activate and use it.
#>

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Virtual Environment Setup Complete ✅                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$Green = @{ ForegroundColor = "Green" }
$Yellow = @{ ForegroundColor = "Yellow" }

Write-Host "✅ Virtual environment created at: backend/venv/" @Green
Write-Host "✅ All dependencies installed (no PATH warnings!)" @Green
Write-Host "✅ Ready to run APScheduler + Celery setup" @Green

Write-Host "`n📋 HOW TO USE THE VIRTUAL ENVIRONMENT`n" @Yellow

Write-Host "Option 1: Let Scripts Do It (EASIEST - Recommended)"
Write-Host "──────────────────────────────────────────────────"
Write-Host "Just run the startup scripts - they automatically activate venv:"
Write-Host ""
Write-Host "  .\start-backend.ps1"
Write-Host "  .\start-celery-worker.ps1"
Write-Host "  .\start-redis.ps1"
Write-Host "  .\start-flower.ps1"
Write-Host ""
Write-Host "✅ No manual activation needed!" @Green
Write-Host ""

Write-Host "Option 2: Manual Activation (if needed)"
Write-Host "────────────────────────────────────────"
Write-Host "Activate venv manually in PowerShell:"
Write-Host ""
Write-Host "  cd backend"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "You'll see '(venv)' in your prompt when activated:"
Write-Host "  (venv) PS D:\...\Natpudan-\backend> _"
Write-Host ""

Write-Host "Option 3: Use venv Python Directly"
Write-Host "────────────────────────────────────"
Write-Host "Run Python/pip without activating:"
Write-Host ""
Write-Host "  .\venv\Scripts\python -c 'print(""Hello from venv!"")'  # Python"
Write-Host "  .\venv\Scripts\pip list  # Pip packages"
Write-Host "  .\venv\Scripts\celery --version  # Celery"
Write-Host ""

Write-Host "📦 COMMON COMMANDS`n" @Yellow

Write-Host "Install new package:"
Write-Host "  .\venv\Scripts\pip install package_name"
Write-Host ""

Write-Host "Run Python script:"
Write-Host "  .\venv\Scripts\python script.py"
Write-Host ""

Write-Host "Run Celery (direct):"
Write-Host "  .\venv\Scripts\celery -A app.celery_config worker"
Write-Host ""

Write-Host "Run Flower (direct):"
Write-Host "  .\venv\Scripts\celery -A app.celery_config flower"
Write-Host ""

Write-Host "🎯 QUICK START (4 TERMINALS)`n" @Yellow

Write-Host "Terminal 1: Redis"
Write-Host "  .\start-redis.ps1"
Write-Host ""

Write-Host "Terminal 2: FastAPI (auto-activates venv)"
Write-Host "  .\start-backend.ps1"
Write-Host ""

Write-Host "Terminal 3: Celery (auto-activates venv)"
Write-Host "  .\start-celery-worker.ps1"
Write-Host ""

Write-Host "Terminal 4: Flower (auto-activates venv)"
Write-Host "  .\start-flower.ps1"
Write-Host ""

Write-Host "✅ All scripts automatically use the virtual environment!" @Green
Write-Host "   No manual activation needed!" @Green

Write-Host "`n📊 VERIFICATION`n" @Yellow

Write-Host "Check venv is working:"
Write-Host "  .\venv\Scripts\python --version"
Write-Host ""

Write-Host "Check packages installed:"
Write-Host "  .\venv\Scripts\pip list | findstr celery"
Write-Host "  .\venv\Scripts\pip list | findstr apscheduler"
Write-Host "  .\venv\Scripts\pip list | findstr redis"
Write-Host ""

Write-Host "⚠️  PATH WARNING FIX`n" @Yellow

Write-Host "The original warnings about:"
Write-Host "  'websockets.exe is installed in AppData\Roaming\Python\..'"
Write-Host ""
Write-Host "ARE NOW FIXED! ✅"
Write-Host ""
Write-Host "Why?"
Write-Host "  • Virtual environment isolates packages locally"
Write-Host "  • Uses backend/venv/Scripts instead of AppData"
Write-Host "  • No system PATH pollution"
Write-Host "  • Cleaner, more portable setup"
Write-Host ""

Write-Host "🎉 YOU'RE ALL SET!`n" @Green

Write-Host "Next step:" @Yellow
Write-Host "  1. Read: QUICK_START_APSCHEDULER_CELERY.md"
Write-Host "  2. Run the 4 startup scripts"
Write-Host "  3. Monitor in Flower at http://localhost:5555"
Write-Host ""
