# APScheduler + Celery - Quick Start (5 Minutes)

## The 4-Terminal Setup

### Terminal 1: Redis
```powershell
.\start-redis.ps1
# OR
docker run -d -p 6379:6379 redis:latest
```

### Terminal 2: FastAPI (with APScheduler)
```powershell
.\start-backend.ps1
# Should see: "[OK] APScheduler started - KB updates scheduled for 2:00 AM UTC daily"
```

### Terminal 3: Celery Worker
```powershell
.\start-celery-worker.ps1
# Should see: "worker: Ready"
```

### Terminal 4: Flower (Optional - Monitoring)
```powershell
.\start-flower.ps1
# Open: http://localhost:5555 (admin/admin)
```

---

## What's Running?

| Process | Port | What It Does |
|---------|------|-------------|
| Redis | 6379 | Message queue (broker) |
| FastAPI | 8000 | Your API + APScheduler inside |
| Celery | (background) | Executes KB updates |
| Flower | 5555 | Monitor dashboard |

---

## Automatic KB Updates

✅ **Happens every day at 2 AM UTC automatically**

**What happens:**
1. APScheduler in FastAPI wakes up at 2 AM
2. Submits "update KB" task to Redis queue
3. Celery worker picks it up and executes
4. FastAPI stays 100% responsive (no blocking)
5. Results stored in Redis for monitoring

---

## Test It Manually

```powershell
$uri = "http://localhost:8000/api/medical/knowledge/pubmed-auto-update"
$body = @{ topics = @("diabetes"); papers_per_topic = 3; days_back = 7 } | ConvertTo-Json

Invoke-RestMethod -Uri $uri -Method Post -ContentType "application/json" -Body $body
```

Watch it execute in Flower dashboard! 📊

---

## Change Schedule (if needed)

Edit `backend/app/main.py`, around line 100:

```python
# Change from 2 AM to 3 AM UTC
scheduler.add_job(
    schedule_kb_update,
    CronTrigger(hour=3, minute=0),  # ← 3 AM
    id="kb_daily_update",
    name="Daily Knowledge Base Update",
    replace_existing=True
)
```

---

## Troubleshoot

| Problem | Solution |
|---------|----------|
| Connection refused | Run `.\start-redis.ps1` |
| "No module named celery" | Run `pip install -r requirements.txt` |
| Tasks not executing | Check Celery worker (Terminal 3) running |
| Can't access Flower | Make sure `.\start-flower.ps1` is running |

---

## Files Created

- `backend/celery_config.py` - Celery config
- `backend/app/tasks.py` - Task definitions
- `backend/kb_update_config.json` - KB settings
- `start-celery-worker.ps1` - Start worker
- `start-redis.ps1` - Start Redis
- `start-flower.ps1` - Start monitor
- `APSCHEDULER_CELERY_SETUP_GUIDE.md` - Full guide

---

## Next Steps

1. ✅ Run all 4 terminals
2. ✅ See APScheduler message in FastAPI logs
3. ✅ Test manual update via API
4. ✅ Watch Flower dashboard
5. ✅ Configure topics/schedule if needed

**Done!** Your KB updates automatically now! 🎉
