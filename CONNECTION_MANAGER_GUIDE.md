# Connection Manager - Port Mismatch Prevention System

## Overview

The Connection Manager system prevents port mismatch errors by providing centralized configuration and validation tools.

## Components

### 1. Centralized Configuration (`config/ports.json`)

Single source of truth for all port configurations:

```json
{
  "services": {
    "backend": {
      "dev": 8001,
      "prod": 8000
    },
    "frontend": {
      "dev": 5173,
      "prod": 3000
    }
  },
  "urls": {
    "backend": {
      "dev": "http://127.0.0.1:8001"
    }
  }
}
```

### 2. Port Configuration Validator (`scripts/check-ports.ps1`)

Validates that all `.env` files match the centralized configuration.

**Usage:**

```powershell
# Check for mismatches
.\scripts\check-ports.ps1

# Auto-fix mismatches
.\scripts\check-ports.ps1 -Fix
```

**What it checks:**
- ✓ Backend `.env` files (PORT setting)
- ✓ Frontend `.env` files (VITE_API_BASE_URL)
- ✓ Frontend `.env.development` (the file that caused our issue)
- ✓ WebSocket URLs

### 3. Connection Manager (`scripts/connection-manager.ps1`)

Validates live service connectivity and configuration consistency.

**Usage:**

```powershell
# Check current status
.\scripts\connection-manager.ps1

# Wait for services to be ready
.\scripts\connection-manager.ps1 -WaitForServices -Timeout 30

# Detailed health information
.\scripts\connection-manager.ps1 -Detailed
```

**What it checks:**
- ✓ Backend port listening
- ✓ Backend health endpoint responding
- ✓ Frontend port listening
- ✓ Frontend accessible
- ✓ **Configuration match between frontend and backend**

## Typical Workflow

### 1. Before Starting Services

Check configuration consistency:

```powershell
.\scripts\check-ports.ps1
```

If issues found, auto-fix:

```powershell
.\scripts\check-ports.ps1 -Fix
```

### 2. After Starting Services

Verify connectivity:

```powershell
.\scripts\connection-manager.ps1
```

Expected output:
```
✓ Backend: Listening on 8001
✓ Backend: Healthy
✓ Frontend: Listening on 5173  
✓ Frontend: Accessible
✓ Configuration: Matched
  Frontend → Backend: http://127.0.0.1:8001

System Status: ALL SYSTEMS GO ✓
```

### 3. In Startup Scripts

Add to `start-dev.ps1`:

```powershell
# Validate configuration before starting
.\scripts\check-ports.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Configuration issues detected. Fix with: .\scripts\check-ports.ps1 -Fix"
    exit 1
}

# Start services...

# Wait for services to be ready
.\scripts\connection-manager.ps1 -WaitForServices -Timeout 30
```

## Error Prevention

The Connection Manager prevents these common issues:

### Issue 1: Port Mismatch (What happened today)
- **Problem**: Frontend `.env.development` pointed to port 8000, backend on 8001
- **Detection**: `check-ports.ps1` compares all .env files against `ports.json`
- **Fix**: `check-ports.ps1 -Fix` updates the mismatched file

### Issue 2: Backend Not Started
- **Problem**: Frontend running but backend offline
- **Detection**: `connection-manager.ps1` checks if port is listening
- **Alert**: Shows "Backend: Not listening" in red

### Issue 3: Wrong Backend Port in Production
- **Problem**: Production frontend still pointing to dev backend
- **Detection**: Checks match the environment (dev/prod)
- **Prevention**: Validates before deployment

### Issue 4: Services Started in Wrong Order
- **Problem**: Frontend tries to connect before backend ready
- **Solution**: `connection-manager.ps1 -WaitForServices` waits for health check

## Integration Examples

### PowerShell Script

```powershell
# At start of any startup script
Write-Host "Validating configuration..."
& "$PSScriptRoot\scripts\check-ports.ps1" -Fix

# After starting services
Write-Host "Waiting for services..."
& "$PSScriptRoot\scripts\connection-manager.ps1" -WaitForServices -Timeout 30

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All systems ready!" -ForegroundColor Green
}
```

### GitHub Actions / CI

```yaml
- name: Validate Port Configuration
  run: |
    pwsh -File ./scripts/check-ports.ps1
    
- name: Wait for Services
  run: |
    pwsh -File ./scripts/connection-manager.ps1 -WaitForServices -Timeout 60
```

### Docker Compose

Add health check script:

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "pwsh", "-File", "/app/scripts/connection-manager.ps1"]
      interval: 10s
      timeout: 5s
      retries: 3
```

## Configuration Management

### Adding New Port

1. Update `config/ports.json`:
```json
{
  "services": {
    "myservice": {
      "dev": 9000,
      "description": "My new service"
    }
  }
}
```

2. Update `check-ports.ps1` to validate the new service

3. Update `connection-manager.ps1` to check the new service

### Changing Ports

1. Update `config/ports.json` only
2. Run `check-ports.ps1 -Fix` to update all .env files
3. Restart services

## Troubleshooting

### "Configuration mismatch detected"

```powershell
# See what's wrong
.\scripts\check-ports.ps1

# Auto-fix
.\scripts\check-ports.ps1 -Fix

# Restart affected services
```

### "Backend not responding"

```powershell
# Check if process is running
netstat -ano | findstr "8001"

# Check backend logs
Get-Content backend\logs\server.log -Tail 50

# Restart backend
.\start-backend.ps1
```

### "Frontend can't connect"

```powershell
# Verify configuration
.\scripts\connection-manager.ps1 -Detailed

# Check browser console for actual URL being called
# Compare with config/ports.json
```

## Best Practices

1. **Always validate before starting**: Run `check-ports.ps1` before `start-dev.ps1`

2. **Use centralized config**: Never hardcode ports in scripts; read from `ports.json`

3. **Check after changes**: Run `connection-manager.ps1` after any config change

4. **Add to CI/CD**: Validate configuration in deployment pipelines

5. **Document port changes**: Update `ports.json` description when changing ports

## Future Enhancements

Potential improvements:

- [ ] Auto-generate `.env` files from `ports.json`
- [ ] Service discovery (auto-detect running services)
- [ ] Port conflict resolution (auto-select free ports)
- [ ] Configuration hot-reload (update without restart)
- [ ] Dashboard UI for connection status

---

**Result**: No more port mismatch errors! 🎉
