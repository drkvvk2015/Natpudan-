<#
Deploy Natpudan AI Medical Assistant in production (Windows)
Prerequisites: Docker Desktop, docker compose v2, valid .env file with secrets
This script now auto-detects the Docker CLI path and fails fast if compose fails.
#>

Param(
    [string]$EnvFile = ".env",
    [switch]$Recreate,
    [switch]$Pull
)

$ErrorActionPreference = "Stop"

function Get-DockerCmd {
    # Try PATH first
    $cmd = (Get-Command docker -ErrorAction SilentlyContinue).Path
    if ($cmd) { return $cmd }
    # Common Docker Desktop locations
    $candidates = @(
        "C:\Program Files\Docker\Docker\resources\bin\docker.exe",
        "C:\Program Files\Docker\Docker\resources\bin\com.docker.cli.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    throw "Docker CLI not found. Ensure Docker Desktop is installed and the CLI is available."
}

$DockerCmd = Get-DockerCmd

Write-Host "[Deploy] Starting production deployment..." -ForegroundColor Cyan

if (-not (Test-Path $EnvFile)) {
    Write-Error "Env file '$EnvFile' not found. Please create it based on .env.sample."
}

# Optionally pull latest images
if ($Pull) {
    Write-Host "[Deploy] Pulling images..." -ForegroundColor Cyan
    & $DockerCmd compose --env-file $EnvFile pull
    if ($LASTEXITCODE -ne 0) { throw "docker compose pull failed (exit $LASTEXITCODE)" }
}

# Bring up the stack
if ($Recreate) {
    Write-Host "[Deploy] Recreating containers..." -ForegroundColor Cyan
    & $DockerCmd compose --env-file $EnvFile up -d --force-recreate
    if ($LASTEXITCODE -ne 0) { throw "docker compose up failed (exit $LASTEXITCODE)" }
} else {
    & $DockerCmd compose --env-file $EnvFile up -d
    if ($LASTEXITCODE -ne 0) { throw "docker compose up failed (exit $LASTEXITCODE)" }
}

# Wait for backend health
Write-Host "[Deploy] Waiting for backend health..." -ForegroundColor Cyan
$maxAttempts = 20
$attempt = 0
while ($attempt -lt $maxAttempts) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
        if ($resp.StatusCode -eq 200) {
            Write-Host "[Deploy] Backend healthy" -ForegroundColor Green
            break
        }
    } catch {
        Start-Sleep -Seconds 3
    }
    $attempt++
}

if ($attempt -ge $maxAttempts) {
    Write-Warning "[Deploy] Backend health check failed. Check logs with: docker compose logs backend"
}

Write-Host "[Deploy] Done." -ForegroundColor Green
