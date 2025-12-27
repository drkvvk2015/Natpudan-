<#
.SYNOPSIS
Utility functions for Podman operations
.DESCRIPTION
Common Podman helper functions for the Natpudan project
#>

function Start-PodmanMachine {
    <#
    .SYNOPSIS
    Start Podman machine (required on Windows/Mac)
    #>
    Write-Host "[Podman] Starting Podman Machine..." -ForegroundColor Cyan
    
    try {
        $machines = podman machine list --format=json | ConvertFrom-Json
        $isRunning = $machines | Where-Object { $_.IsRunning -eq $true }
        
        if ($isRunning) {
            Write-Host "[Podman] ✓ Podman Machine already running" -ForegroundColor Green
            return $true
        }
        
        podman machine start
        Start-Sleep -Seconds 3
        
        Write-Host "[Podman] ✓ Podman Machine started" -ForegroundColor Green
        return $true
    } catch {
        Write-Error "[Podman] Failed to start machine: $_"
        return $false
    }
}

function Stop-PodmanMachine {
    <#
    .SYNOPSIS
    Stop Podman machine
    #>
    Write-Host "[Podman] Stopping Podman Machine..." -ForegroundColor Cyan
    
    try {
        podman machine stop
        Write-Host "[Podman] ✓ Podman Machine stopped" -ForegroundColor Green
        return $true
    } catch {
        Write-Error "[Podman] Failed to stop machine: $_"
        return $false
    }
}

function Get-PodmanStatus {
    <#
    .SYNOPSIS
    Check Podman system status
    #>
    Write-Host "[Podman] System Status:" -ForegroundColor Cyan
    
    try {
        podman info
    } catch {
        Write-Error "[Podman] Failed to get status: $_"
    }
}

function Test-PodmanHealth {
    <#
    .SYNOPSIS
    Test Podman installation and machine status
    #>
    Write-Host "[Podman] Testing Podman health..." -ForegroundColor Cyan
    
    # Check podman command
    if (-not (Get-Command podman -ErrorAction SilentlyContinue)) {
        Write-Error "[Podman] Podman command not found"
        return $false
    }
    Write-Host "[Podman] ✓ Podman installed" -ForegroundColor Green
    
    # Check podman-compose
    if (-not (Get-Command podman-compose -ErrorAction SilentlyContinue)) {
        Write-Error "[Podman] podman-compose not found"
        return $false
    }
    Write-Host "[Podman] ✓ podman-compose installed" -ForegroundColor Green
    
    # Check machine
    try {
        $machines = podman machine list --format=json | ConvertFrom-Json
        $isRunning = $machines | Where-Object { $_.IsRunning -eq $true }
        
        if (-not $isRunning) {
            Write-Warning "[Podman] ⚠ No Podman machines running"
            return $false
        }
        Write-Host "[Podman] ✓ Podman machine running" -ForegroundColor Green
        return $true
    } catch {
        Write-Error "[Podman] Failed to check machines: $_"
        return $false
    }
}

function Clear-PodmanResources {
    <#
    .SYNOPSIS
    Clean up unused Podman resources
    #>
    Write-Host "[Podman] Cleaning up unused resources..." -ForegroundColor Cyan
    
    try {
        podman system prune -a --volumes -f
        Write-Host "[Podman] ✓ Resources cleaned" -ForegroundColor Green
    } catch {
        Write-Error "[Podman] Failed to clean resources: $_"
    }
}

function Get-ContainerLogs {
    <#
    .SYNOPSIS
    Get logs from a specific container
    .PARAMETER ContainerName
    Name of the container
    .PARAMETER Lines
    Number of lines to show (default: 50)
    .PARAMETER Follow
    Follow log output
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$ContainerName,
        
        [int]$Lines = 50,
        
        [switch]$Follow
    )
    
    $args = @("logs", "--tail", $Lines)
    if ($Follow) { $args += "-f" }
    $args += $ContainerName
    
    & podman $args
}

function Invoke-ContainerCommand {
    <#
    .SYNOPSIS
    Execute a command in a running container
    .PARAMETER ContainerName
    Name of the container
    .PARAMETER Command
    Command to execute
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$ContainerName,
        
        [Parameter(Mandatory=$true)]
        [string]$Command
    )
    
    & podman exec -it $ContainerName /bin/sh -c $Command
}

function Get-NatpudanContainers {
    <#
    .SYNOPSIS
    List all Natpudan containers
    #>
    Write-Host "[Podman] Natpudan Containers:" -ForegroundColor Cyan
    
    podman ps -a --filter "name=physician-ai"
}

function Get-ServiceStatus {
    <#
    .SYNOPSIS
    Get status of all services in docker-compose
    .PARAMETER EnvFile
    Path to environment file (default: .env)
    #>
    param(
        [string]$EnvFile = ".env"
    )
    
    Write-Host "[Podman] Service Status:" -ForegroundColor Cyan
    
    if (-not (Test-Path $EnvFile)) {
        Write-Error "Environment file '$EnvFile' not found"
        return
    }
    
    podman-compose --env-file $EnvFile ps
}

function Restart-Services {
    <#
    .SYNOPSIS
    Restart all services
    .PARAMETER EnvFile
    Path to environment file (default: .env)
    #>
    param(
        [string]$EnvFile = ".env"
    )
    
    Write-Host "[Podman] Restarting services..." -ForegroundColor Cyan
    
    if (-not (Test-Path $EnvFile)) {
        Write-Error "Environment file '$EnvFile' not found"
        return
    }
    
    podman-compose --env-file $EnvFile restart
    Write-Host "[Podman] ✓ Services restarted" -ForegroundColor Green
}

function Backup-Database {
    <#
    .SYNOPSIS
    Backup PostgreSQL database
    .PARAMETER BackupPath
    Directory to save backup
    #>
    param(
        [string]$BackupPath = "./backups"
    )
    
    Write-Host "[Podman] Backing up database..." -ForegroundColor Cyan
    
    if (-not (Test-Path $BackupPath)) {
        New-Item -ItemType Directory -Path $BackupPath | Out-Null
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = Join-Path $BackupPath "physician_ai_$timestamp.sql"
    
    try {
        podman exec physician-ai-db pg_dump -U physician_user physician_ai > $backupFile
        Write-Host "[Podman] ✓ Database backed up to $backupFile" -ForegroundColor Green
    } catch {
        Write-Error "[Podman] Failed to backup database: $_"
    }
}

Export-ModuleMember -Function @(
    'Start-PodmanMachine',
    'Stop-PodmanMachine',
    'Get-PodmanStatus',
    'Test-PodmanHealth',
    'Clear-PodmanResources',
    'Get-ContainerLogs',
    'Invoke-ContainerCommand',
    'Get-NatpudanContainers',
    'Get-ServiceStatus',
    'Restart-Services',
    'Backup-Database'
)
