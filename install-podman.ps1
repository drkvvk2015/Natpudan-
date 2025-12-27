<#
.SYNOPSIS
Install Podman on Windows using Windows Package Manager (winget)
.DESCRIPTION
Automated Podman installation for Windows
#>

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Podman Installation for Windows" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if running as admin
$isAdmin = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[!] This script requires Administrator privileges" -ForegroundColor Yellow
    Write-Host "    Restarting as Administrator..." -ForegroundColor Gray
    
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit 0
}

# Step 1: Check if Podman is already installed
Write-Host "[1/4] Checking if Podman is already installed..." -ForegroundColor Yellow

$podmanInstalled = Get-Command podman -ErrorAction SilentlyContinue
if ($podmanInstalled) {
    Write-Host "      [OK] Podman is already installed!" -ForegroundColor Green
    Write-Host "      Version: $(podman --version)" -ForegroundColor Gray
} else {
    Write-Host "      [!] Podman not found, proceeding with installation..." -ForegroundColor Yellow
}

# Step 2: Check if winget is available
Write-Host "`n[2/4] Checking for Windows Package Manager (winget)..." -ForegroundColor Yellow

$wingetInstalled = Get-Command winget -ErrorAction SilentlyContinue
if (-not $wingetInstalled) {
    Write-Host "      [!] winget not found" -ForegroundColor Yellow
    Write-Host "      Please install App Installer from Microsoft Store or use Method 2" -ForegroundColor Gray
    Write-Host "      See: PODMAN_WINDOWS_INSTALLATION.md" -ForegroundColor Gray
    Write-Host "      Or visit: https://podman.io/docs/installation/windows" -ForegroundColor Cyan
    exit 1
}

Write-Host "      [OK] winget found" -ForegroundColor Green

# Step 3: Install Podman
if (-not $podmanInstalled) {
    Write-Host "`n[3/4] Installing Podman..." -ForegroundColor Yellow
    Write-Host "      This may take several minutes..." -ForegroundColor Gray
    
    try {
        winget install RedHat.Podman -e --accept-package-agreements --accept-source-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "      [OK] Podman installed successfully" -ForegroundColor Green
        } else {
            Write-Error "Installation failed with exit code $LASTEXITCODE"
            exit 1
        }
    } catch {
        Write-Error "Installation error: $_"
        exit 1
    }
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "`n[3/4] Podman already installed, skipping installation..." -ForegroundColor Yellow
}

# Step 4: Verify and setup
Write-Host "`n[4/4] Verifying and setting up..." -ForegroundColor Yellow

# Verify Podman
$podman = Get-Command podman -ErrorAction SilentlyContinue
if ($podman) {
    Write-Host "      [OK] Podman is working" -ForegroundColor Green
    podman --version
} else {
    Write-Error "Podman command not found after installation"
    exit 1
}

# Initialize and start machine
Write-Host "`n      Initializing Podman Machine..." -ForegroundColor Gray

try {
    $machines = podman machine list --format=json | ConvertFrom-Json -ErrorAction SilentlyContinue
    $machineExists = $machines | Where-Object { $_.Name -eq "podman-machine-default" }
    
    if (-not $machineExists) {
        Write-Host "      Creating Podman Machine..." -ForegroundColor Gray
        podman machine init
    } else {
        Write-Host "      [OK] Podman Machine already exists" -ForegroundColor Green
    }
    
    # Start machine
    $isRunning = $machines | Where-Object { $_.IsRunning -eq $true }
    if (-not $isRunning) {
        Write-Host "      Starting Podman Machine..." -ForegroundColor Gray
        podman machine start
        Start-Sleep -Seconds 5
    }
    
    Write-Host "      [OK] Podman Machine is running" -ForegroundColor Green
} catch {
    Write-Warning "Could not initialize Podman Machine: $_"
}

# Install podman-compose
Write-Host "`n      Installing podman-compose..." -ForegroundColor Gray

try {
    pip install podman-compose
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      [OK] podman-compose installed" -ForegroundColor Green
    } else {
        Write-Warning "podman-compose installation may have issues"
    }
} catch {
    Write-Warning "podman-compose installation error: $_"
}

# Final status
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Installed Versions:" -ForegroundColor Cyan
podman --version
podman-compose --version

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "  1. Start your application:" -ForegroundColor Yellow
Write-Host "     cd d:\Users\CNSHO\Documents\GitHub\Natpudan-" -ForegroundColor Gray
Write-Host "     .\start-podman-compose.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Access your services:" -ForegroundColor Yellow
Write-Host "     Frontend: http://127.0.0.1:3000" -ForegroundColor Gray
Write-Host "     Backend:  http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host ""

Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  Setup Guide:        PODMAN_SETUP.md" -ForegroundColor Gray
Write-Host "  Quick Reference:    PODMAN_QUICK_REFERENCE.md" -ForegroundColor Gray
Write-Host "  Troubleshooting:    PODMAN_TROUBLESHOOTING.md" -ForegroundColor Gray
Write-Host ""

Write-Host "[OK] Podman is ready to use! Run start-podman-compose.ps1 to begin." -ForegroundColor Green
Write-Host ""
