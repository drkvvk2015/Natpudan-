# Quick Diagnostic Script for Natpudan AI Debug Setup
# Run this to check the health of all services

param(
    [switch]$Fix = $false,    # Auto-fix issues where possible
    [switch]$Verbose = $false  # Show detailed output
)

# ============================================================================
# CONFIGURATION
# ============================================================================
$global:RootDir = "D:\Users\CNSHO\Documents\GitHub\Natpudan-"
$global:BackendDir = Join-Path $global:RootDir "backend"

# Colors
$Colors = @{
    "Success"  = "Green"
    "Error"    = "Red"
    "Warning"  = "Yellow"
    "Info"     = "Cyan"
    "Debug"    = "Magenta"
}

# ============================================================================
# FUNCTIONS
# ============================================================================

function Write-Status {
    param([string]$Message, [string]$Type = "Info", [string]$Icon = "")
    if ($Icon) {
        Write-Host "[$Icon] $Message" -ForegroundColor $Colors[$Type]
    } else {
        Write-Host "$Message" -ForegroundColor $Colors[$Type]
    }
}

function Test-Port {
    param([int]$Port)
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("127.0.0.1", $Port)
        $tcp.Close()
        return $true
    } catch {
        return $false
    }
}

function Test-Service {
    param([string]$Name, [int]$Port, [string]$Url)
    
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ $Name" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    # Test port
    if (Test-Port -Port $Port) {
        Write-Status "Port $Port: OPEN" "Success" "✓"
        
        # Test HTTP endpoint if URL provided
        if ($Url) {
            try {
                $response = Invoke-WebRequest -Uri $Url -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
                Write-Status "HTTP Status: $($response.StatusCode) OK" "Success" "✓"
                
                if ($Verbose) {
                    Write-Status "Response Headers:" "Debug"
                    $response.Headers.GetEnumerator() | ForEach-Object {
                        Write-Host "  $($_.Key): $($_.Value)" -ForegroundColor Gray
                    }
                }
            } catch {
                Write-Status "HTTP Request Failed: $($_.Exception.Message)" "Error" "✗"
            }
        }
    } else {
        Write-Status "Port $Port: CLOSED (Service not running)" "Error" "✗"
    }
}

function Check-Docker {
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ DOCKER & CONTAINERS" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    # Check Docker installation
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-Status "$dockerVersion" "Success" "✓"
        }
    } catch {
        Write-Status "Docker not installed" "Error" "✗"
        return $false
    }
    
    # Check Docker daemon
    try {
        docker ps >$null 2>&1
        Write-Status "Docker daemon running" "Success" "✓"
    } catch {
        Write-Status "Docker daemon not responding" "Error" "✗"
        return $false
    }
    
    # List running containers
    Write-Host "`nRunning Containers:" -ForegroundColor Yellow
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    if ($containers) {
        $containers | ForEach-Object {
            if ($_ -match "physician-ai") {
                Write-Host "  $_" -ForegroundColor Green
            } else {
                Write-Host "  $_" -ForegroundColor Gray
            }
        }
    } else {
        Write-Status "  No containers running" "Warning" "⚠"
    }
    
    return $true
}

function Check-Python {
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ PYTHON ENVIRONMENT" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Status "$pythonVersion" "Success" "✓"
    } catch {
        Write-Status "Python not found" "Error" "✗"
        return $false
    }
    
    # Check virtual environment
    $venvPath = Join-Path $global:BackendDir "venv"
    if (Test-Path $venvPath) {
        Write-Status "Virtual environment exists" "Success" "✓"
        
        # Check if activated
        if (Test-Path env:VIRTUAL_ENV) {
            Write-Status "Virtual environment is ACTIVE" "Success" "✓"
        } else {
            Write-Status "Virtual environment not active (activate with: .\backend\venv\Scripts\Activate.ps1)" "Warning" "⚠"
        }
    } else {
        Write-Status "Virtual environment not found" "Error" "✗"
        if ($Fix) {
            Write-Status "Creating virtual environment..." "Info" "⚙️"
            python -m venv $venvPath
        }
        return $false
    }
    
    # Check key packages
    Write-Host "`nKey Packages:" -ForegroundColor Yellow
    $packages = @("fastapi", "celery", "redis", "sqlalchemy", "psycopg2", "flower")
    
    foreach ($package in $packages) {
        try {
            python -c "import $($package.Replace('-', '_'))" 2>$null
            Write-Status "$package" "Success" "✓"
        } catch {
            Write-Status "$package - NOT INSTALLED" "Error" "✗"
        }
    }
    
    return $true
}

function Check-Database {
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ DATABASE" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    # Check PostgreSQL container
    $dbContainer = docker ps --filter "name=physician-ai-db" --format "{{.Names}}"
    
    if ($dbContainer) {
        Write-Status "PostgreSQL Container: Running" "Success" "✓"
        
        # Test connection
        try {
            $result = docker exec physician-ai-db pg_isready -U physician_user 2>&1
            if ($result -like "*accepting*") {
                Write-Status "Database Connection: OK" "Success" "✓"
                
                # Get database stats
                $stats = docker exec physician-ai-db psql -U physician_user -d physician_ai -t -c `
                    "SELECT 'Tables: ' || count(*) FROM information_schema.tables WHERE table_schema='public'" 2>&1
                Write-Status "$stats" "Info" "📊"
            } else {
                Write-Status "Database Connection: FAILED" "Error" "✗"
            }
        } catch {
            Write-Status "Could not test database: $($_)" "Error" "✗"
        }
    } else {
        Write-Status "PostgreSQL Container: Not Running" "Error" "✗"
    }
}

function Check-Redis {
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ REDIS (Message Broker)" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    # Check local Redis
    if (Test-Port -Port 6379) {
        Write-Status "Local Redis: RUNNING" "Success" "✓"
        
        # Test ping
        try {
            $response = docker exec physician-ai-redis redis-cli PING 2>$null
            if ($response -eq "PONG") {
                Write-Status "Redis Response: PONG" "Success" "✓"
                
                # Get stats
                $stats = docker exec physician-ai-redis redis-cli INFO memory 2>&1 | grep "used_memory_human"
                Write-Status "$stats" "Info" "📊"
            }
        } catch {
            Write-Status "Could not ping Redis" "Error" "✗"
        }
    } else {
        Write-Status "Redis: NOT RUNNING" "Error" "✗"
    }
}

function Check-Backend {
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ FASTAPI BACKEND" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    if (Test-Port -Port 8000) {
        Write-Status "Backend: RUNNING" "Success" "✓"
        
        # Test endpoints
        $endpoints = @{
            "Health Check" = "http://localhost:8000/health"
            "API Docs" = "http://localhost:8000/docs"
            "OpenAPI Spec" = "http://localhost:8000/openapi.json"
        }
        
        Write-Host "`nEndpoints:" -ForegroundColor Yellow
        foreach ($endpoint in $endpoints.GetEnumerator()) {
            try {
                $response = Invoke-WebRequest -Uri $endpoint.Value -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
                Write-Status "$($endpoint.Key): $($response.StatusCode)" "Success" "✓"
            } catch {
                Write-Status "$($endpoint.Key): FAILED" "Error" "✗"
            }
        }
    } else {
        Write-Status "Backend: NOT RUNNING" "Error" "✗"
    }
}

function Check-Celery {
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ CELERY WORKER" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    # Check if worker is running (via Flower)
    if (Test-Port -Port 5555) {
        Write-Status "Flower Dashboard: RUNNING" "Success" "✓"
        
        try {
            $workers = Invoke-WebRequest -Uri "http://localhost:5555/api/workers" `
                -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
            $workerCount = ($workers.Content | ConvertFrom-Json).PSObject.Properties.Count
            Write-Status "Active Workers: $workerCount" "Info" "📊"
        } catch {
            Write-Status "Could not fetch worker stats" "Error" "✗"
        }
    } else {
        Write-Status "Celery Worker: NOT RUNNING" "Error" "✗"
        Write-Status "Flower Dashboard: NOT RUNNING (run .\start-flower.ps1)" "Warning" "⚠"
    }
}

function Check-Frontend {
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ REACT FRONTEND" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    if (Test-Port -Port 5173) {
        Write-Status "Frontend Dev Server: RUNNING" "Success" "✓"
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5173" `
                -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
            Write-Status "Vite Server: OK" "Success" "✓"
        } catch {
            Write-Status "Frontend not responding" "Warning" "⚠"
        }
    } else {
        Write-Status "Frontend Dev Server: NOT RUNNING" "Warning" "⚠"
        Write-Status "Run 'npm run dev' in frontend directory" "Info" "💡"
    }
}

function Show-Summary {
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ DIAGNOSTICS SUMMARY" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    # Count running services
    $running = 0
    $total = 0
    
    $services = @(
        @{Name="Backend"; Port=8000},
        @{Name="Frontend"; Port=5173},
        @{Name="Flower"; Port=5555},
        @{Name="Redis"; Port=6379},
        @{Name="PostgreSQL"; Port=5432}
    )
    
    foreach ($service in $services) {
        if (Test-Port -Port $service.Port) {
            Write-Status "$($service.Name): RUNNING" "Success" "✓"
            $running++
        } else {
            Write-Status "$($service.Name): NOT RUNNING" "Warning" "✗"
        }
        $total++
    }
    
    Write-Host "`nStatus: $running/$total services running" -ForegroundColor Cyan
    
    if ($running -eq $total) {
        Write-Host "`n✅ All services healthy and running!" -ForegroundColor Green
        Write-Host @"

Quick Links:
  • Frontend:  http://localhost:5173
  • Backend:   http://localhost:8000/docs
  • Flower:    http://localhost:5555
"@
    } elseif ($running -gt 0) {
        Write-Host "`n⚠️  Some services are missing. Run:" -ForegroundColor Yellow
        Write-Host "  .\start-debug-full.ps1" -ForegroundColor Cyan
    } else {
        Write-Host "`n❌ No services running. Run:" -ForegroundColor Red
        Write-Host "  .\start-debug-full.ps1" -ForegroundColor Cyan
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Host @"
╔════════════════════════════════════════════════════════════════════════════╗
║                NATPUDAN AI - DIAGNOSTIC REPORT                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

# Run all checks
Check-Docker
Check-Python
Check-Database
Check-Redis
Check-Backend
Check-Celery
Check-Frontend

# Show summary
Show-Summary

Write-Host "`n"
