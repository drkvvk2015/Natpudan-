# Real-time Service Monitor for Natpudan AI
# Shows health status of all services with auto-refresh

$global:RootDir = "D:\Users\CNSHO\Documents\GitHub\Natpudan-"

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

function Get-ServiceStatus {
    param([string]$Name, [int]$Port, [string]$Url = $null)
    
    if (Test-Port -Port $Port) {
        if ($Url) {
            try {
                $response = Invoke-WebRequest -Uri $Url -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    return @{Status="✅ UP"; Color="Green"; Port="$Port"}
                }
            } catch {
                return @{Status="⚠️  SLOW"; Color="Yellow"; Port="$Port"}
            }
        }
        return @{Status="✅ UP"; Color="Green"; Port="$Port"}
    } else {
        return @{Status="❌ DOWN"; Color="Red"; Port="$Port"}
    }
}

function Get-DockerStatus {
    try {
        $running = docker ps --filter "name=physician-ai" --format "table {{.Names}}\t{{.Status}}" 2>$null
        if ($running) {
            return @{Count=($running | Measure-Object).Count - 1; Status="✅ RUNNING"; Color="Green"}
        }
    } catch {}
    return @{Count=0; Status="❌ NOT RUNNING"; Color="Red"}
}

function Show-Dashboard {
    Clear-Host
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $date = Get-Date -Format "dddd, MMMM d, yyyy"
    
    Write-Host @"
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║           🏥 NATPUDAN AI - REAL-TIME SERVICE MONITOR 🏥                   ║
║                                                                            ║
║  Last Updated: $timestamp on $date                                ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

    # Test all services
    Write-Host "`n📊 SERVICE STATUS" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    $frontend = Get-ServiceStatus -Name "Frontend" -Port 5173 -Url "http://localhost:5173"
    $backend = Get-ServiceStatus -Name "Backend" -Port 8000 -Url "http://localhost:8000/health"
    $flower = Get-ServiceStatus -Name "Flower" -Port 5555 -Url "http://localhost:5555"
    $redis = Get-ServiceStatus -Name "Redis" -Port 6379
    $postgres = Get-ServiceStatus -Name "PostgreSQL" -Port 5432
    
    Write-Host ("  Frontend (React)          " + $frontend.Status + " ") -ForegroundColor $frontend.Color -NoNewline
    Write-Host "| Port " + $frontend.Port -ForegroundColor Gray
    
    Write-Host ("  Backend (FastAPI)         " + $backend.Status + " ") -ForegroundColor $backend.Color -NoNewline
    Write-Host "| Port " + $backend.Port -ForegroundColor Gray
    
    Write-Host ("  Flower (Celery Monitor)   " + $flower.Status + " ") -ForegroundColor $flower.Color -NoNewline
    Write-Host "| Port " + $flower.Port -ForegroundColor Gray
    
    Write-Host ("  Redis (Broker)            " + $redis.Status + " ") -ForegroundColor $redis.Color -NoNewline
    Write-Host "| Port " + $redis.Port -ForegroundColor Gray
    
    Write-Host ("  PostgreSQL (Database)     " + $postgres.Status + " ") -ForegroundColor $postgres.Color -NoNewline
    Write-Host "| Port " + $postgres.Port -ForegroundColor Gray
    
    # Docker status
    Write-Host "`n🐳 DOCKER CONTAINERS" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    $docker = Get-DockerStatus
    Write-Host ("  Containers " + $docker.Status) -ForegroundColor $docker.Color
    
    try {
        $containers = docker ps --filter "name=physician-ai" --format "{{.Names}}" 2>$null
        if ($containers) {
            $containers | ForEach-Object {
                Write-Host ("    • " + $_) -ForegroundColor Green
            }
        }
    } catch {}
    
    # Quick Links
    Write-Host "`n🔗 QUICK LINKS" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    if ($frontend.Status -like "*UP*") {
        Write-Host "  ⭐ Frontend:  http://localhost:5173" -ForegroundColor Green
    } else {
        Write-Host "  ⭐ Frontend:  http://localhost:5173" -ForegroundColor Gray
    }
    
    if ($backend.Status -like "*UP*") {
        Write-Host "  📚 API Docs:  http://localhost:8000/docs" -ForegroundColor Green
        Write-Host "  📖 ReDoc:     http://localhost:8000/redoc" -ForegroundColor Green
    } else {
        Write-Host "  📚 API Docs:  http://localhost:8000/docs" -ForegroundColor Gray
        Write-Host "  📖 ReDoc:     http://localhost:8000/redoc" -ForegroundColor Gray
    }
    
    if ($flower.Status -like "*UP*") {
        Write-Host "  🌸 Flower:    http://localhost:5555" -ForegroundColor Green
    } else {
        Write-Host "  🌸 Flower:    http://localhost:5555" -ForegroundColor Gray
    }
    
    # Status Summary
    Write-Host "`n📈 STATUS SUMMARY" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    $upCount = 0
    $total = 5
    
    if ($frontend.Status -like "*UP*") { $upCount++ }
    if ($backend.Status -like "*UP*") { $upCount++ }
    if ($flower.Status -like "*UP*") { $upCount++ }
    if ($redis.Status -like "*UP*") { $upCount++ }
    if ($postgres.Status -like "*UP*") { $upCount++ }
    
    $percentage = [math]::Round(($upCount / $total) * 100)
    $statusBar = ""
    for ($i = 0; $i -lt $upCount; $i++) { $statusBar += "█" }
    for ($i = $upCount; $i -lt $total; $i++) { $statusBar += "░" }
    
    Write-Host "  Services Running: $upCount/$total" -ForegroundColor Cyan
    Write-Host "  [$statusBar] $percentage%" -ForegroundColor Cyan
    
    if ($upCount -eq $total) {
        Write-Host "`n  ✨ All systems operational! Proceeding with caution... ✨" -ForegroundColor Green
    } elseif ($upCount -gt 0) {
        Write-Host "`n  ⚠️  Some services are offline. Run .\start-debug-full.ps1" -ForegroundColor Yellow
    } else {
        Write-Host "`n  ❌ All services offline. Run .\start-debug-full.ps1" -ForegroundColor Red
    }
    
    # Commands
    Write-Host "`n⌨️  COMMANDS" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "  'S' - Start all services (.\start-debug-full.ps1)" -ForegroundColor Gray
    Write-Host "  'D' - Run diagnostics (.\diagnose.ps1)" -ForegroundColor Gray
    Write-Host "  'L' - View logs (docker logs physician-ai-backend)" -ForegroundColor Gray
    Write-Host "  'R' - Refresh (updates every 10 seconds automatically)" -ForegroundColor Gray
    Write-Host "  'Q' - Quit this monitor" -ForegroundColor Gray
    Write-Host "`n(Refreshing automatically in 10 seconds... Press 'Q' to exit)" -ForegroundColor Yellow
    Write-Host ""
}

function Show-Logs {
    Write-Host "`n📋 BACKEND LOGS" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    try {
        docker logs --tail 20 physician-ai-backend 2>$null | ForEach-Object {
            if ($_ -like "*ERROR*") {
                Write-Host $_ -ForegroundColor Red
            } elseif ($_ -like "*WARNING*") {
                Write-Host $_ -ForegroundColor Yellow
            } elseif ($_ -like "*INFO*") {
                Write-Host $_ -ForegroundColor Green
            } else {
                Write-Host $_
            }
        }
    } catch {
        Write-Host "Could not fetch logs" -ForegroundColor Red
    }
    
    Write-Host "`nPress any key to return to dashboard..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# ============================================================================
# MAIN LOOP
# ============================================================================

while ($true) {
    Show-Dashboard
    
    # Wait for input with timeout (10 seconds for auto-refresh)
    $key = $null
    $timeout = 10
    $elapsed = 0
    
    while ($elapsed -lt $timeout) {
        if ([System.Console]::KeyAvailable) {
            $key = [System.Console]::ReadKey($true)
            break
        }
        Start-Sleep -Milliseconds 100
        $elapsed += 0.1
    }
    
    if ($key) {
        $char = $key.Character.ToString().ToUpper()
        
        switch ($char) {
            'Q' {
                Write-Host "`nExiting monitor..." -ForegroundColor Cyan
                exit 0
            }
            'S' {
                Write-Host "`nStarting services..." -ForegroundColor Cyan
                Push-Location $global:RootDir
                & ".\start-debug-full.ps1"
                Pop-Location
            }
            'D' {
                Write-Host "`nRunning diagnostics..." -ForegroundColor Cyan
                Push-Location $global:RootDir
                & ".\diagnose.ps1"
                Pop-Location
                Write-Host "`nPress any key to return to dashboard..."
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
            'L' {
                Show-Logs
            }
            'R' {
                # Force refresh by continuing loop
                continue
            }
            default {
                # Any other key continues the loop (refresh)
                continue
            }
        }
    }
}
