#!/usr/bin/env pwsh
<#
.SYNOPSIS
Phase 6 Setup - Download and configure Ollama + LLaMA

.DESCRIPTION
Automates Ollama installation and model setup for local LLM inference.

.NOTES
Requires: PowerShell 5.1+, Internet connection
#>

param(
    [switch]$DownloadOnly = $false,
    [string]$Model = "llama2",
    [switch]$StartService = $true
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Phase 6 Setup - Ollama Local LLM Configuration        ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

function Test-Ollama {
    $ollama_cmd = Get-Command ollama -ErrorAction SilentlyContinue
    return $null -ne $ollama_cmd
}

function Install-Ollama {
    Write-Host "[STEP 1] Installing Ollama..." -ForegroundColor Yellow
    
    if (Test-Ollama) {
        Write-Host "✓ Ollama already installed" -ForegroundColor Green
        ollama --version
        return $true
    }
    
    Write-Host "Ollama not found. Installation options:" -ForegroundColor Yellow
    Write-Host "  1. macOS: brew install ollama"
    Write-Host "  2. Linux: curl https://ollama.ai/install.sh | sh"
    Write-Host "  3. Windows: Download installer from https://ollama.ai"
    Write-Host "`nPlease install Ollama and run this script again." -ForegroundColor Magenta
    
    return $false
}

function Download-Model {
    param(
        [string]$ModelName
    )
    
    Write-Host "`n[STEP 2] Downloading $ModelName model..." -ForegroundColor Yellow
    
    # Check if model already exists
    $models_output = & ollama list 2>&1
    if ($models_output -match $ModelName) {
        Write-Host "✓ Model $ModelName already downloaded" -ForegroundColor Green
        return $true
    }
    
    Write-Host "Downloading $ModelName (this may take 5-10 minutes, ~5GB)..." -ForegroundColor Cyan
    
    try {
        & ollama pull $ModelName
        Write-Host "✓ Model $ModelName downloaded successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Failed to download model: $_" -ForegroundColor Red
        return $false
    }
}

function Start-Ollama {
    Write-Host "`n[STEP 3] Starting Ollama service..." -ForegroundColor Yellow
    
    # Check if already running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Ollama already running on localhost:11434" -ForegroundColor Green
            return $true
        }
    }
    catch { }
    
    Write-Host "Starting Ollama service..." -ForegroundColor Cyan
    
    # Start in background
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden -PassThru | Out-Null
    
    # Wait for service to start
    Write-Host "Waiting for Ollama to start..." -ForegroundColor Yellow
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✓ Ollama service started" -ForegroundColor Green
                return $true
            }
        }
        catch { }
    }
    
    Write-Host "✗ Ollama service failed to start" -ForegroundColor Red
    return $false
}

function List-Models {
    Write-Host "`n[INFO] Available Ollama models:" -ForegroundColor Cyan
    & ollama list
}

function Test-Backend {
    Write-Host "`n[STEP 4] Testing backend connection..." -ForegroundColor Yellow
    
    $test_script = @"
import asyncio
from app.services.phase_6_services.ollama_client import OllamaClient

async def test():
    client = OllamaClient()
    await client.initialize()
    available = await client.is_available()
    models = await client.list_models()
    await client.close()
    return available, models

result = asyncio.run(test())
print(f"Ollama available: {result[0]}")
print(f"Models: {result[1]}")
"@
    
    try {
        Write-Host "Testing connection to Phase 6 endpoints..." -ForegroundColor Cyan
        
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/phase-6/health" `
            -ErrorAction SilentlyContinue
        
        if ($response.StatusCode -eq 200) {
            $data = $response.Content | ConvertFrom-Json
            Write-Host "✓ Phase 6 health: $($data.status)" -ForegroundColor Green
            Write-Host "✓ Ollama available: $($data.ollama_available)" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "✗ Backend not responding (start backend server first)" -ForegroundColor Yellow
        Write-Host "   Run: .\start-dev.ps1 or .\start-backend.ps1" -ForegroundColor Yellow
    }
}

# Main execution
try {
    # Check Ollama installation
    if (-not (Install-Ollama)) {
        exit 1
    }
    
    # Download model
    if (-not $DownloadOnly) {
        if (-not (Download-Model -ModelName $Model)) {
            Write-Host "`n⚠ Model download failed, but you can retry later" -ForegroundColor Yellow
        }
    }
    else {
        Download-Model -ModelName $Model
        exit 0
    }
    
    # Start service
    if ($StartService) {
        if (-not (Start-Ollama)) {
            Write-Host "`n⚠ Failed to start Ollama. Try running: ollama serve" -ForegroundColor Yellow
        }
    }
    
    # List models
    List-Models
    
    # Test backend
    Test-Backend
    
    # Summary
    Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   Phase 6 Setup Complete!                                ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "  1. Start backend server: .\start-dev.ps1"
    Write-Host "  2. Test endpoints:"
    Write-Host "     GET  http://localhost:8000/api/phase-6/health"
    Write-Host "     POST http://localhost:8000/api/phase-6/chat"
    Write-Host "  3. Try a medical query"
    
    Write-Host "`nOllama Commands:" -ForegroundColor Cyan
    Write-Host "  ollama list           # Show downloaded models"
    Write-Host "  ollama pull llama2    # Download a model"
    Write-Host "  ollama show llama2    # Show model details"
    Write-Host "  ollama serve          # Start service (done)"
    
    Write-Host "`nAPI Examples:" -ForegroundColor Cyan
    Write-Host "  curl http://localhost:8000/api/phase-6/setup-guide"
    Write-Host "  curl http://localhost:8000/api/phase-6/roadmap"
    
}
catch {
    Write-Host "`n✗ Setup failed: $_" -ForegroundColor Red
    exit 1
}
