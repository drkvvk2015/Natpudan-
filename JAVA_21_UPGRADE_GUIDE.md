# Java 21 LTS Upgrade Guide for Natpudan Android App

## Summary
Your Android project has been configured to use Java 21 LTS (Long-Term Support). This upgrade provides better performance, security, and access to modern Java features.

## Changes Made

### 1. Updated `android/app/build.gradle`
Added Java 21 compilation options:
```groovy
compileOptions {
    sourceCompatibility JavaVersion.VERSION_21
    targetCompatibility JavaVersion.VERSION_21
}
```

### 2. Updated `android/gradle.properties`
Added placeholder for Java home configuration (optional).

## Prerequisites - Java 21 Installation

### Option 1: Download and Install Java 21 (Recommended)
1. Download **Eclipse Temurin JDK 21** (formerly AdoptOpenJDK):
   - Visit: https://adoptium.net/temurin/releases/?version=21
   - Choose: **Windows x64 JDK .msi installer**
   - Install to default location (e.g., `C:\Program Files\Eclipse Adoptium\jdk-21.x.x`)

2. Set JAVA_HOME environment variable:
   ```powershell
   # Run as Administrator
   [System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Eclipse Adoptium\jdk-21.x.x', 'Machine')
   ```

3. Add to PATH:
   ```powershell
   # Run as Administrator
   $currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
   [System.Environment]::SetEnvironmentVariable('Path', "$currentPath;%JAVA_HOME%\bin", 'Machine')
   ```

4. Restart PowerShell/Terminal and verify:
   ```powershell
   java -version
   # Should show: openjdk version "21.x.x"
   ```

### Option 2: Use Android Studio's Bundled JDK
If you have Android Studio installed, it includes a JDK. Configure Gradle to use it:

1. Find the JDK path in Android Studio:
   - File → Project Structure → SDK Location → JDK location
   - Typical path: `C:\Program Files\Android\Android Studio\jbr` (JetBrains Runtime)

2. If using JDK 17 or earlier, upgrade Android Studio or manually install JDK 21.

### Option 3: Use SDKMAN (Windows via WSL or Git Bash)
```bash
sdk install java 21.0.1-tem
sdk use java 21.0.1-tem
```

## Building the Android App

### Using Gradle Wrapper (Recommended)
The Gradle wrapper will automatically download the correct Gradle version:

```powershell
# Navigate to android directory
cd android

# Clean build
.\gradlew clean

# Build debug APK
.\gradlew assembleDebug

# Build release APK (requires signing config)
.\gradlew assembleRelease
```

### Troubleshooting

#### Error: "Unsupported Java version"
- Ensure Java 21 is installed and JAVA_HOME is set correctly
- Check: `java -version` should show version 21.x.x

#### Error: "Could not find or load main class org.gradle.wrapper.GradleWrapperMain"
- Re-download Gradle wrapper:
  ```powershell
  cd android
  gradle wrapper --gradle-version=8.7
  ```

#### Error: "Android Gradle plugin requires Java 17 to run"
- Gradle 8.5+ supports Java 21
- Update Gradle wrapper if needed (already using 8.13.0 in your project)

## Compatibility Notes

### Android Gradle Plugin 8.13.0
✅ Your project uses AGP 8.13.0, which fully supports Java 21.

### Minimum Requirements
- **Gradle**: 8.5+ (you have wrapper configured)
- **Android Gradle Plugin**: 8.3+ (you have 8.13.0 ✅)
- **Android Studio**: Arctic Fox or later (for IDE support)

### Java 21 Features Available
With Java 21, you can now use:
- **Pattern Matching for switch** (Preview in 17, finalized in 21)
- **Record Patterns** (finalized in 21)
- **Virtual Threads** (finalized in 21)
- **Sequenced Collections** (finalized in 21)
- All features from Java 17 LTS

## Verification Steps

1. **Verify Java installation**:
   ```powershell
   java -version
   javac -version
   ```

2. **Check Gradle uses Java 21**:
   ```powershell
   cd android
   .\gradlew -version
   # Should show "JVM: 21.x.x"
   ```

3. **Test build**:
   ```powershell
   cd android
   .\gradlew clean assembleDebug
   ```

4. **Check APK**:
   - Built APK location: `android/app/build/outputs/apk/debug/app-debug.apk`
   - Install and test on device/emulator

## Integration with Capacitor

Your project uses Capacitor for cross-platform development. The Java 21 upgrade only affects the Android native layer:

- ✅ Capacitor plugins continue to work
- ✅ Web assets (React frontend) unchanged
- ✅ Existing Capacitor configuration preserved

## Next Steps

1. Install Java 21 JDK (see Option 1 above)
2. Set JAVA_HOME and PATH environment variables
3. Restart your terminal/IDE
4. Run test build: `cd android && .\gradlew assembleDebug`
5. Test the app on an emulator or device

## Rollback (If Needed)

If you need to revert to an earlier Java version:

1. Change in `android/app/build.gradle`:
   ```groovy
   compileOptions {
       sourceCompatibility JavaVersion.VERSION_17  // or VERSION_11
       targetCompatibility JavaVersion.VERSION_17
   }
   ```

2. Clean and rebuild:
   ```powershell
   cd android
   .\gradlew clean
   .\gradlew assembleDebug
   ```

## Additional Resources

- [Java 21 Release Notes](https://openjdk.org/projects/jdk/21/)
- [Android Gradle Plugin Release Notes](https://developer.android.com/build/releases/gradle-plugin)
- [Gradle Compatibility Matrix](https://docs.gradle.org/current/userguide/compatibility.html)
- [Capacitor Android Documentation](https://capacitorjs.com/docs/android)

## Support

If you encounter issues:
1. Check that Java 21 is properly installed: `java -version`
2. Verify JAVA_HOME is set correctly: `echo $env:JAVA_HOME`
3. Ensure Gradle can find Java 21: `cd android && .\gradlew -version`
4. Clean build directory: `cd android && .\gradlew clean`

---
**Upgrade Date**: December 30, 2025  
**Target Version**: Java 21 LTS  
**Project**: Natpudan Medical AI Assistant - Android App
