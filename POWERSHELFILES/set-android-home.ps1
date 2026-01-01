# PowerShell script to detect and set ANDROID_HOME environment variable
# Usage: .\set-android-home.ps1

Write-Host "Detecting Android SDK location..." -ForegroundColor Cyan

# Common Android SDK locations on Windows
$androidSdkLocations = @(
    "$env:LOCALAPPDATA\Android\Sdk",
    "$env:APPDATA\Android\Sdk",
    "C:\Program Files\Android\Android Studio\sdk",
    "C:\Android\sdk",
    "$env:USERPROFILE\AppData\Local\Android\Sdk"
)

$androidHome = $null

# Check if ANDROID_HOME is already set
if ($env:ANDROID_HOME -and (Test-Path $env:ANDROID_HOME)) {
    Write-Host "✓ ANDROID_HOME is already set: $env:ANDROID_HOME" -ForegroundColor Green
    $androidHome = $env:ANDROID_HOME
}
else {
    Write-Host "⚠ ANDROID_HOME not set, searching for Android SDK..." -ForegroundColor Yellow
    
    # Search for Android SDK in common locations
    foreach ($location in $androidSdkLocations) {
        if (Test-Path $location) {
            Write-Host "✓ Found Android SDK at: $location" -ForegroundColor Green
            $androidHome = $location
            break
        }
    }
}

if ($androidHome) {
    # Set environment variable for current session
    $env:ANDROID_HOME = $androidHome
    $env:ANDROID_SDK_ROOT = $androidHome
    
    Write-Host "`n✓ Environment variables set for current session:" -ForegroundColor Green
    Write-Host "  ANDROID_HOME=$env:ANDROID_HOME" -ForegroundColor White
    Write-Host "  ANDROID_SDK_ROOT=$env:ANDROID_SDK_ROOT" -ForegroundColor White
    
    # Add to PATH
    $platformTools = Join-Path $androidHome "platform-tools"
    $cmdlineTools = Join-Path $androidHome "cmdline-tools\latest\bin"
    
    if (Test-Path $platformTools) {
        $env:PATH = "$platformTools;$env:PATH"
        Write-Host "  Added to PATH: $platformTools" -ForegroundColor White
    }
    
    if (Test-Path $cmdlineTools) {
        $env:PATH = "$cmdlineTools;$env:PATH"
        Write-Host "  Added to PATH: $cmdlineTools" -ForegroundColor White
    }
    
    Write-Host "`n📋 To set permanently for your user account, run:" -ForegroundColor Cyan
    Write-Host "  [System.Environment]::SetEnvironmentVariable('ANDROID_HOME', '$androidHome', 'User')" -ForegroundColor Yellow
    Write-Host "  [System.Environment]::SetEnvironmentVariable('ANDROID_SDK_ROOT', '$androidHome', 'User')" -ForegroundColor Yellow
    
    Write-Host "`n📋 Or set system-wide (requires admin), run:" -ForegroundColor Cyan
    Write-Host "  [System.Environment]::SetEnvironmentVariable('ANDROID_HOME', '$androidHome', 'Machine')" -ForegroundColor Yellow
    Write-Host "  [System.Environment]::SetEnvironmentVariable('ANDROID_SDK_ROOT', '$androidHome', 'Machine')" -ForegroundColor Yellow
    
    # Offer to set permanently
    Write-Host "`nWould you like to set ANDROID_HOME permanently for your user account? (Y/N)" -ForegroundColor Cyan
    $response = Read-Host
    
    if ($response -eq 'Y' -or $response -eq 'y') {
        try {
            [System.Environment]::SetEnvironmentVariable('ANDROID_HOME', $androidHome, 'User')
            [System.Environment]::SetEnvironmentVariable('ANDROID_SDK_ROOT', $androidHome, 'User')
            Write-Host "✓ Environment variables set permanently for user account!" -ForegroundColor Green
            Write-Host "  Please restart your terminal for changes to take effect." -ForegroundColor Yellow
        }
        catch {
            Write-Host "✗ Failed to set environment variables: $_" -ForegroundColor Red
        }
    }
    
}
else {
    Write-Host "`n✗ Android SDK not found!" -ForegroundColor Red
    Write-Host "`nPlease install Android Studio or Android SDK and try again." -ForegroundColor Yellow
    Write-Host "Download from: https://developer.android.com/studio" -ForegroundColor Cyan
    Write-Host "`nAfter installation, the SDK is typically located at:" -ForegroundColor Yellow
    Write-Host "  $env:LOCALAPPDATA\Android\Sdk" -ForegroundColor White
    exit 1
}
