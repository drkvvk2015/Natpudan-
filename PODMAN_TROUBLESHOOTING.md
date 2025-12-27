# Podman Troubleshooting Guide for Natpudan AI

## Pre-flight Checks

Run this first if you encounter issues:

```powershell
# 1. Check Podman version
podman --version

# 2. Check Podman Compose version
podman-compose --version

# 3. Check Podman Machine status
podman machine list

# 4. Check Podman info
podman info

# 5. List containers
podman ps -a

# 6. List volumes
podman volume ls

# 7. List networks
podman network ls
```

## Common Issues & Solutions

### ❌ "Podman not found"

**Problem**: `podman: command not found`

**Solutions**:
```powershell
# 1. Check if Podman is installed
Get-Command podman

# 2. Install Podman if not present
choco install podman -y
# OR
scoop install podman

# 3. Verify installation
podman --version

# 4. If using WSL, install Podman in WSL:
wsl sudo apt-get install podman
```

---

### ❌ "podman-compose not found"

**Problem**: `podman-compose: command not found`

**Solutions**:
```powershell
# 1. Check if installed
Get-Command podman-compose

# 2. Install via pip
pip install podman-compose

# 3. Verify installation
podman-compose --version

# 4. If pip not in PATH, try:
python -m pip install podman-compose

# 5. On WSL:
wsl pip install podman-compose
```

---

### ❌ "Podman Machine not running"

**Problem**: 
```
Error: podman machine not initialized or running
```

**Solutions**:
```powershell
# 1. Check machine status
podman machine list

# 2. Initialize machine (if needed)
podman machine init

# 3. Start machine
podman machine start

# 4. Force start
podman machine start --force

# 5. If stuck, restart Windows and try again
Restart-Computer

# 6. SSH into machine to debug
podman machine ssh
```

---

### ❌ "Cannot connect to Podman socket"

**Problem**: 
```
Error: Cannot connect to Podman socket
```

**Solutions**:
```powershell
# 1. Verify machine is running
podman machine list
# Status should show "running"

# 2. Start machine
podman machine start

# 3. Check socket exists
podman machine inspect

# 4. Reset machine (destructive)
podman machine stop
podman machine rm
podman machine init
podman machine start

# 5. On WSL, check podman socket
wsl ls -la /run/podman/podman.sock
```

---

### ❌ "Port already in use"

**Problem**: 
```
Error: bind: address already in use
```

**Solutions**:
```powershell
# 1. Find process using the port
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess

# 2. Get process details
Get-Process -PID <PID>

# 3. Kill the process (if safe)
Stop-Process -PID <PID> -Force

# 4. Or change port in docker-compose.yml
# From: "8000:8000"
# To:   "8001:8000"

# 5. Restart services
podman-compose down
podman-compose up -d
```

---

### ❌ "Permission denied" errors

**Problem**: 
```
Error: permission denied while trying to connect to Podman daemon
```

**Solutions**:

On Windows (rootless mode is default and secure):
```powershell
# 1. Podman runs as current user, should work fine
# 2. If issues persist, restart Podman machine
podman machine stop
podman machine start

# 3. On WSL, add user to podman group
wsl sudo usermod -aG podman $USER
```

On Linux in WSL:
```bash
# Add user to podman group
sudo usermod -aG podman $USER

# Log out and back in for changes to take effect
exit
```

---

### ❌ "Compose file parsing error"

**Problem**: 
```
Error parsing docker-compose.yml
```

**Solutions**:
```powershell
# 1. Validate YAML syntax
podman-compose config

# 2. Check for tab characters (YAML hates tabs)
Get-Content docker-compose.yml | Select-String "`t"
# If output, replace tabs with spaces

# 3. Verify indentation (must be 2 spaces)
# Open in VS Code and use "Change All End of Line Sequence" if needed

# 4. Check for duplicate keys or syntax errors
code docker-compose.yml

# 5. Test with simpler compose file first
echo "version: '3'" | Out-File test-compose.yml
echo "services:" | Add-Content test-compose.yml
echo "  test:" | Add-Content test-compose.yml
echo "    image: alpine" | Add-Content test-compose.yml
podman-compose -f test-compose.yml up
podman-compose -f test-compose.yml down
```

---

### ❌ "Cannot pull images"

**Problem**: 
```
Error pulling image: connection refused
```

**Solutions**:
```powershell
# 1. Check network connectivity
Test-Connection 8.8.8.8

# 2. Check if Podman machine has network access
podman machine ssh ping 8.8.8.8

# 3. Try pulling a simple image
podman pull alpine

# 4. If behind proxy, configure:
podman machine ssh
# Inside the machine, edit /etc/containers/registries.conf

# 5. Restart machine to reset network
podman machine stop
podman machine start

# 6. Check available disk space
podman system info | Select-String "GraphRoot"
```

---

### ❌ "Database connection failed"

**Problem**: 
```
psycopg2.OperationalError: could not connect to server
```

**Solutions**:
```powershell
# 1. Check if PostgreSQL container is running
podman-compose ps

# 2. View PostgreSQL logs
podman-compose logs db

# 3. Test connection from host
podman-compose exec db psql -U physician_user -c "SELECT 1"

# 4. Verify network
podman network inspect physician-ai-network

# 5. Check PostgreSQL is listening
podman-compose exec db netstat -tlnp | grep 5432

# 6. Verify environment variables
podman-compose config | Select-String -Pattern "POSTGRES"

# 7. Restart database
podman-compose restart db

# 8. Full reset (destructive)
podman-compose down -v  # Removes volumes!
podman-compose up -d
```

---

### ❌ "Backend container keeps restarting"

**Problem**: Container exits immediately after starting

**Solutions**:
```powershell
# 1. Check logs
podman-compose logs backend

# 2. View last few logs
podman-compose logs --tail 100 backend

# 3. Check exit code
podman ps -a --format "{{.Names}}\t{{.Status}}" | Select-String backend

# 4. Rebuild image
podman-compose build --no-cache backend

# 5. Verify environment variables
podman-compose config | Select-String "OPENAI_API_KEY"

# 6. Check if dependencies are ready
podman-compose logs db

# 7. Try manual startup to see error
podman-compose up backend  # Don't use -d
```

---

### ❌ "Frontend not loading at localhost:3000"

**Problem**: Connection refused or blank page

**Solutions**:
```powershell
# 1. Check if frontend container is running
podman-compose ps frontend

# 2. View frontend logs
podman-compose logs frontend

# 3. Test port is open
Test-NetConnection -ComputerName 127.0.0.1 -Port 3000

# 4. Check frontend build
podman-compose exec frontend ls -la /app

# 5. Verify API connection in container
podman-compose exec frontend curl http://backend:8000/health

# 6. Clear browser cache
# Press Ctrl+Shift+Delete in browser or use DevTools

# 7. Rebuild frontend
podman-compose build --no-cache frontend
podman-compose up -d frontend

# 8. Check NODE_ENV
podman-compose config | Select-String "NODE_ENV"
```

---

### ❌ "Volume not mounting"

**Problem**: Files not visible in container

**Solutions**:
```powershell
# 1. List volumes
podman volume ls

# 2. Inspect volume mount
podman volume inspect postgres_data

# 3. Verify volume in container
podman-compose exec backend ls -la /app/data

# 4. Check file permissions
Get-Item ./backend/data -Force

# 5. Recreate volume
podman-compose down
podman volume rm postgres_data
podman-compose up -d

# 6. Use absolute paths in docker-compose.yml
# From: ./backend/data:/app/data
# To: ${PWD}/backend/data:/app/data

# 7. On WSL, mount from /mnt/c for better compatibility
```

---

### ❌ "Out of disk space"

**Problem**: 
```
No space left on device
```

**Solutions**:
```powershell
# 1. Check disk usage
podman system info | Select-String "GraphRoot"
Get-Item (podman system info | Select-String "GraphRoot")

# 2. Clean unused resources
podman system prune -a --volumes -f

# 3. Check image sizes
podman images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# 4. Remove unused images
podman image prune -a

# 5. On WSL, check WSL disk usage
wsl df -h

# 6. Expand WSL disk (if using WSL)
# See: https://docs.microsoft.com/en-us/windows/wsl/vhd
```

---

## Debug Commands

### Full System Diagnostics

```powershell
# Run comprehensive check
.\start-podman-compose.ps1  # or use PowerShell module
Import-Module ./podman-utils.psm1
Test-PodmanHealth
Get-PodmanStatus
```

### Container Inspection

```powershell
# Get detailed container info
podman inspect physician-ai-backend

# Check specific field
podman inspect physician-ai-backend --format='{{.State.Status}}'

# Get IP address
podman inspect physician-ai-backend --format='{{.NetworkSettings.IPAddress}}'
```

### Network Debugging

```powershell
# List all connections in container
podman-compose exec backend netstat -tlnp

# Test DNS
podman-compose exec backend nslookup db

# Ping other containers
podman-compose exec backend ping -c 4 db

# Check routing
podman-compose exec backend ip route
```

### Resource Monitoring

```powershell
# Real-time stats
podman stats

# Memory usage
podman stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}"

# CPU usage
podman stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}"
```

---

## Getting Help

1. **Check official docs**: https://docs.podman.io/
2. **Podman Compose issues**: https://github.com/containers/podman-compose/issues
3. **System logs**: Check `podman-compose logs -f`
4. **Machine SSH**: `podman machine ssh` for deep inspection
5. **Community**: Podman communities/forums

---

## Recovery Steps (Nuclear Option)

⚠️ **This destroys everything - use only if nothing else works:**

```powershell
# Stop and remove everything
podman-compose down -v

# Remove all containers
podman container rm -af

# Remove all images
podman image rm -af

# Remove all volumes
podman volume prune -af

# Remove all networks
podman network prune -f

# Clean system
podman system prune -af

# Stop machine
podman machine stop

# Optional: Recreate machine
podman machine rm
podman machine init
podman machine start

# Start fresh
podman-compose up -d
```

---

## Quick Reference

| Issue | Command |
|-------|---------|
| Check status | `podman-compose ps` |
| View logs | `podman-compose logs -f` |
| Restart | `podman-compose restart` |
| Hard reset | `podman-compose down -v && podman-compose up -d` |
| Machine start | `podman machine start` |
| Machine stop | `podman machine stop` |
| Cleanup | `podman system prune -af` |
| Health check | `podman-compose exec backend curl http://localhost:8000/health` |
