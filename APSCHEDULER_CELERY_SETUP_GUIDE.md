# APScheduler + Celery Setup Guide

## Overview
This guide walks you through setting up automatic knowledge base updates using **APScheduler + Celery** (Combined Option 2+3).

**What it does:**
- ✅ APScheduler runs inside FastAPI and schedules jobs
- ✅ Every 2 AM UTC, it submits a KB update task to Celery
- ✅ Celery worker processes the task independently (doesn't block API)
- ✅ Redis acts as the message broker between FastAPI and Celery
- ✅ Flower provides real-time monitoring dashboard

**Result:** Your API stays responsive while KB updates happen in the background! 🚀

---

## Prerequisites

### 1. **Python 3.10+ (already have)**
```powershell
python --version
```

### 2. **Redis Server**
Choose ONE option:

**Option A: Docker (Easiest)**
```powershell
.\start-redis.ps1
```
This automatically starts Redis in Docker.

**Option B: Windows Native**
Download from: https://github.com/microsoftarchive/redis/releases

**Option C: WSL2 (Linux Subsystem)**
```bash
wsl sudo apt-get install redis-server
wsl sudo service redis-server start
```

---

## Installation Steps

### Step 1: Install Dependencies
```powershell
cd backend
pip install -r requirements.txt
```

New packages added:
- `apscheduler` - Task scheduling
- `celery` - Background task worker
- `redis` - Message broker & result storage

### Step 2: Verify Redis Connection
```powershell
# If using Docker
.\start-redis.ps1

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

---

## How It Works

### Architecture
```
FastAPI (main.py)
  ├─ HTTP API (responds to requests)
  ├─ APScheduler (runs inside app)
  │  └─ Every 2 AM → Submits task to Redis
  │
Redis (Message Queue)
  ├─ Receives task from FastAPI
  └─ Stores task for Celery
  
Celery Worker (separate process)
  ├─ Connects to Redis
  ├─ Picks up task from queue
  └─ Executes KB update (takes 30-60 seconds)
  
Flower (monitoring - optional)
  └─ Web dashboard at http://localhost:5555
     Shows task status, worker health, etc.
```

### Timeline (Example: KB Update at 2 AM)
```
2:00:00 AM - APScheduler wakes up
2:00:01 AM - Submits task to Redis → Returns immediately (API responsive)
2:00:02 AM - FastAPI continues handling requests normally
2:00:03 AM - Celery worker picks up task
2:00:05 AM - Worker fetches papers from PubMed (30 seconds)
2:00:35 AM - Worker indexes papers into FAISS
2:01:00 AM - Task complete, result stored in Redis

→ ZERO downtime, API fully responsive! ✅
```

---

## Starting the System

### Terminal 1: Start Redis (if not using auto-start)
```powershell
.\start-redis.ps1
```

### Terminal 2: Start FastAPI (with APScheduler built-in)
```powershell
.\start-backend.ps1
# OR
cd backend
python -m uvicorn app.main:app --reload
```

You should see:
```
[INFO] [STARTING] Natpudan AI Medical Assistant...
[INFO] [OK] APScheduler started - KB updates scheduled for 2:00 AM UTC daily
[INFO] [STARTED] Application started - ...
```

✅ FastAPI is running with APScheduler inside!

### Terminal 3: Start Celery Worker
```powershell
.\start-celery-worker.ps1
```

You should see:
```
╔════════════════════════════════════════════════════════════════╗
║       Celery Worker - Knowledge Base Auto-Update              ║
╚════════════════════════════════════════════════════════════════╝

✅ Redis is accessible
🚀 Starting Celery Worker...

[2025-12-11 14:30:45,123: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-12-11 14:30:45,234: INFO/MainProcess] mingle: there are no remote workers -- disabling remote control
[2025-12-11 14:30:45,345: INFO/MainProcess] worker: Preparing bootsteps.
[2025-12-11 14:30:45,456: INFO/MainProcess] worker: Ready. (worker1@your-machine)
```

✅ Celery worker is running and waiting for tasks!

### Terminal 4 (Optional): Start Flower (Monitoring)
```powershell
.\start-flower.ps1
```

Then open: **http://localhost:5555**
- Username: `admin`
- Password: `admin`

You'll see:
- Active workers
- Queued tasks
- Completed tasks with execution time
- Task history

---

## Testing the Setup

### Test 1: Manual Task Submission
```powershell
# In PowerShell while backend is running
$uri = "http://localhost:8000/api/medical/knowledge/pubmed-auto-update"
$body = @{
    topics = @("diabetes", "hypertension")
    papers_per_topic = 3
    days_back = 7
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $uri -Method Post `
    -ContentType "application/json" `
    -Body $body

$response | ConvertTo-Json
```

Expected response:
```json
{
  "status": "success",
  "task_id": "abc123def456",
  "timestamp": "2025-12-11T14:45:30.123456",
  "result": {
    "topics_searched": 2,
    "papers_found": 6,
    "papers_indexed": 6,
    "errors": []
  }
}
```

### Test 2: Check Celery Task Status
```powershell
# In Python
python
>>> from app.tasks import update_knowledge_base
>>> from app.celery_config import get_celery_app
>>> 
>>> celery_app = get_celery_app()
>>> 
>>> # Submit task
>>> task = update_knowledge_base.delay(
...     topics=["diabetes"],
...     papers_per_topic=3,
...     days_back=7
... )
>>> 
>>> # Check status
>>> print(task.id)  # Task ID
>>> print(task.status)  # PENDING, STARTED, SUCCESS, FAILURE
>>> print(task.result)  # Result when complete
>>> 
>>> # Wait for completion (blocking)
>>> result = task.get(timeout=120)
>>> print(result)
```

### Test 3: Monitor with Flower
Open http://localhost:5555 and:
1. Click **"Tasks"** tab
2. Submit a manual update task
3. Watch it execute in real-time on the dashboard
4. See execution time, memory usage, status

### Test 4: Schedule Verification
```powershell
# Check APScheduler is running
cd backend
python

>>> from apscheduler.schedulers.background import BackgroundScheduler
>>> from apscheduler.triggers.cron import CronTrigger
>>> 
>>> # The scheduler is running inside FastAPI if you see:
>>> # [INFO] [OK] APScheduler started - KB updates scheduled for 2:00 AM UTC daily
```

---

## Configuration

### Change Update Schedule
Edit `backend/app/main.py`, find the scheduler setup (around line 100):

```python
# Change from 2:00 AM to 3:00 AM UTC
scheduler.add_job(
    schedule_kb_update,
    CronTrigger(hour=3, minute=0),  # ← Change here
    id="kb_daily_update",
    name="Daily Knowledge Base Update",
    replace_existing=True
)
```

### Add More Topics
Edit `backend/app/main.py`, in the `schedule_kb_update()` function:

```python
def schedule_kb_update():
    task = update_knowledge_base.delay(
        topics=[
            "diabetes mellitus",
            "hypertension",
            "heart disease",
            "cancer",
            # Add more topics here:
            "stroke",
            "chronic kidney disease",
            "asthma"
        ],
        papers_per_topic=5,
        days_back=7
    )
```

### Adjust Papers Per Topic
```python
# Lower number = faster, fewer papers
# Higher number = slower, more papers
result = pubmed.auto_update_knowledge_base(
    vector_kb=kb,
    topics=topics,
    papers_per_topic=10,  # ← Change this
    days_back=7
)
```

---

## Environment Variables

Set these to customize behavior:

```bash
# Redis connection (default: redis://localhost:6379/0)
REDIS_URL=redis://localhost:6379/0

# OpenAI API key (required for KB updates)
OPENAI_API_KEY=sk-...

# Database (for storing update history)
DATABASE_URL=sqlite:///./natpudan.db

# Log level
LOG_LEVEL=INFO
```

---

## Troubleshooting

### Error: "Connection refused (Errno 111)"
**Problem:** Redis not running
**Solution:**
```powershell
.\start-redis.ps1
# Wait 3 seconds, then check
redis-cli ping
```

### Error: "ImportError: No module named 'celery'"
**Problem:** Dependencies not installed
**Solution:**
```powershell
cd backend
pip install -r requirements.txt
```

### Tasks Not Executing
**Problem:** Celery worker not running
**Solution:**
```powershell
# Terminal 3: Start Celery
.\start-celery-worker.ps1
```

### Scheduler Not Starting
**Problem:** APScheduler error in FastAPI logs
**Solution:** Check logs, restart backend:
```powershell
.\start-backend.ps1
```

### Can't Connect to Flower
**Problem:** Flower not running or wrong port
**Solution:**
```powershell
.\start-flower.ps1  # Uses port 5555 by default
# Then visit: http://localhost:5555
```

---

## Production Deployment

### Docker Compose
Replace your current `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery:
    build: ./backend
    command: celery -A app.celery_config worker --loglevel=info
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://user:pass@postgres/db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./backend:/app

  flower:
    build: ./backend
    command: celery -A app.celery_config flower
    ports:
      - "5555:5555"
    depends_on:
      - redis

  fastapi:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}

volumes:
  redis_data:
```

Then:
```bash
docker-compose up
```

### Systemd Service (Linux)
Create `/etc/systemd/system/natpudan-celery.service`:

```ini
[Unit]
Description=Natpudan Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=celery
WorkingDirectory=/opt/natpudan/backend
ExecStart=/opt/natpudan/backend/venv/bin/celery -A app.celery_config worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable natpudan-celery
sudo systemctl start natpudan-celery
```

---

## Monitoring & Maintenance

### Check Task History
```bash
redis-cli
> KEYS "*celery*"  # See all celery keys
> GET "celery-task-meta-<task_id>"  # Get task result
```

### Clear Old Tasks
```bash
# Redis CLI
> FLUSHDB  # Clear all (careful!)
> 
# Or delete specific keys
> DEL celery-task-meta-old-task-id
```

### View Logs
```bash
# FastAPI logs (includes APScheduler)
.\start-backend.ps1

# Celery worker logs
.\start-celery-worker.ps1

# Flower web logs
.\start-flower.ps1
```

---

## Files Created

1. **backend/celery_config.py** - Celery configuration
2. **backend/app/tasks.py** - Background task definitions
3. **backend/kb_update_config.json** - KB update configuration
4. **start-celery-worker.ps1** - Start Celery worker
5. **start-redis.ps1** - Start Redis
6. **start-flower.ps1** - Start Flower dashboard
7. **backend/requirements.txt** - Updated with Celery, APScheduler, Redis

---

## Summary

| Component | Purpose | Status |
|-----------|---------|--------|
| **APScheduler** | Schedule jobs inside FastAPI | ✅ Running with FastAPI |
| **Celery** | Execute tasks in worker process | ✅ Separate process (Terminal 3) |
| **Redis** | Message queue between FastAPI & Celery | ✅ Running (Terminal 1) |
| **Flower** | Monitor tasks in real-time | ✅ Dashboard at 5555 |
| **Knowledge Base Updates** | Every 2 AM UTC automatically | ✅ Scheduled & executing |

You now have a **production-ready** automatic KB update system! 🎉

Questions? Check logs or reach out. Enjoy! 🚀
