#!/usr/bin/env pwsh
# Podman Compose Helper Script
# Usage: .\podman-compose.ps1 [command] [args...]
# Examples:
#   .\podman-compose.ps1 up -d          # Start all services
#   .\podman-compose.ps1 down           # Stop all services
#   .\podman-compose.ps1 ps             # List containers
#   .\podman-compose.ps1 logs backend   # View backend logs

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

Write-Host "🐳 Running Podman Compose..." -ForegroundColor Cyan
Write-Host "Command: python -m podman_compose $($Arguments -join ' ')" -ForegroundColor Gray
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Warning ".env file not found! Creating from .env.example..."
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file. Please update with your settings." -ForegroundColor Green
    } else {
        Write-Error "❌ .env.example not found. Please create .env manually."
        exit 1
    }
}

# Run podman-compose
try {
    python -m podman_compose @Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Podman Compose failed with exit code: $LASTEXITCODE"
        exit $LASTEXITCODE
    }
} catch {
    Write-Error "❌ Error running podman-compose: $_"
    exit 1
}

Write-Host ""
Write-Host "✅ Command completed successfully!" -ForegroundColor Green
