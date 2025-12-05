# Multi-Platform Build Scripts
# Usage: .\build-all.ps1 [platform]
# Platforms: web, android, ios, windows, linux, all

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("web", "android", "ios", "windows", "linux", "all")]
    [string]$Platform = "all"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Natpudan AI - Multi-Platform Build" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Node.js not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}
Write-Host "Node.js: $(node --version)" -ForegroundColor Green

# Check npm
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "Error: npm not found." -ForegroundColor Red
    exit 1
}
Write-Host "npm: $(npm --version)" -ForegroundColor Green
Write-Host ""

# Navigate to frontend directory
Set-Location -Path "frontend"

# Function to build web
function Build-Web {
    Write-Host "Building web application..." -ForegroundColor Yellow
    npm run build:web
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Web build completed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Web build failed" -ForegroundColor Red
        exit 1
    }
}

# Function to build Android
function Build-Android {
    Write-Host "Building Android APK..." -ForegroundColor Yellow
    
    # Check if Android SDK is available
    if (-not $env:ANDROID_HOME) {
        Write-Host "Warning: ANDROID_HOME not set. Please install Android Studio." -ForegroundColor Red
        return
    }
    
    npm run build:android
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Android build completed successfully" -ForegroundColor Green
        Write-Host "APK location: android/app/build/outputs/apk/release/" -ForegroundColor Cyan
    }
    else {
        Write-Host "✗ Android build failed" -ForegroundColor Red
    }
}

# Function to build iOS
function Build-iOS {
    Write-Host "Building iOS IPA..." -ForegroundColor Yellow
    
    # Check if on macOS
    if ($IsMacOS -or $IsLinux) {
        npm run build:ios
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] iOS build completed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "✗ iOS build failed" -ForegroundColor Red
        }
    }
    else {
        Write-Host "iOS builds require macOS and Xcode" -ForegroundColor Yellow
    }
}

# Function to build Windows
function Build-Windows {
    Write-Host "Building Windows installer..." -ForegroundColor Yellow
    npm run build:windows
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Windows build completed successfully" -ForegroundColor Green
        Write-Host "Installer location: release/" -ForegroundColor Cyan
    }
    else {
        Write-Host "✗ Windows build failed" -ForegroundColor Red
    }
}

# Function to build Linux
function Build-Linux {
    Write-Host "Building Linux packages..." -ForegroundColor Yellow
    npm run build:linux
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Linux build completed successfully" -ForegroundColor Green
        Write-Host "Packages location: release/" -ForegroundColor Cyan
    }
    else {
        Write-Host "✗ Linux build failed" -ForegroundColor Red
    }
}

# Execute builds based on platform
Write-Host "Starting build for: $Platform" -ForegroundColor Cyan
Write-Host ""

switch ($Platform) {
    "web" {
        Build-Web
    }
    "android" {
        Build-Web
        Build-Android
    }
    "ios" {
        Build-Web
        Build-iOS
    }
    "windows" {
        Build-Web
        Build-Windows
    }
    "linux" {
        Build-Web
        Build-Linux
    }
    "all" {
        Build-Web
        Write-Host ""
        Build-Android
        Write-Host ""
        Build-Windows
        Write-Host ""
        Build-Linux
        Write-Host ""
        Build-iOS
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Build process completed!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan

# Return to root directory
Set-Location -Path ".."
