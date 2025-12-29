#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Port Configuration Validator
.DESCRIPTION
    Validates that all config files use consistent ports
.EXAMPLE
    .\check-ports.ps1
    .\check-ports.ps1 -Fix
#>

param(
    [switch]$Fix
)

$ConfigFile = Join-Path $PSScriptRoot "..\config\ports.json"

Write-Host "`n===========================================`n" -ForegroundColor Cyan
Write-Host "Port Configuration Validator`n" -ForegroundColor White

# Load config
if (-not (Test-Path $ConfigFile)) {
    Write-Host "[ERROR] Config file not found: $ConfigFile" -ForegroundColor Red
    exit 1
}

$config = Get-Content $ConfigFile | ConvertFrom-Json
$backendUrl = $config.urls.backend.dev

Write-Host "Expected Backend URL: $backendUrl`n" -ForegroundColor Cyan

# Check frontend .env files
$files = @(
    "..\frontend\.env",
    "..\frontend\.env.development",
    "..\frontend\.env.local"
)

$issues = @()
$checked = 0
$passed = 0

foreach ($file in $files) {
    $path = Join-Path $PSScriptRoot $file
    
    if (-not (Test-Path $path)) {
        continue
    }
    
    $content = Get-Content $path -Raw
    $checked++
    
    if ($content -match "VITE_API_BASE_URL=(.*)") {
        $actualUrl = $matches[1].Trim()
        
        if ($actualUrl -eq $backendUrl) {
            Write-Host "[OK] $file" -ForegroundColor Green
            Write-Host "     $actualUrl" -ForegroundColor Gray
            $passed++
        } else {
            Write-Host "[MISMATCH] $file" -ForegroundColor Red
            Write-Host "           Expected: $backendUrl" -ForegroundColor Yellow
            Write-Host "           Actual:   $actualUrl" -ForegroundColor Red
            
            $issues += @{
                File = $path
                Expected = $backendUrl
                Actual = $actualUrl
            }
        }
    }
    Write-Host ""
}

Write-Host "===========================================`n" -ForegroundColor Cyan
Write-Host "Summary: $passed/$checked files correct`n" -ForegroundColor White

if ($issues.Count -eq 0) {
    Write-Host "[SUCCESS] All configurations match!`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "[WARNING] Found $($issues.Count) mismatches`n" -ForegroundColor Yellow
    
    if ($Fix) {
        Write-Host "Applying fixes...`n" -ForegroundColor Cyan
        
        foreach ($issue in $issues) {
            $content = Get-Content $issue.File -Raw
            $newContent = $content -replace "VITE_API_BASE_URL=.*", "VITE_API_BASE_URL=$($issue.Expected)"
            Set-Content -Path $issue.File -Value $newContent -NoNewline
            Write-Host "[FIXED] $($issue.File)" -ForegroundColor Green
        }
        
        Write-Host "`n[SUCCESS] All issues fixed! Restart services.`n" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "Run with -Fix to automatically correct:`n" -ForegroundColor Cyan
        Write-Host "  .\scripts\check-ports.ps1 -Fix`n" -ForegroundColor Yellow
        exit 1
    }
}
