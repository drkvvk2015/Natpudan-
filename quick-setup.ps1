# Quick Manual Setup Script
# Use this if setup.ps1 is stuck

Write-Host "Quick Setup - Creating Virtual Environment" -ForegroundColor Cyan
Write-Host ""

# Go to backend
if (-not (Test-Path "backend")) {
    New-Item -ItemType Directory -Path "backend" -Force | Out-Null
}

Set-Location backend

# Create venv with verbose output
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
Write-Host "(This may take 1-2 minutes, please wait...)" -ForegroundColor White

python -m venv venv --clear

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Virtual environment created!" -ForegroundColor Green
}
else {
    Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

Set-Location ..
Write-Host ""
Write-Host "Done! Now run: .\setup.ps1" -ForegroundColor Green
