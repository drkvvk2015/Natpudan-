#!/usr/bin/env pwsh
<#!
    Orchestrates backend (FastAPI) and frontend (Vite) for local development.
    - Starts backend via start-backend.ps1
    - Waits for /health to report healthy
    - Starts frontend via start-frontend.ps1
    - Runs both in background jobs and streams logs
    - Ctrl+C stops both jobs cleanly
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = $PSScriptRoot

function Start-JobWithName {
    [CmdletBinding(DefaultParameterSetName = 'FilePath')]
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true, ParameterSetName = 'FilePath')][string]$FilePath,
        [Parameter(Mandatory = $true, ParameterSetName = 'ScriptBlock')][scriptblock]$ScriptBlock
    )
    $existing = Get-Job -Name $Name -ErrorAction SilentlyContinue
    if ($existing) {
        try { Stop-Job -Name $Name -Force -ErrorAction SilentlyContinue } catch {}
        try { Remove-Job -Name $Name -ErrorAction SilentlyContinue } catch {}
    }
    if ($PSCmdlet.ParameterSetName -eq 'FilePath') {
        return Start-Job -Name $Name -FilePath $FilePath
    }
    else {
        return Start-Job -Name $Name -ScriptBlock $ScriptBlock
    }
}

# Start backend
$backendScript = Join-Path $repoRoot 'start-backend.ps1'
if (-not (Test-Path $backendScript)) { Write-Error "Missing $backendScript"; exit 1 }

Write-Host "Starting backend..." -ForegroundColor Green
$backendJob = Start-JobWithName -Name 'backend' -FilePath $backendScript

# Wait for health (up to ~30s)
$healthOk = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $resp = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 2 -Method Get
        if ($resp.status -eq 'healthy') { $healthOk = $true; break }
    }
    catch { Start-Sleep -Milliseconds 500 }
    Start-Sleep -Milliseconds 500
}
if ($healthOk) { Write-Host "Backend is healthy." -ForegroundColor Cyan } else { Write-Warning "Backend health not confirmed; proceeding to start frontend anyway." }

# Start frontend
$frontendScript = Join-Path $repoRoot 'start-frontend.ps1'
if (-not (Test-Path $frontendScript)) { Write-Error "Missing $frontendScript"; exit 1 }

Write-Host "Starting frontend..." -ForegroundColor Green
$frontendJob = Start-JobWithName -Name 'frontend' -FilePath $frontendScript

Write-Host "\nDev environment starting..." -ForegroundColor Yellow
Write-Host "- API:     http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "- Health:  http://127.0.0.1:8000/health" -ForegroundColor Yellow
Write-Host "- Frontend (once ready): http://localhost:3000" -ForegroundColor Yellow

# Stream logs
Write-Host "\nPress Ctrl+C to stop both services." -ForegroundColor Magenta

$stopping = $false
$onExit = {
    if ($script:stopping) { return }
    $script:stopping = $true
    Write-Host "\nStopping services..." -ForegroundColor Magenta
    Get-Job -Name backend, frontend -ErrorAction SilentlyContinue | ForEach-Object { try { Stop-Job $_ -Force -ErrorAction SilentlyContinue } catch {} }
    Get-Job -Name backend, frontend -ErrorAction SilentlyContinue | ForEach-Object { try { Remove-Job $_ -ErrorAction SilentlyContinue } catch {} }
}

# Handle Ctrl+C
$null = Register-EngineEvent PowerShell.Exiting -Action $onExit

# Tail job output
while ($true) {
    Receive-Job -Name backend, frontend -Keep -ErrorAction SilentlyContinue | ForEach-Object { $_ }
    Start-Sleep -Milliseconds 300
}
