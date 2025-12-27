# Podman Deployment Setup & Troubleshooting Guide

## Status: ✅ FIXED

The `deploy-podman-production.ps1` script has been fixed and is ready to use.

## What Was Fixed

- Replaced Unicode checkmark characters (✓) with ASCII [OK] to fix PowerShell syntax errors
- Script now runs without parsing errors

## Prerequisites

### 1. Install Podman (Windows)
```powershell
# Option A: Using Chocolatey
choco install podman

# Option B: Manual installation
# Download from: https://podman.io/docs/installation/windows
# Run installer and follow prompts
```

### 2. Install podman-compose
```powershell
pip install podman-compose
```

### 3. Start Podman Machine (first time only)
```powershell
podman machine init
podman machine start
```

### 4. Verify Installation
```powershell
podman --version
podman-compose --version
podman machine list
```

---

## Deployment Workflow

### Option A: Full Production Deployment
```powershell
# Prepare environment file
cp .env.example .env.prod
# Edit .env.prod with your production settings

# Deploy with Podman
.\deploy-podman-production.ps1 -EnvFile .env.prod -Pull

# Expected output:
# [Deploy] [OK] Environment file found: .env.prod
# [Deploy] [OK] Podman: ...
# [Deploy] [OK] Podman Compose: ...
# [Deploy] Containers stopped (or warning if first run)
# [Deploy] Building container images...
# [Deploy] [OK] Services started
# [Deploy] Waiting for services to be ready...
```

### Option B: Development with Docker Compose
```powershell
# Use standard docker-compose for local development
docker-compose up --build

# Or with Podman:
podman-compose up --build
```

### Option C: Simple Backend + Frontend (No Containers)
```powershell
# Use the simple startup script
.\start-backend-simple.ps1

# Opens two windows:
# 1. Backend (http://127.0.0.1:8000)
# 2. Frontend (http://127.0.0.1:5173)
```

---

## Troubleshooting

### Error: "Podman not found"
```powershell
# Install Podman from: https://podman.io/docs/installation/windows
# Then verify installation:
podman --version
```

### Error: "podman-compose not found"
```powershell
pip install podman-compose --upgrade
```

### Error: "no container with name ... found"
**This is normal on first run.** The script will:
1. Try to stop existing containers (none yet)
2. Continue with build and start
3. This warning can be safely ignored

### Podman Machine Not Starting
```powershell
# Check machine status
podman machine list

# If stuck, reset:
podman machine stop
podman machine rm
podman machine init
podman machine start
```

### Ports Already in Use
```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill process (example: PID 1234)
taskkill /PID 1234 /F

# Or use different ports in .env.prod
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

### Services Not Connecting
```powershell
# Check container logs
podman-compose -f docker-compose.yml --env-file .env.prod logs backend
podman-compose -f docker-compose.yml --env-file .env.prod logs frontend
podman-compose -f docker-compose.yml --env-file .env.prod logs postgres

# Restart services
podman-compose -f docker-compose.yml --env-file .env.prod restart
```

---

## Management Commands

### View Running Containers
```powershell
podman ps
podman-compose ps
```

### Stop Services
```powershell
podman-compose --env-file .env.prod down
```

### View Logs
```powershell
# All services
podman-compose --env-file .env.prod logs -f

# Specific service
podman-compose --env-file .env.prod logs -f backend
podman-compose --env-file .env.prod logs -f frontend
```

### Execute Commands in Container
```powershell
# Run command in backend container
podman-compose --env-file .env.prod exec backend python -c "..."

# Access database shell
podman-compose --env-file .env.prod exec postgres psql -U natpudan_user -d natpudan_db
```

### Remove Everything and Start Fresh
```powershell
# Warning: This deletes all data!
podman-compose --env-file .env.prod down -v
podman image prune -a
podman volume prune
```

---

## Environment File (.env.prod)

### Critical Variables (MUST CHANGE FOR PRODUCTION)
```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here     # Get from OpenAI dashboard
SECRET_KEY=your-256-char-random-secret-key      # Generate with: openssl rand -hex 32
DATABASE_URL=postgresql://user:pass@postgres:5432/natpudan_db
POSTGRES_PASSWORD=your-strong-database-password
```

### Production URLs
```bash
FRONTEND_URL=https://yourdomain.com
VITE_API_BASE_URL=https://api.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Optional Features
```bash
REDIS_URL=redis://redis:6379/0                  # Caching
SENTRY_DSN=https://...                          # Error tracking
```

---

## Access Points (After Deployment)

| Service | URL | Purpose |
|---------|-----|---------|
| Backend API | http://127.0.0.1:8000 | REST API endpoints |
| Frontend | http://127.0.0.1:3000 | Web application |
| API Docs | http://127.0.0.1:8000/docs | Swagger documentation |
| PostgreSQL | 127.0.0.1:5432 | Database |
| Redis | 127.0.0.1:6379 | Cache/Queue |

---

## Next Steps

1. **Update .env.prod** with your production settings
2. **Set OPENAI_API_KEY** from https://platform.openai.com/api-keys
3. **Generate SECRET_KEY** with: `openssl rand -hex 32`
4. **Run deployment**: `.\deploy-podman-production.ps1 -EnvFile .env.prod -Pull`
5. **Monitor logs**: `podman-compose logs -f`
6. **Verify access**: http://127.0.0.1:8000/docs

---

## Files Reference

- **Deployment Script**: [deploy-podman-production.ps1](./deploy-podman-production.ps1) ✅ FIXED
- **Production Env File**: [.env.prod](./.env.prod) ✅ CREATED
- **Docker Compose**: [docker-compose.yml](./docker-compose.yml)
- **Env Template**: [backend/.env.example](./backend/.env.example)
- **Simple Startup**: [start-backend-simple.ps1](./start-backend-simple.ps1)

---

## Status Summary

✅ **Podman deployment script fixed** - All syntax errors resolved  
✅ **Production environment file created** - Ready for customization  
✅ **Podman machine running** - Ready for container deployment  
✅ **docker-compose.yml available** - Full service definitions ready  
✅ **Documentation complete** - Comprehensive troubleshooting guide  

**Next: Update .env.prod and run deployment!**
