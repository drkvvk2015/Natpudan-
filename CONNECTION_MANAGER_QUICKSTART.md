# Connection Manager - Quick Reference

## Problem Solved
**Prevents port mismatch errors** like the one we experienced where frontend `.env.development` pointed to port 8000 while backend ran on port 8001.

## Tools Available

### 1. Connection Manager (`scripts/connection-manager.ps1`)
**Checks live system status**

```powershell
# Quick status check
.\scripts\connection-manager.ps1

# Detailed health information
.\scripts\connection-manager.ps1 -Detailed
```

**Output Example:**
```
--- Backend Service ---
  Port: 8001
  Listening: YES
  Health: HEALTHY
    Database: True
    OpenAI: True

--- Frontend Service ---
  Port: 5173
  Listening: YES
  Accessible: YES

--- Configuration Status ---
  Config Match: YES
    Frontend -> Backend: http://127.0.0.1:8001

[SUCCESS] ALL SYSTEMS GO!
```

### 2. Port Configuration Validator (`scripts/check-ports.ps1`)
**Validates .env files match central config**

```powershell
# Check for mismatches
.\scripts\check-ports.ps1

# Auto-fix mismatches
.\scripts\check-ports.ps1 -Fix
```

**Output Example:**
```
[OK] ..\frontend\.env
     http://127.0.0.1:8001

[MISMATCH] ..\frontend\.env.development
           Expected: http://127.0.0.1:8001
           Actual:   http://127.0.0.1:8000

Run with -Fix to automatically correct
```

### 3. Central Configuration (`config/ports.json`)
**Single source of truth for all ports**

```json
{
  "services": {
    "backend": { "dev": 8001 },
    "frontend": { "dev": 5173 }
  },
  "urls": {
    "backend": { "dev": "http://127.0.0.1:8001" }
  }
}
```

## Typical Workflow

### Before Starting Services
```powershell
# 1. Validate configuration
.\scripts\check-ports.ps1

# 2. If mismatches found, auto-fix
.\scripts\check-ports.ps1 -Fix

# 3. Start services
.\start-backend.ps1
cd frontend; npm run dev
```

### After Starting Services
```powershell
# Verify everything is connected
.\scripts\connection-manager.ps1 -Detailed
```

### When Debugging Connection Issues
```powershell
# 1. Check what's running
.\scripts\connection-manager.ps1

# 2. Check configuration
.\scripts\check-ports.ps1

# 3. Fix if needed
.\scripts\check-ports.ps1 -Fix
```

## Integration in Startup Scripts

Add to your `start-dev.ps1`:

```powershell
# Validate ports before starting
Write-Host "Validating configuration..." -ForegroundColor Cyan
& ".\scripts\check-ports.ps1" -Fix

if ($LASTEXITCODE -ne 0) {
    Write-Host "Configuration issues detected!" -ForegroundColor Red
    exit 1
}

# Start services...
# (your existing startup code)

# Verify connectivity after starting
Start-Sleep -Seconds 5
& ".\scripts\connection-manager.ps1"
```

## What It Prevents

✅ **Port Mismatch** - Frontend pointing to wrong backend port  
✅ **Stale Configuration** - Old .env files with outdated ports  
✅ **Service Not Running** - Detects when backend/frontend offline  
✅ **Wrong Environment** - Dev config used in production  

## Files Checked

The validator checks these frontend files:
- `frontend/.env`
- `frontend/.env.development`
- `frontend/.env.local`
- `frontend/.env.production` (when applicable)

All compared against: `config/ports.json`

## Quick Commands

```powershell
# Status check
.\scripts\connection-manager.ps1

# Fix config
.\scripts\check-ports.ps1 -Fix

# Both (recommended workflow)
.\scripts\check-ports.ps1 -Fix ; .\scripts\connection-manager.ps1
```

---

**Result**: No more "backend offline" due to port mismatches! 🎉
