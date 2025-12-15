# 🚀 Natpudan AI - Complete Debug Setup (5-Minute Quick Start)

## Prerequisites Check

Ensure Docker Desktop is installed and running:
```powershell
docker --version  # Should show: Docker version XX.XX.XX
docker ps         # Should succeed without errors
```

---

## Step 1: Start Everything (One Command)

```powershell
# Navigate to project root
cd D:\Users\CNSHO\Documents\GitHub\Natpudan-

# Start all services
.\start-debug-full.ps1
```

This will automatically start:
- ✅ Docker services (PostgreSQL, Redis, Nginx)
- ✅ FastAPI Backend (port 8000)
- ✅ Celery Worker (background tasks)
- ✅ Flower Dashboard (monitoring)
- ✅ React Frontend (port 5173)

---

## Step 2: Open Dashboards in Browser

Once the script completes, open these tabs:

### 1. **Frontend** (React App)
```
http://localhost:5173
```

### 2. **Backend API Docs** (Test endpoints)
```
http://localhost:8000/docs
```

### 3. **Flower Dashboard** (Monitor Celery)
```
http://localhost:5555
Username: admin
Password: admin
```

### 4. **Backend Health Check**
```
http://localhost:8000/health
```

---

## Step 3: Monitor Services

Each service runs in its own terminal. Watch for:

### Backend Terminal
```
[INFO] GET /api/auth/login - 200 OK
[INFO] WebSocket connected: user_123
```

### Celery Worker Terminal
```
[INFO] app.tasks: Received task: process_pdf
[INFO] Task succeeded in 2.3s
```

### Frontend Terminal
```
VITE v4.X.X ready in XXX ms

  ➜  Local:   http://127.0.0.1:5173/
  ➜  press h to show help
```

---

## Common Tasks

### Test API Endpoint

1. Open **http://localhost:8000/docs**
2. Find any endpoint (e.g., `/api/auth/login`)
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. Watch response below

### Monitor Celery Task

1. Open **http://localhost:5555** (Flower)
2. Click **Active** tab
3. Trigger a long-running task from frontend
4. Watch it execute in real-time
5. See task details, timing, worker info

### Check Database

```powershell
# Connect to database
docker exec -it physician-ai-db psql -U physician_user -d physician_ai

# List tables
\dt

# Query users
SELECT * FROM users;

# Exit
\q
```

### Check Redis

```powershell
# Connect to Redis
docker exec -it physician-ai-redis redis-cli

# Test connection
PING  # Returns: PONG

# View keys
KEYS *

# Get specific key
GET <key>

# Exit
EXIT
```

---

## Troubleshooting

### Services won't start
```powershell
# Check Docker is running
docker ps

# If Docker isn't responding, restart Docker Desktop
# Then try again:
.\start-debug-full.ps1
```

### Port already in use
```powershell
# Find what's using port 8000
Get-NetTCPConnection -LocalPort 8000

# Kill it
Stop-Process -Id <PID> -Force
```

### Backend crashes on startup
```powershell
# Check backend logs
docker logs physician-ai-backend

# Try restarting
docker-compose restart backend
```

### Frontend can't connect to backend
```powershell
# Check backend is running
curl http://localhost:8000/health

# Check browser console (F12) for errors
# Look for CORS or network errors
```

### Celery tasks not running
```powershell
# Check Redis is running
docker exec physician-ai-redis redis-cli PING

# Check Celery worker is running
# (should see "Worker ready" in Celery terminal)

# Check Flower dashboard
http://localhost:5555
```

---

## Service URLs Reference

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **Frontend** | 5173 | http://localhost:5173 | React App |
| **Backend** | 8000 | http://localhost:8000 | API Server |
| **Backend Docs** | 8000 | http://localhost:8000/docs | Swagger UI |
| **Flower** | 5555 | http://localhost:5555 | Task Monitor |
| **Redis** | 6379 | redis://localhost:6379 | Message Broker |
| **PostgreSQL** | 5432 | psql://localhost:5432 | Database |

---

## Keyboard Shortcuts

### In Any Terminal
- **Ctrl + C** - Stop service
- **Clear** - Clear screen
- **Exit** - Close terminal

### In Browser
- **F12** - Open DevTools
- **Ctrl + Shift + K** - Open Console
- **Ctrl + Shift + E** - Open Network tab
- **Ctrl + Shift + I** - Open Inspector

### In Flower Dashboard
- **Refresh** - F5 or Cmd+R
- **View Task Details** - Click task in list
- **Revoke Task** - Right-click task

---

## Advanced Debugging

### Full Diagnostic Report
```powershell
# Run diagnostic script
.\diagnose.ps1

# Shows:
# ✓ Python version
# ✓ Virtual environment status
# ✓ Docker containers
# ✓ Service ports
# ✓ Database connection
# ✓ Redis status
# ✓ Running tasks
```

### Backend Only
```powershell
# If you only want backend (no frontend, no Celery)
.\start-debug-full.ps1 -NoFrontend
```

### Docker Only
```powershell
# If you only want Docker services (no backend/frontend)
.\start-debug-full.ps1 -DockerOnly
```

### Check All Logs
```powershell
# Follow backend logs in real-time
docker logs -f physician-ai-backend

# View recent logs
docker logs --tail 50 physician-ai-backend

# View with timestamps
docker logs --timestamps physician-ai-backend

# View database logs
docker logs -f physician-ai-db

# View Redis logs
docker logs -f physician-ai-redis
```

---

## Next: Making Changes

### Edit Backend Code
1. Edit files in `backend/app/`
2. Backend auto-reloads (check terminal)
3. Test with Swagger UI: http://localhost:8000/docs

### Edit Frontend Code
1. Edit files in `frontend/src/`
2. Frontend hot-reloads automatically
3. Check http://localhost:5173

### Create Database Migration
```powershell
# In backend directory
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Add Celery Task
1. Create in `backend/app/tasks.py`
2. Call from API endpoint
3. Monitor in Flower Dashboard

---

## Stop Everything

### Graceful Shutdown
```powershell
# Press Ctrl+C in each terminal window
# Or type "exit" and press Enter
```

### Complete Cleanup
```powershell
# Stop all Docker containers
docker-compose down

# Remove volumes (clears data)
docker-compose down -v

# Restart everything
.\start-debug-full.ps1
```

---

## What's Running

```
Your Computer
├── Frontend (React on :5173)
│   └── Makes API calls to Backend
├── Backend (FastAPI on :8000)
│   ├── Handles HTTP requests
│   ├── Manages database
│   └── Schedules tasks
├── Celery Worker
│   └── Executes background jobs
├── Flower (on :5555)
│   └── Shows Celery task status
└── Docker Containers
    ├── PostgreSQL (database)
    ├── Redis (message broker)
    └── Nginx (reverse proxy)
```

---

## Support

**Something not working?**

1. Run diagnostic: `.\diagnose.ps1`
2. Check logs: `docker logs physician-ai-backend`
3. Check browser console: F12
4. Verify Docker: `docker ps`

**Still stuck?**
- Check DEBUG_SETUP_GUIDE.md for detailed docs
- Review the troubleshooting section above
- Check project README.md

---

## 🎉 You're Ready!

```powershell
.\start-debug-full.ps1
```

Then open:
- http://localhost:5173 (Frontend)
- http://localhost:8000/docs (API Docs)
- http://localhost:5555 (Flower)

**Happy debugging!** 🚀
