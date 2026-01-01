# Stop Development Environment
# This script stops all Natpudan development processes

$ErrorActionPreference = "Continue"

Write-Host "=== Stopping Natpudan Development Environment ===" -ForegroundColor Cyan
Write-Host ""

# Function to stop processes on a specific port
function Stop-ProcessOnPort {
    param([int]$Port, [string]$ServiceName)
    
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connections) {
        $processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($pid in $processIds) {
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "Stopping $ServiceName (PID: $pid)..." -ForegroundColor Yellow
                    Stop-Process -Id $pid -Force
                    Write-Host "✓ $ServiceName stopped" -ForegroundColor Green
                }
            } catch {
                Write-Host "⚠ Could not stop process $pid" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "No process found on port $Port" -ForegroundColor Gray
    }
}

# Stop backend (port 8000)
Stop-ProcessOnPort -Port 8000 -ServiceName "Backend"
Start-Sleep -Seconds 1

# Stop frontend (port 5173)
Stop-ProcessOnPort -Port 5173 -ServiceName "Frontend"
Start-Sleep -Seconds 1

# Also stop any Python/Node processes that might be running
Write-Host ""
Write-Host "Checking for remaining Python/Node processes..." -ForegroundColor Cyan

$pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*Natpudan*" }
if ($pythonProcesses) {
    Write-Host "Stopping $($pythonProcesses.Count) Python process(es)..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
}

$nodeProcesses = Get-Process -Name "node*" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*Natpudan*" }
if ($nodeProcesses) {
    Write-Host "Stopping $($nodeProcesses.Count) Node process(es)..." -ForegroundColor Yellow
    $nodeProcesses | Stop-Process -Force
}

Write-Host ""
Write-Host "✓ All development services stopped" -ForegroundColor Green
Write-Host ""
