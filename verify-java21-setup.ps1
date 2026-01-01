# Java 21 Setup and Verification Script for Natpudan Android
# Run this script to check Java installation and build status

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Java 21 Upgrade Verification Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Java Installation
Write-Host "[1/5] Checking Java installation..." -ForegroundColor Yellow
$javaFound = $false
try {
    $javaVersion = & java -version 2>&1 | Out-String
    if ($javaVersion) {
        $javaFound = $true
        Write-Host "Java found: $($javaVersion.Split([Environment]::NewLine)[0])" -ForegroundColor Green
        
        if ($javaVersion -match "21\.") {
            Write-Host "Java 21 detected!" -ForegroundColor Green
        } else {
            Write-Host "Java 21 is required for this project" -ForegroundColor Yellow
            Write-Host "  Please install Java 21 from: https://adoptium.net/temurin/releases/?version=21" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "Java not found in PATH" -ForegroundColor Red
    Write-Host "  Please install Java 21 from: https://adoptium.net/temurin/releases/?version=21" -ForegroundColor Yellow
    Write-Host "  After installation, set JAVA_HOME and add to PATH" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Check JAVA_HOME
Write-Host "[2/5] Checking JAVA_HOME environment variable..." -ForegroundColor Yellow
if ($env:JAVA_HOME) {
    Write-Host "JAVA_HOME is set to: $env:JAVA_HOME" -ForegroundColor Green
    
    # Verify the path exists
    if (Test-Path $env:JAVA_HOME) {
        Write-Host "JAVA_HOME path exists" -ForegroundColor Green
    } else {
        Write-Host "JAVA_HOME path does not exist!" -ForegroundColor Yellow
    }
} else {
    Write-Host "JAVA_HOME is not set" -ForegroundColor Yellow
    Write-Host "  To set JAVA_HOME (run as Administrator):" -ForegroundColor Cyan
    Write-Host '  [System.Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Eclipse Adoptium\jdk-21.x.x", "Machine")' -ForegroundColor Gray
}

Write-Host ""

# Step 3: Check Android SDK
Write-Host "[3/5] Checking Android SDK..." -ForegroundColor Yellow
$androidSdkPath = "$env:LOCALAPPDATA\Android\Sdk"
if (Test-Path $androidSdkPath) {
    Write-Host "Android SDK found at: $androidSdkPath" -ForegroundColor Green
} else {
    Write-Host "Android SDK not found at standard location" -ForegroundColor Yellow
    Write-Host "  Install Android Studio from: https://developer.android.com/studio" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Check Gradle Configuration
Write-Host "[4/5] Checking Gradle configuration..." -ForegroundColor Yellow
$gradleWrapperPath = "android\gradlew.bat"
if (Test-Path $gradleWrapperPath) {
    Write-Host "Gradle wrapper found" -ForegroundColor Green
    
    # Check Gradle version
    Write-Host "  Checking Gradle version..." -ForegroundColor Cyan
    Push-Location android
    try {
        $gradleVersion = & .\gradlew.bat -version 2>&1 | Select-String "Gradle" | Select-Object -First 1
        Write-Host "  $gradleVersion" -ForegroundColor Gray
    } catch {
        Write-Host "  Could not determine Gradle version" -ForegroundColor Yellow
    }
    Pop-Location
} else {
    Write-Host "Gradle wrapper not found" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Verify Java 21 Configuration in build.gradle
Write-Host "[5/5] Verifying Java 21 configuration in build.gradle..." -ForegroundColor Yellow
$buildGradlePath = "android\app\build.gradle"
if (Test-Path $buildGradlePath) {
    $buildGradleContent = Get-Content $buildGradlePath -Raw
    if ($buildGradleContent -match "JavaVersion\.VERSION_21") {
        Write-Host "Java 21 configured in build.gradle" -ForegroundColor Green
    } else {
        Write-Host "Java 21 not found in build.gradle" -ForegroundColor Yellow
    }
} else {
    Write-Host "build.gradle not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Provide next steps
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Green
Write-Host "1. If Java 21 is not installed, download from: https://adoptium.net/temurin/releases/?version=21" -ForegroundColor White
Write-Host "2. Set JAVA_HOME and add to PATH (see JAVA_21_UPGRADE_GUIDE.md for details)" -ForegroundColor White
Write-Host "3. Restart terminal/PowerShell after setting environment variables" -ForegroundColor White
Write-Host "4. Run test build:" -ForegroundColor White
Write-Host "   cd android" -ForegroundColor Cyan
Write-Host "   .\gradlew clean assembleDebug" -ForegroundColor Cyan
Write-Host ""
Write-Host "For detailed instructions, see: JAVA_21_UPGRADE_GUIDE.md" -ForegroundColor Yellow
Write-Host ""

# Optional: Prompt to open guide
$openGuide = Read-Host "Open JAVA_21_UPGRADE_GUIDE.md? (y/n)"
if ($openGuide -eq "y" -or $openGuide -eq "Y") {
    if (Test-Path "JAVA_21_UPGRADE_GUIDE.md") {
        Start-Process "JAVA_21_UPGRADE_GUIDE.md"
    }
}

Write-Host ""
Write-Host "Script complete!" -ForegroundColor Green
