# 🎴 NATPUDAN AI DEBUG SETUP - QUICK REFERENCE CARD

## 🚀 FASTEST START

```powershell
cd D:\Users\CNSHO\Documents\GitHub\Natpudan-
.\start-debug-full.ps1
```

Then open:
- http://localhost:5173 (Frontend)
- http://localhost:8000/docs (API)
- http://localhost:5555 (Flower - admin/admin)

---

## 📊 PORT MAP

```
5173  → Frontend (React)
8000  → Backend (FastAPI)
8000  → /docs (Swagger UI)
8000  → /health (Health Check)
5555  → Flower (Task Monitor)
6379  → Redis (Broker)
5432  → PostgreSQL (Database)
```

---

## 🎯 COMMANDS

```powershell
# Start everything
.\start-debug-full.ps1

# Check health
.\diagnose.ps1

# Real-time monitor
.\monitor.ps1

# View backend logs
docker logs -f physician-ai-backend

# Connect to database
docker exec -it physician-ai-db psql -U physician_user -d physician_ai

# Connect to Redis
docker exec -it physician-ai-redis redis-cli

# Stop everything
docker-compose down

# Full reset
docker-compose down -v
```

---

## 📚 DOCS MAP

| File | Purpose | Time |
|------|---------|------|
| START_HERE.md | Execution | 2 min |
| QUICK_START_DEBUG.md | Getting started | 5 min |
| DEBUG_SETUP_GUIDE.md | Complete guide | 60 min |
| DEBUG_SCRIPTS_README.md | Scripts info | 15 min |
| DEBUG_SETUP_COMPLETE.md | Full summary | 10 min |
| DEBUG_SETUP_SUMMARY.txt | Visual | 5 min |

---

## 🔑 CREDENTIALS

| Service | User | Pass |
|---------|------|------|
| Flower | admin | admin |
| PostgreSQL | physician_user | secure_password |
| Database | - | physician_ai |

---

## ✅ VERIFICATION

After running startup:

```powershell
# Check all services
.\diagnose.ps1

# Should show 5/5 services UP
# ✓ Frontend
# ✓ Backend
# ✓ Flower
# ✓ Redis
# ✓ PostgreSQL
```

---

## 🌐 BROWSER TABS

Keep these open:

```
Tab 1: http://localhost:5173      → Frontend
Tab 2: http://localhost:8000/docs → API Testing
Tab 3: http://localhost:5555      → Flower Monitor
Tab 4: Browser DevTools (F12)     → Debugging
```

---

## 🔍 KEYBOARD SHORTCUTS

| Key | Action |
|-----|--------|
| F12 | Browser DevTools |
| Ctrl+C | Stop service |
| Ctrl+Shift+K | Console (DevTools) |
| Ctrl+Shift+E | Network (DevTools) |
| Ctrl+Shift+I | Inspector (DevTools) |
| F5 | Refresh |

---

## 🎯 QUICK WORKFLOWS

### Test API
1. Open: http://localhost:8000/docs
2. Find endpoint
3. Click "Try it out"
4. Execute
5. See response ✓

### Monitor Task
1. Open: http://localhost:5555
2. Login: admin/admin
3. Click "Active"
4. Trigger task from frontend
5. Watch execute ✓

### Debug Frontend
1. Open: http://localhost:5173
2. Press F12
3. Go to Console
4. Check for errors ✓

### Query Database
1. Run: `docker exec -it physician-ai-db psql -U physician_user -d physician_ai`
2. Execute: `SELECT * FROM users;`
3. Exit: `\q` ✓

---

## 🆘 QUICK FIXES

```powershell
# Port in use
Stop-Process -Id <PID> -Force

# Docker not running
# → Open Docker Desktop

# Backend error
docker logs physician-ai-backend

# Restart service
docker-compose restart backend

# Full reset
docker-compose down -v
.\start-debug-full.ps1
```

---

## 📋 CHECKLIST

- [ ] Docker Desktop running
- [ ] Run `.\start-debug-full.ps1`
- [ ] Wait 30-60 seconds
- [ ] Open http://localhost:5173
- [ ] Open http://localhost:8000/docs
- [ ] Open http://localhost:5555
- [ ] Test API endpoint
- [ ] Monitor Celery task
- [ ] Check backend logs ✓

---

## 🎓 FILES CREATED

### Scripts (3)
✓ start-debug-full.ps1  
✓ diagnose.ps1  
✓ monitor.ps1  

### Docs (8)
✓ START_HERE.md  
✓ QUICK_START_DEBUG.md  
✓ DEBUG_SETUP_GUIDE.md  
✓ DEBUG_SCRIPTS_README.md  
✓ DEBUG_SETUP_COMPLETE.md  
✓ DEBUG_SETUP_SUMMARY.txt  
✓ DEBUG_SETUP_INDEX.md  
✓ REFERENCE_CARD.md (this file)  

---

## 🚀 START NOW

```powershell
.\start-debug-full.ps1
```

Open browser:
- http://localhost:5173
- http://localhost:8000/docs
- http://localhost:5555

**Done!** 🎉

---

## 📞 HELP

- Quick start? → START_HERE.md
- Need more info? → QUICK_START_DEBUG.md
- Full details? → DEBUG_SETUP_GUIDE.md
- Check health? → .\diagnose.ps1
- Real-time? → .\monitor.ps1

---

## 💡 PRO TIPS

1. Keep terminals visible (see all logs)
2. Use `.\monitor.ps1` for real-time status
3. Use F12 DevTools for frontend debugging
4. Use Flower for task monitoring
5. Use `docker logs -f` to follow logs

---

## ✨ FEATURES

✅ Docker containers (Postgres, Redis, Nginx)  
✅ FastAPI backend (auto-reload)  
✅ React frontend (hot reload)  
✅ Celery worker (async tasks)  
✅ Flower dashboard (monitoring)  
✅ WebSocket support  
✅ Real-time APIs  
✅ Full logging  
✅ Health checks  
✅ API documentation  

---

## 🎬 VISUAL FLOW

```
START
  ↓
.\start-debug-full.ps1
  ↓
Wait 30-60 seconds
  ↓
Open browsers
  ├─ http://localhost:5173 (Frontend)
  ├─ http://localhost:8000/docs (API)
  └─ http://localhost:5555 (Flower)
  ↓
Develop/Debug/Monitor
  ↓
Press Ctrl+C to stop
  ↓
END
```

---

**Save this card for quick reference!** 🎴

Print it out or bookmark in browser 📌
