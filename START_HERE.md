# 🎬 EXECUTION INSTRUCTIONS - START HERE!

## ⚡ FASTEST START (2 STEPS)

### Step 1: Open PowerShell
```
Right-click on Windows desktop
→ Select "Open PowerShell window here"
OR
Win+X → Select "Windows PowerShell (Admin)"
```

### Step 2: Run This Command
```powershell
cd D:\Users\CNSHO\Documents\GitHub\Natpudan-
.\start-debug-full.ps1
```

**That's it!** ✨

Wait 30-60 seconds for all services to start...

---

## 🌐 OPEN IN BROWSER (While Services Start)

Once you see the services starting in the terminals, open these URLs:

### Tab 1: Frontend
```
http://localhost:5173
```

### Tab 2: API Documentation
```
http://localhost:8000/docs
```

### Tab 3: Flower Task Monitor
```
http://localhost:5555
```
Username: `admin`  
Password: `admin`

---

## 📋 WHAT YOU'LL SEE

### Terminal 1: FastAPI Backend
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [1234]
INFO:     Application startup complete
```

### Terminal 2: Celery Worker
```
[tasks] Celery worker starting...
[worker] Ready to accept tasks
celery@hostname ready.
```

### Terminal 3: Frontend (Vite)
```
VITE v4.5.0  ready in 245 ms

➜  Local:   http://127.0.0.1:5173/
➜  press h to show help
```

### Terminal 4: Original Terminal
```
[SUCCESS] All services started!
Frontend: http://localhost:5173
API Docs: http://localhost:8000/docs
Flower: http://localhost:5555
```

---

## ✅ VERIFY EVERYTHING IS WORKING

### Check 1: Frontend Loads
1. Go to http://localhost:5173
2. Should see login page or dashboard
3. ✅ Working!

### Check 2: API Documentation
1. Go to http://localhost:8000/docs
2. Should see Swagger UI with blue interface
3. Click any endpoint → Try it out → Execute
4. Should get response
5. ✅ Working!

### Check 3: Flower Dashboard
1. Go to http://localhost:5555
2. Login: admin / admin
3. Should see workers and task stats
4. ✅ Working!

### Check 4: Health Check
1. Go to http://localhost:8000/health
2. Should see JSON: `{"status": "healthy", ...}`
3. ✅ Working!

---

## 🎮 KEYBOARD SHORTCUTS

### In Any Terminal
- `Ctrl + C` - Stop the service
- `Ctrl + Z` - Suspend (Windows)
- `Clear` or `cls` - Clear screen

### In Browser
- `F12` - Open Developer Tools
- `Ctrl + Shift + K` - Open Console
- `Ctrl + Shift + E` - Open Network tab
- `Ctrl + Shift + I` - Open Inspector
- `F5` - Refresh page
- `Ctrl + R` - Hard refresh (clear cache)

### In Flower Dashboard
- `F5` - Refresh dashboard
- Click **Active** - See running tasks
- Click **Scheduled** - See upcoming tasks
- Click **Stats** - See performance metrics

---

## 🔍 TROUBLESHOOTING IF SOMETHING GOES WRONG

### Issue: "PowerShell cannot find start-debug-full.ps1"

**Fix:**
```powershell
# Make sure you're in the right directory
cd D:\Users\CNSHO\Documents\GitHub\Natpudan-

# Check the file exists
ls start-debug-full.ps1

# If not found, you may be in wrong directory
# List files to verify
ls
```

### Issue: "Access Denied" when running script

**Fix:**
```powershell
# Need to run as Administrator
# Right-click PowerShell → "Run as administrator"
# Then try again

.\start-debug-full.ps1
```

### Issue: "Docker is not installed"

**Fix:**
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install it
3. Restart your computer
4. Try again: `.\start-debug-full.ps1`

### Issue: Port Already in Use

**Fix:**
```powershell
# Find what's using the port
Get-NetTCPConnection -LocalPort 8000 | Select OwningProcess

# Stop that process
Stop-Process -Id <PID> -Force

# Try starting again
.\start-debug-full.ps1
```

### Issue: Backend crashes on startup

**Fix:**
```powershell
# Check what's wrong
docker logs physician-ai-backend

# If database issue
docker logs physician-ai-db

# Try restarting
docker-compose restart

# Or complete reset
docker-compose down -v
.\start-debug-full.ps1
```

---

## 📚 NEED MORE HELP?

### Quick Questions (5 minutes)?
Read: **QUICK_START_DEBUG.md**

### Need Details?
Read: **DEBUG_SETUP_GUIDE.md**

### Check Service Health?
Run: `.\diagnose.ps1`

### Real-time Dashboard?
Run: `.\monitor.ps1`

### View Complete Summary?
Read: **DEBUG_SETUP_COMPLETE.md**

---

## 🎯 WHAT TO DO AFTER STARTUP

### Option 1: Explore Frontend
1. Go to http://localhost:5173
2. Try creating account
3. Test features
4. Check browser console (F12) for errors

### Option 2: Test API
1. Go to http://localhost:8000/docs
2. Click any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. See the response

### Option 3: Monitor Tasks
1. Go to http://localhost:5555
2. Login: admin/admin
3. Click "Active" to see running tasks
4. Click "Stats" to see metrics
5. Try triggering a task from frontend

### Option 4: Check Logs
1. Watch the terminal windows
2. Make API requests
3. Watch request logs appear
4. Trigger background tasks
5. Watch task execution logs

---

## 🚀 COMMON NEXT STEPS

### If You Want to Edit Code
1. Edit files in `backend/app/` or `frontend/src/`
2. Backend/Frontend auto-reload
3. Check terminal for errors
4. Test changes in browser

### If You Want to Debug
1. Open DevTools (F12)
2. Go to Console tab
3. Go to Network tab
4. Make API requests
5. Watch requests/responses

### If You Want to Test API
1. Go to http://localhost:8000/docs
2. Find endpoint you want to test
3. Click "Try it out"
4. Fill in the form
5. Click "Execute"
6. See the response

### If You Want to Monitor Tasks
1. Go to http://localhost:5555
2. Login: admin/admin
3. Trigger a task from frontend
4. Watch it execute in Flower
5. Click on task for details

---

## ⏹️ HOW TO STOP

### Stop Individual Service
```powershell
# Press Ctrl+C in that terminal
# Or type: exit
```

### Stop All Services
```powershell
# Option 1: Press Ctrl+C in each terminal

# Option 2: Run this in any terminal
docker-compose down
```

### Complete Reset (Clear All Data)
```powershell
docker-compose down -v
```

---

## 🔄 IF YOU NEED TO RESTART

```powershell
# Option 1: Simple restart
docker-compose restart

# Option 2: Full restart with cleanup
docker-compose down
.\start-debug-full.ps1

# Option 3: Complete reset (clears data)
docker-compose down -v
.\start-debug-full.ps1
```

---

## 📊 SYSTEM REQUIREMENTS MET?

Before running, verify:

- ✅ Windows 10 or 11
- ✅ Docker Desktop installed
- ✅ Python 3.8+ installed
- ✅ At least 8GB RAM recommended
- ✅ 10GB disk space available
- ✅ Internet connection (for initial setup)

---

## 🎬 NOW YOU'RE READY!

### Run This Command:
```powershell
cd D:\Users\CNSHO\Documents\GitHub\Natpudan-
.\start-debug-full.ps1
```

### Then Open:
- Frontend: http://localhost:5173
- API: http://localhost:8000/docs
- Flower: http://localhost:5555

### And Start:
- Developing
- Testing
- Debugging
- Monitoring

**Happy coding!** 🚀

---

## 💡 PRO TIPS

### Tip 1: Keep Terminals Visible
Arrange terminals side-by-side to see logs from all services at once.

### Tip 2: Use Monitor Dashboard
Run `.\monitor.ps1` in a separate terminal for real-time status.

### Tip 3: Check Diagnostics
Run `.\diagnose.ps1` anytime to verify all services are healthy.

### Tip 4: Follow Logs
Use `docker logs -f physician-ai-backend` to follow logs as they happen.

### Tip 5: Use Flower
Monitor all background tasks and their execution times in Flower.

---

## ❓ FAQ

**Q: How long does it take to start?**
A: Usually 30-60 seconds for all services to be ready.

**Q: Can I edit code while it's running?**
A: Yes! Backend and frontend auto-reload on save.

**Q: Will I lose data if I stop?**
A: No, data persists in Docker volumes (unless you use `down -v`).

**Q: How do I debug backend code?**
A: Add print statements or use VS Code debugger. Check terminal for output.

**Q: How do I debug frontend code?**
A: Use browser DevTools (F12). Check Console and Network tabs.

**Q: What if something breaks?**
A: Run `.\diagnose.ps1` to check health, or `docker-compose down -v` to reset.

---

**READY?** 

Run: `.\start-debug-full.ps1`

Then open http://localhost:5173 🚀
