# Background Services Status & Setup Guide

## Current Status (December 14, 2025)

### ✅ Running Services
- **Backend (FastAPI)**: http://127.0.0.1:8000 - ✅ RUNNING
- **Frontend (React)**: http://127.0.0.1:5173 - ✅ RUNNING
- **Database**: SQLite - ✅ CONNECTED
- **OpenAI API**: - ✅ CONFIGURED
- **Knowledge Base**: 0 documents indexed - ✅ LOADED

### ❌ Not Running Services
- **Redis**: Message broker - ❌ NOT INSTALLED
- **Celery Worker**: Background task processor - ❌ NOT RUNNING (requires Redis)
- **Flower**: Task monitoring dashboard - ❌ NOT RUNNING (requires Celery)

---

## Impact on Application

### What Works WITHOUT Redis/Celery/Flower:
✅ All core features are fully functional:
- Patient intake and management
- AI-powered diagnosis and chat
- Prescription generation
- Knowledge base search (existing documents)
- Treatment plans and discharge summaries
- Analytics and reporting
- PDF uploads (uses local queue processor)
- All API endpoints

### What Doesn't Work:
❌ **Automated scheduled tasks:**
- Daily knowledge base updates (scheduled for 2 AM UTC)
- Background processing of long-running tasks
- Distributed task queue

❌ **Monitoring:**
- Flower web dashboard (http://localhost:5555)
- Real-time task monitoring

---

## Setup Instructions

### Option 1: Docker Desktop (RECOMMENDED)

**Easiest and most reliable approach**

1. **Install Docker Desktop:**
   - Download: https://www.docker.com/products/docker-desktop
   - Install and **restart your computer**
   - Verify: `docker --version`

2. **Start Redis:**
   ```powershell
   .\start-redis.ps1
   ```
   - Port: 6379
   - URL: redis://localhost:6379

3. **Start Celery Worker:**
   ```powershell
   .\start-celery-worker.ps1
   ```
   - Concurrency: 4 workers
   - Processes long-running tasks

4. **Start Flower (Optional):**
   ```powershell
   .\start-flower.ps1
   ```
   - Dashboard: http://localhost:5555
   - Username: admin
   - Password: admin

---

### Option 2: Windows Native Redis (Memurai)

**If you can't use Docker**

1. **Install Memurai Developer:**
   ```powershell
   winget install Memurai.MemuraiDeveloper
   ```
   OR download from: https://www.memurai.com/get-memurai

2. **Start Memurai service:**
   ```powershell
   net start Memurai
   ```

3. **Update backend/.env:**
   ```
   REDIS_URL=redis://localhost:6379/0
   ```

4. **Start Celery Worker:**
   ```powershell
   .\start-celery-worker.ps1
   ```

5. **Start Flower:**
   ```powershell
   .\start-flower.ps1
   ```

---

### Option 3: WSL2 (Linux Subsystem)

**If you have Windows Subsystem for Linux**

1. **Install Redis in WSL:**
   ```bash
   wsl sudo apt-get update
   wsl sudo apt-get install redis-server
   ```

2. **Start Redis:**
   ```bash
   wsl sudo service redis-server start
   ```

3. **Update backend/.env:**
   ```
   REDIS_URL=redis://localhost:6379/0
   ```

4. **Start Celery Worker:**
   ```powershell
   .\start-celery-worker.ps1
   ```

---

## Workarounds Without Redis/Celery

### Manual Knowledge Base Updates

Instead of waiting for the 2 AM scheduled update, run manual updates:

```powershell
.\manual-kb-update.ps1
```

OR via API:
```powershell
$body = @{
    topics = @("diabetes", "hypertension", "cancer")
    papers_per_topic = 5
    days_back = 7
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/medical/knowledge/pubmed-auto-update" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Alternative Task Processing

The app uses a **local queue processor** for PDF uploads:
- Runs in-process with FastAPI
- Processes files in batches
- No Redis required
- Limited to lighter workloads

---

## Troubleshooting

### Redis Connection Errors
```
[SCHEDULER] ❌ Error submitting task: Error connecting to Redis
```

**Solution:** Ensure Redis is running:
```powershell
# If using Docker:
docker ps | findstr redis

# If using Memurai:
Get-Service Memurai

# If using WSL:
wsl sudo service redis-server status
```

### Celery Worker Not Starting
```
[ERROR] Failed to start worker: No broker configured
```

**Solution:** 
1. Check Redis is running
2. Verify `REDIS_URL` in `backend/.env`
3. Test Redis connection:
   ```powershell
   Test-NetConnection -ComputerName localhost -Port 6379
   ```

### Docker Service Marked for Deletion
```
Failed to create service: The specified service has been marked for deletion
```

**Solution:**
1. Restart your computer
2. Reinstall Docker Desktop
3. OR use Memurai instead

---

## Recommended Setup

### For Development:
- ✅ Run backend + frontend only
- ✅ Use manual KB updates when needed
- ⚠️ Redis/Celery/Flower optional

### For Production:
- ✅ Install Docker Desktop
- ✅ Start Redis, Celery, Flower
- ✅ Enable automated scheduling
- ✅ Monitor tasks with Flower

---

## Quick Start Commands

### Start Everything (with Redis/Celery):
```powershell
# Terminal 1: Redis
.\start-redis.ps1

# Terminal 2: Celery Worker
.\start-celery-worker.ps1

# Terminal 3: Flower (optional)
.\start-flower.ps1

# Terminal 4: Backend
.\start-backend.ps1

# Terminal 5: Frontend
cd frontend; npm run dev
```

### Start Minimal (without Redis/Celery):
```powershell
# Terminal 1: Backend
.\start-backend.ps1

# Terminal 2: Frontend
cd frontend; npm run dev
```

---

## Services Summary

| Service | Port | Status | Required | Purpose |
|---------|------|--------|----------|---------|
| Backend | 8000 | ✅ Running | Yes | API server |
| Frontend | 5173 | ✅ Running | Yes | Web UI |
| Redis | 6379 | ❌ Not Running | For scheduling | Message broker |
| Celery | N/A | ❌ Not Running | For scheduling | Task worker |
| Flower | 5555 | ❌ Not Running | Optional | Task monitor |

---

## Next Steps

1. **Decide if you need background tasks**
   - Yes → Install Docker + Start Redis/Celery
   - No → Continue using app as-is

2. **For production deployment:**
   - Set up Redis in production
   - Configure Celery workers
   - Enable Flower for monitoring

3. **For immediate use:**
   - App is fully functional without Redis/Celery
   - Use manual KB updates when needed

---

**Last Updated:** December 14, 2025
