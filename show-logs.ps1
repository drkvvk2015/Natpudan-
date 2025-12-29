<#
.SYNOPSIS
View logs for Natpudan containers.
.DESCRIPTION
Workaround for Podman on Windows where 'podman-compose logs -f' fails for multiple containers.
.PARAMETER Container
The service to view logs for (backend, frontend, db, redis, celery, flower).
#>

param(
    [ValidateSet("backend", "frontend", "db", "redis", "celery", "flower", "nginx")]
    [string]$Container = "backend",
    
    [switch]$Follow
)

$containerMap = @{
    "backend"  = "physician-ai-backend"
    "frontend" = "physician-ai-frontend"
    "db"       = "physician-ai-db"
    "redis"    = "physician-ai-redis"
    "celery"   = "physician-ai-celery"
    "flower"   = "physician-ai-flower"
    "nginx"    = "physician-ai-nginx"
}

$target = $containerMap[$Container]

Write-Host "--- Viewing Logs for $Container ($target) ---" -ForegroundColor Cyan

$args = @("logs", "--tail", "100")
if ($Follow) { $args += "-f" }
$args += $target

podman $args
