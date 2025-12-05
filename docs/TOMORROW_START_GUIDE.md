# [EMOJI] Natpudan AI - Quick Start Guide

## Single Command Startup (Recommended)

To start the entire application with one command:

```powershell
.\start-app-complete.ps1
```

This script will:
- [OK] Install all dependencies automatically
- [OK] Handle port conflicts and cleanup
- [OK] Start backend and frontend with health checks
- [OK] Provide retry mechanism on failures
- [OK] Clean shutdown with Ctrl+C

## Manual Startup (Alternative)

If you prefer manual control:

1. **Start Backend:**
   ```powershell
   .\start-backend.ps1
   ```

2. **Start Frontend:**
   ```powershell
   .\start-frontend.ps1
   ```

## Application URLs

- **Frontend:** http://127.0.0.1:5173/
- **Backend API:** http://127.0.0.1:8000/
- **API Documentation:** http://127.0.0.1:8000/docs

## Current Known Issues & Status

### [OK] Completed Fixes
1. **Vite server loop** - Fixed with port conflict detection
2. **Auto-populate present history** - Implemented with complaint duration
3. **Live differential diagnosis** - Created comprehensive API endpoint
4. **Lab investigations & reports** - Full system with file upload
5. **Missing JWT dependency** - Added PyJWT to requirements
6. **Undefined array errors** - Added comprehensive safety checks

### [WRENCH] Remaining Issues to Fix Tomorrow

1. **Frontend Stability**
   - Some undefined state access errors
   - Need to add more error boundaries
   - Component rerender optimization

2. **Backend Communication**
   - API endpoint error handling
   - WebSocket connection stability
   - Database transaction safety

3. **Development Environment**
   - Hot reload improvements
   - Better error logging
   - Performance monitoring

## Troubleshooting

### App Won't Start
```powershell
# Kill all processes and restart
taskkill /f /im node.exe
taskkill /f /im python.exe
.\start-app-complete.ps1
```

### Port Conflicts
The startup script automatically handles port conflicts, but manually:
```powershell
# Check what's using the ports
Get-NetTCPConnection -LocalPort 8000,5173 -State Listen
# Kill specific processes
Stop-Process -Id <PID> -Force
```

### Missing Dependencies
```powershell
# Reinstall everything
Remove-Item node_modules -Recurse -Force
Remove-Item .venv -Recurse -Force
.\start-app-complete.ps1
```

### Database Issues
```powershell
# Reinitialize database
cd backend
python init_db_manual.py
```

## Development Environment Setup

### Required Software
- Python 3.10+
- Node.js 18+
- PowerShell 5.1+
- Git

### Environment Variables
Create `.env` file in `/backend/`:
```
DATABASE_URL=sqlite:///./natpudan.db
OPENAI_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

## Next Session Plan

1. **Run startup script and fix any remaining errors**
2. **Test all Clinical Case Sheet features:**
   - Complaint auto-population
   - Live diagnosis
   - Lab investigations
   - File uploads
3. **Performance optimization**
4. **Error handling improvements**
5. **Production deployment preparation**

## Quick Commands Reference

```powershell
# Start everything
.\start-app-complete.ps1

# Check health
Invoke-WebRequest http://127.0.0.1:8000/health

# View logs
Get-Job | Receive-Job

# Stop everything
Get-Job | Stop-Job; Get-Job | Remove-Job
```

---
**Status:** Ready for tomorrow's session with single-command startup solution [EMOJI]
