#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Starts the frontend Vite dev server
#>

Set-Location "$PSScriptRoot/frontend"

# Check if Vite is already running on port 5173
$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if ($port5173) {
    Write-Host "Vite dev server already running on port 5173. Stopping existing process..." -ForegroundColor Yellow
    $process = Get-Process -Id $port5173.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

Write-Host "Starting Vite dev server on port 5173..." -ForegroundColor Green

# Start Vite in this process
npm run dev
