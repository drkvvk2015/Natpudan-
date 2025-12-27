# Getting Started with Podman - Complete Guide

## Current Status

✅ **PowerShell scripts are fixed** - Ready to use
❌ **Podman is not installed yet** - Need to install first

---

## Step 1: Install Podman (5-10 minutes)

### Option A: Automated Installation (Recommended)

Run this script (requires Administrator):

```powershell
# Right-click PowerShell and select "Run as Administrator"
# Then run:
.\install-podman.ps1
```

This script will:
- Check for administrator privileges
- Install Podman via Windows Package Manager (winget)
- Initialize Podman Machine
- Install podman-compose
- Verify everything works

**Recommended**: Let the script handle everything.

---

### Option B: Manual Installation

If the automated script doesn't work:

```powershell
# 1. Install via Windows Package Manager
winget install RedHat.Podman

# 2. After installation, open a new PowerShell window and:
podman machine init
podman machine start

# 3. Install podman-compose
pip install podman-compose

# 4. Verify
podman --version
podman-compose --version
```

---

### Option C: Direct Download

If winget doesn't work:

1. Visit: https://podman.io/docs/installation/windows
2. Download the Windows installer
3. Run the installer
4. In PowerShell:
   ```powershell
   podman machine init
   podman machine start
   pip install podman-compose
   ```

---

## Step 2: Verify Installation

After installing, verify everything works:

```powershell
# Check Podman version
podman --version

# Check Podman Machine status
podman machine list

# Check podman-compose version
podman-compose --version

# Test Podman works
podman run --rm alpine echo "Podman is working!"
```

All commands should succeed without errors.

---

## Step 3: Start Your Application

Once Podman is installed and verified:

```powershell
# Navigate to your project
cd d:\Users\CNSHO\Documents\GitHub\Natpudan-

# Run the startup script
.\start-podman-compose.ps1
```

The script will:
1. Check Podman installation
2. Verify Podman Machine is running
3. Check environment configuration
4. Start all services
5. Show you access URLs

---

## Step 4: Access Your Application

After the startup script completes, open these URLs:

| Service | URL |
|---------|-----|
| Frontend (React) | http://127.0.0.1:3000 |
| Backend API | http://127.0.0.1:8000 |
| Database | 127.0.0.1:5432 |
| Redis Cache | 127.0.0.1:6379 |
| Task Dashboard | http://127.0.0.1:5555 |

**Start with the Frontend**: http://127.0.0.1:3000

---

## Common Issues & Quick Fixes

### Issue: "Podman: The term is not recognized"

**Solution**:
```powershell
# After installing via winget, open a NEW PowerShell window
# The PATH needs to be refreshed

# Or refresh manually:
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### Issue: "winget not found"

**Solution**: You're on Windows 10 or earlier
- Update Windows to latest version
- Or use Option B (manual installation)
- Or download directly from podman.io

### Issue: "podman-compose not found"

**Solution**:
```powershell
# Install or reinstall it
pip install podman-compose

# Or upgrade it
pip install --upgrade podman-compose

# Verify
podman-compose --version
```

### Issue: "Podman Machine creation timeout"

**Solution**:
```powershell
# Cancel the current process (Ctrl+C)
# Try without graphics:
podman machine init --no-graphics
podman machine start --no-graphics
```

### Issue: "Services won't start"

**Solution**:
1. Check Podman is running:
   ```powershell
   podman machine list
   ```
   Should show status as "running"

2. Check logs:
   ```powershell
   podman-compose logs
   ```

3. See troubleshooting guide:
   ```powershell
   .\PODMAN_TROUBLESHOOTING.md
   ```

---

## Useful Commands (After Installation)

```powershell
# Start services
podman-compose up -d

# View status
podman-compose ps

# View logs
podman-compose logs -f

# Stop services
podman-compose down

# Restart a service
podman-compose restart backend

# Execute command
podman-compose exec backend bash
```

See `PODMAN_QUICK_REFERENCE.md` for more commands.

---

## Documentation Files

| File | Purpose |
|------|---------|
| **PODMAN_README.md** | Quick overview |
| **PODMAN_SETUP.md** | Detailed configuration guide |
| **PODMAN_QUICK_REFERENCE.md** | Command cheat sheet |
| **PODMAN_TROUBLESHOOTING.md** | Solutions for problems |
| **PODMAN_WINDOWS_INSTALLATION.md** | Windows installation details |
| **install-podman.ps1** | Automated installation script |
| **start-podman-compose.ps1** | Application startup script |

---

## What to Do Next

1. **Install Podman**:
   ```powershell
   .\install-podman.ps1
   ```

2. **Wait for installation to complete** (~5-10 minutes)

3. **Start your application**:
   ```powershell
   .\start-podman-compose.ps1
   ```

4. **Open http://127.0.0.1:3000 in your browser**

5. **Done!** Your application is running.

---

## If You Get Stuck

1. **Read the error message carefully** - It usually tells you what's wrong
2. **Check**: `PODMAN_TROUBLESHOOTING.md`
3. **Try the automated installer**: `.\install-podman.ps1`
4. **Check service logs**: `podman-compose logs`
5. **Restart Podman Machine**: 
   ```powershell
   podman machine stop
   podman machine start
   ```

---

## Need More Help?

- **Podman Documentation**: https://docs.podman.io/
- **Troubleshooting Guide**: `./PODMAN_TROUBLESHOOTING.md`
- **Command Reference**: `./PODMAN_QUICK_REFERENCE.md`
- **Setup Details**: `./PODMAN_SETUP.md`

---

## TL;DR - Quick Start

```powershell
# 1. Install
.\install-podman.ps1

# 2. Start app
.\start-podman-compose.ps1

# 3. Open browser
# http://127.0.0.1:3000
```

That's it! 🚀
