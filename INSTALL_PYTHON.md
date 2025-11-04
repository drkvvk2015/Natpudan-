# 🐍 Python Installation Guide

## Python is Required!

The Physician AI Assistant requires Python 3.8 or higher. You need to install Python before proceeding.

## Installation Options

### Option 1: Official Python Website (Recommended)

1. **Download Python:**
   - Visit: https://www.python.org/downloads/
   - Click "Download Python 3.11.x" (latest stable version)

2. **Install Python:**
   - Run the downloaded installer
   - ⚠️ **IMPORTANT:** Check "Add Python to PATH" at the bottom
   - Click "Install Now"
   - Wait for installation to complete

3. **Verify Installation:**
   ```powershell
   python --version
   # Should show: Python 3.11.x
   ```

### Option 2: Microsoft Store

1. **Install from Store:**
   ```powershell
   # This will open Microsoft Store
   python
   ```
   - Click "Get" or "Install" on Python 3.11
   - Wait for installation

2. **Verify Installation:**
   ```powershell
   python --version
   ```

### Option 3: Windows Package Manager (winget)

```powershell
# Install Python 3.11
winget install Python.Python.3.11

# After installation, restart PowerShell
# Then verify:
python --version
```

## After Installing Python

1. **Close and reopen PowerShell** (important for PATH updates)

2. **Verify Python is working:**
   ```powershell
   python --version
   pip --version
   ```

3. **Run the setup script:**
   ```powershell
   cd "D:\Users\CNSHO\Documents\GitHub\Natpudan-"
   .\setup.ps1
   ```

## Troubleshooting

### "Python not found" after installation

**Solution:** Restart PowerShell or add Python to PATH manually:

```powershell
# Find Python installation
Get-ChildItem -Path "C:\Program Files\Python*" -Recurse -Filter python.exe

# Add to PATH (replace with your actual Python path)
$env:Path += ";C:\Program Files\Python311;C:\Program Files\Python311\Scripts"
```

### Microsoft Store version opens instead of Python

**Solution:** Python isn't installed. Install it using Option 1 or 2 above.

### "pip not found"

**Solution:** Reinstall Python and ensure "pip" is selected during installation, or:

```powershell
python -m ensurepip --upgrade
```

## Quick Start After Python Installation

```powershell
# 1. Navigate to project
cd "D:\Users\CNSHO\Documents\GitHub\Natpudan-"

# 2. Run setup (creates venv, installs packages)
.\setup.ps1

# 3. Run tests
.\test.ps1

# 4. Start the server
cd backend
python run.py
```

## Need Help?

If you continue to have issues:
1. Ensure Python 3.8+ is installed
2. Verify `python --version` works
3. Make sure Python is in your PATH
4. Try restarting your computer after installation

---

**Once Python is installed, come back and run `.\setup.ps1`!**
