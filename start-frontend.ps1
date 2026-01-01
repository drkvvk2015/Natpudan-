#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Starts the frontend Vite dev server
#>

Set-Location "$PSScriptRoot/frontend"

Write-Host "Starting Vite dev server on port 5173..." -ForegroundColor Green

# Start Vite in this process
npm run dev
