<#
.SYNOPSIS
Connects to the internal shell of a running Podman container (SSH-like experience).
.DESCRIPTION
This script starts an interactive shell session (/bin/bash or /bin/sh) inside the specified container.
Default container is the backend API.
.PARAMETER Container
The name of the service to connect to (backend, redis, db, frontend).
.EXAMPLE
.\connect-ssh.ps1
.EXAMPLE
.\connect-ssh.ps1 -Container redis
#>

param(
    [ValidateSet("backend", "redis", "db", "frontend", "celery", "nginx")]
    [string]$Container = "backend"
)

$ErrorActionPreference = "Stop"

# Map friendly names to actual container names
$containerMap = @{
    "backend"  = "physician-ai-backend"
    "redis"    = "physician-ai-redis"
    "db"       = "physician-ai-db"
    "frontend" = "physician-ai-frontend"
    "celery"   = "physician-ai-celery"
    "nginx"    = "physician-ai-nginx"
}

$targetContainer = $containerMap[$Container]

Write-Host "Connecting to $Container ($targetContainer)..." -ForegroundColor Cyan
Write-Host "Type 'exit' to close the session." -ForegroundColor Gray

# Check if running
$status = podman inspect -f '{{.State.Running}}' $targetContainer 2>$null
if ($status -ne "true") {
    Write-Host "Container '$targetContainer' is not running." -ForegroundColor Yellow
    Write-Host "Available containers:" -ForegroundColor Cyan
    podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    exit 1
}

# Try bash, fall back to sh
Write-Host "Connecting to $targetContainer shell..." -ForegroundColor Cyan
try {
    podman exec -it $targetContainer /bin/bash
} catch {
    Write-Warning "Bash not found, falling back to sh..."
    podman exec -it $targetContainer /bin/sh
}
