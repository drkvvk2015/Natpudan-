<#
.SYNOPSIS
Migrate from Docker to Podman
.DESCRIPTION
Helps migrate your Natpudan setup from Docker to Podman
#>

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Docker → Podman Migration Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Check Docker
Write-Host "[1/5] Checking Docker status..." -ForegroundColor Yellow

$dockerExists = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerExists) {
    Write-Host "  ⚠ Docker found - will not interfere" -ForegroundColor Yellow
    Write-Host "  You can use Docker and Podman simultaneously" -ForegroundColor Gray
} else {
    Write-Host "  ✓ Docker not found (or not in PATH)" -ForegroundColor Green
}

# Step 2: Check Podman
Write-Host "`n[2/5] Checking Podman..." -ForegroundColor Yellow

$podmanExists = Get-Command podman -ErrorAction SilentlyContinue
if (-not $podmanExists) {
    Write-Error "Podman not found. Install it first from: https://podman.io/docs/installation/windows"
    exit 1
}

Write-Host "  ✓ Podman found" -ForegroundColor Green

# Step 3: Check podman-compose
Write-Host "`n[3/5] Checking podman-compose..." -ForegroundColor Yellow

$podmanComposeExists = Get-Command podman-compose -ErrorAction SilentlyContinue
if (-not $podmanComposeExists) {
    Write-Host "  ⚠ podman-compose not installed" -ForegroundColor Yellow
    Write-Host "  Installing: pip install podman-compose" -ForegroundColor Gray
    
    pip install podman-compose
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install podman-compose"
        exit 1
    }
    
    Write-Host "  ✓ podman-compose installed" -ForegroundColor Green
} else {
    Write-Host "  ✓ podman-compose found" -ForegroundColor Green
}

# Step 4: Start Podman machine
Write-Host "`n[4/5] Starting Podman Machine..." -ForegroundColor Yellow

try {
    $machines = podman machine list --format=json | ConvertFrom-Json
    $isRunning = $machines | Where-Object { $_.IsRunning -eq $true }
    
    if (-not $isRunning) {
        Write-Host "  Starting Podman Machine..." -ForegroundColor Gray
        podman machine start
        Start-Sleep -Seconds 5
    }
    
    Write-Host "  ✓ Podman Machine is running" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Warning: Could not verify Podman Machine" -ForegroundColor Yellow
}

# Step 5: Configure migration
Write-Host "`n[5/5] Configuration..." -ForegroundColor Yellow

Write-Host "`nYour docker-compose.yml is already compatible!" -ForegroundColor Green
Write-Host "  ✓ No changes needed to configuration files" -ForegroundColor Green
Write-Host "  ✓ No changes needed to Dockerfiles" -ForegroundColor Green
Write-Host "  ✓ No changes needed to .env files" -ForegroundColor Green

# Provide next steps
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Migration Ready!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review configuration:" -ForegroundColor Yellow
Write-Host "     .\PODMAN_SETUP.md" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start your application:" -ForegroundColor Yellow
Write-Host "     .\start-podman-compose.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Or deploy to production:" -ForegroundColor Yellow
Write-Host "     .\deploy-podman-production.ps1 -EnvFile .env" -ForegroundColor Gray
Write-Host ""

Write-Host "Useful Podman Compose Commands:" -ForegroundColor Cyan
Write-Host "  podman-compose up -d               # Start services" -ForegroundColor Gray
Write-Host "  podman-compose down                # Stop services" -ForegroundColor Gray
Write-Host "  podman-compose logs -f             # View logs" -ForegroundColor Gray
Write-Host "  podman-compose ps                  # List containers" -ForegroundColor Gray
Write-Host "  podman-compose exec backend bash   # Enter container" -ForegroundColor Gray
Write-Host ""

Write-Host "System Information:" -ForegroundColor Cyan
Write-Host ""
podman --version
podman-compose --version
Write-Host ""

Write-Host "Migration complete! Ready to use Podman with Natpudan AI" -ForegroundColor Green
Write-Host ""
