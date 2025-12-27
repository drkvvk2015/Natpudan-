# Podman Deployment - TLS Certificate Issue & Solutions

## Current Issue

**Error**: `tls: failed to verify certificate: x509: certificate signed by unknown authority`

**Cause**: Podman on Windows has TLS certificate verification issues when pulling from Docker Hub.

---

## Solution Options

### Option 1: Use Native Development (No Containers) ✅ RECOMMENDED FOR DEV

```powershell
# Simple startup - backend + frontend, no Docker/Podman complexity
.\start-dev-native.ps1
```

**Pros**:
- No container overhead
- Direct access to code and logs
- Instant feedback during development
- Works perfectly for local testing

**Cons**:
- Doesn't match production environment exactly
- Requires Python and Node.js installed locally

**When to use**: Development, testing, debugging

---

### Option 2: Fix Podman TLS Issues (For Production)

#### Step 1: Disable TLS Certificate Verification (Not Secure - Dev Only)
```powershell
# Edit Podman machine config
podman machine stop
podman machine rm

# Recreate without TLS verification
podman machine init --tls-verify=false
podman machine start
```

⚠️ **WARNING**: This is insecure and should ONLY be used in development/testing environments!

#### Step 2: Use Docker Desktop Instead (Easier)
```powershell
# Install Docker Desktop (includes docker-compose)
# https://www.docker.com/products/docker-desktop

# Then use regular docker-compose
docker-compose -f docker-compose.yml --env-file .env.prod up --build
```

#### Step 3: Pre-build Images Offline
```powershell
# Pull images from different registry (without TLS issues)
podman pull registry.k8s.io/pause

# Or use local caching:
podman-compose build --no-cache
```

---

## Recommended Approach

### For Development ✅
```powershell
.\start-dev-native.ps1
```
- Uses local Python/Node
- No container issues
- Perfect for coding and testing

### For Production 🏢
```powershell
# Use Docker Desktop instead of Podman
docker-compose -f docker-compose.yml --env-file .env.prod up -d --build

# Or fix Podman TLS and use:
podman-compose -f docker-compose.yml --env-file .env.prod up -d --build
```

---

## Files Available

| File | Purpose | When to Use |
|------|---------|------------|
| [start-dev-native.ps1](./start-dev-native.ps1) | Native Python + Node startup | Development ✅ |
| [start-backend-simple.ps1](./start-backend-simple.ps1) | Manual backend + frontend | Manual control |
| [deploy-podman-production.ps1](./deploy-podman-production.ps1) | Container deployment | Production (after TLS fix) |
| [docker-compose.yml](./docker-compose.yml) | Service definitions | Docker or Podman |

---

## Quick Start (Recommended)

```powershell
# Option A: Native development (no containers)
.\start-dev-native.ps1

# Option B: Use Docker Desktop if you have it
docker-compose --env-file .env.prod up --build

# Option C: Fix Podman and use it
podman machine stop
podman machine init --insecure
podman machine start
podman-compose --env-file .env.prod up --build
```

---

## Environment Setup

### For Native Development
```bash
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env

# Frontend
cd frontend
npm install
cp .env.example .env
```

### For Docker/Podman
```bash
cp .env.example .env.prod
# Edit with production settings
# Then: docker-compose -f docker-compose.yml --env-file .env.prod up --build
```

---

## Next Steps

1. **For Local Development**: Run `.\start-dev-native.ps1`
2. **For Production**: Install Docker Desktop or fix Podman TLS
3. **For Testing**: Use native development, then test containers separately

---

## Troubleshooting

### "Module not found" errors
```powershell
cd backend
python -m pip install -r requirements.txt --upgrade
```

### Port conflicts
```powershell
# Change ports in .env files
BACKEND_PORT=8001
FRONTEND_PORT=5174
```

### Database initialization
```powershell
cd backend
python init_db_manual.py
```

---

**Status**: ✅ Native development ready, Podman production setup available
