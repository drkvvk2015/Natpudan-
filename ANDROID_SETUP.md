# Android Build Setup Guide

This guide will help you set up your environment for building Android APKs.

## Prerequisites

- ✅ Android Studio installed
- ⚠️ ANDROID_HOME environment variable not set

## Quick Fix

### Option 1: Automatic Setup (Recommended)

Run the PowerShell script to automatically detect and set ANDROID_HOME:

```powershell
.\set-android-home.ps1
```

This script will:
1. Search for Android SDK in common locations
2. Set ANDROID_HOME and ANDROID_SDK_ROOT for current session
3. Offer to set permanently for your user account
4. Add Android SDK tools to PATH

### Option 2: Manual Setup

#### Find Your Android SDK Location

Android Studio typically installs the SDK at:
- **Windows**: `%LOCALAPPDATA%\Android\Sdk` (usually `C:\Users\YourName\AppData\Local\Android\Sdk`)
- **macOS**: `~/Library/Android/sdk`
- **Linux**: `~/Android/Sdk`

To verify in Android Studio:
1. Open Android Studio
2. Go to **File** → **Settings** (Windows/Linux) or **Android Studio** → **Preferences** (macOS)
3. Navigate to **Appearance & Behavior** → **System Settings** → **Android SDK**
4. Note the **Android SDK Location** path

#### Set Environment Variables

##### Windows (PowerShell - User Level):

```powershell
# Replace with your actual SDK path
$androidSdk = "$env:LOCALAPPDATA\Android\Sdk"

[System.Environment]::SetEnvironmentVariable('ANDROID_HOME', $androidSdk, 'User')
[System.Environment]::SetEnvironmentVariable('ANDROID_SDK_ROOT', $androidSdk, 'User')

# Restart your terminal
```

##### Windows (PowerShell - System Level, requires Admin):

```powershell
# Replace with your actual SDK path
$androidSdk = "$env:LOCALAPPDATA\Android\Sdk"

[System.Environment]::SetEnvironmentVariable('ANDROID_HOME', $androidSdk, 'Machine')
[System.Environment]::SetEnvironmentVariable('ANDROID_SDK_ROOT', $androidSdk, 'Machine')

# Restart your terminal
```

##### Windows (Command Prompt):

```cmd
setx ANDROID_HOME "%LOCALAPPDATA%\Android\Sdk"
setx ANDROID_SDK_ROOT "%LOCALAPPDATA%\Android\Sdk"
```

##### macOS/Linux (Bash):

```bash
# Add to ~/.bashrc or ~/.zshrc
export ANDROID_HOME=$HOME/Library/Android/sdk  # macOS
# export ANDROID_HOME=$HOME/Android/Sdk        # Linux
export ANDROID_SDK_ROOT=$ANDROID_HOME
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Reload shell configuration
source ~/.bashrc  # or source ~/.zshrc
```

## Verify Setup

After setting environment variables, verify they're correctly set:

### Windows (PowerShell):
```powershell
$env:ANDROID_HOME
$env:ANDROID_SDK_ROOT
```

### macOS/Linux:
```bash
echo $ANDROID_HOME
echo $ANDROID_SDK_ROOT
```

You should see the path to your Android SDK.

## Build Android APK

Once ANDROID_HOME is set, you can build the Android APK:

### From Frontend Directory:

```powershell
cd frontend
npm run build:android
```

### From Root Directory:

```powershell
npm run build:android
```

## Troubleshooting

### "ANDROID_HOME not set" Error

**Symptoms**: Build fails with "Warning: ANDROID_HOME not set"

**Solutions**:
1. Run `.\set-android-home.ps1` to auto-detect and set
2. Verify Android Studio is installed
3. Check SDK location in Android Studio settings
4. Manually set environment variables (see above)
5. **Restart your terminal** after setting variables

### "gradlew: Permission denied" (Linux/macOS)

**Solution**:
```bash
cd frontend/android
chmod +x gradlew
```

### Android SDK Not Found

**Symptoms**: Script reports "Android SDK not found"

**Solutions**:
1. Install Android Studio from https://developer.android.com/studio
2. Open Android Studio and complete the setup wizard
3. Go to SDK Manager and install:
   - Android SDK Platform (latest version)
   - Android SDK Build-Tools (latest version)
   - Android SDK Command-line Tools

### Build Fails with "SDK location not found"

**Symptoms**: Gradle can't find SDK even with ANDROID_HOME set

**Solution**: Create `frontend/android/local.properties`:
```properties
sdk.dir=C:\\Users\\YourName\\AppData\\Local\\Android\\Sdk
```
(Use your actual ANDROID_HOME path, with double backslashes on Windows)

## GitLab CI/CD

The `.gitlab-ci.yml` is configured to automatically detect Android SDK in the Ionic Appflow runner. The build job will:

1. Check common Android SDK locations
2. Set ANDROID_HOME and ANDROID_SDK_ROOT
3. Add SDK tools to PATH
4. Build the Android APK

If the Android SDK is not available in the CI/CD environment, the job will fail gracefully with `allow_failure: true`.

## Required Android SDK Components

Ensure these are installed via Android Studio SDK Manager:

- ✅ Android SDK Platform (API 34 or latest)
- ✅ Android SDK Build-Tools (34.0.0 or latest)
- ✅ Android SDK Command-line Tools (latest)
- ✅ Android Emulator (optional, for testing)

## Signing Configuration (for Release Builds)

To build a signed release APK, you need to configure signing:

1. Generate a keystore (one-time setup):
```bash
keytool -genkey -v -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

2. Create `frontend/android/gradle.properties`:
```properties
RELEASE_STORE_FILE=../../my-release-key.keystore
RELEASE_STORE_PASSWORD=your_keystore_password
RELEASE_KEY_ALIAS=my-key-alias
RELEASE_KEY_PASSWORD=your_key_password
```

3. Update `frontend/android/app/build.gradle` (signing config already included in template)

## Next Steps

After successful Android build, you'll find the APK at:
```
frontend/android/app/build/outputs/apk/release/app-release.apk
```

You can then:
1. Install on an Android device for testing
2. Upload to Google Play Console for distribution
3. Share the APK directly

## References

- [Capacitor Android Development](https://capacitorjs.com/docs/android)
- [Android Studio Download](https://developer.android.com/studio)
- [Publishing to Google Play](https://developer.android.com/studio/publish)
