# Natpudan AI - Startup Guide

## Quick Start Commands

### 🚀 Development Mode (Recommended for Development)
```powershell
.\start-all.ps1
```
**Features:**
- ✅ SQLite database (no container needed)
- ✅ Services in separate terminal windows
- ✅ Fast startup (~20 seconds)
- ✅ Easy debugging
- ✅ Auto-reload on code changes

**Services Started:**
- Backend (FastAPI) → http://127.0.0.1:8001
- Frontend (React) → http://localhost:5173
- Celery Worker (background tasks)
- Flower Dashboard → http://localhost:5555

---

### 🐋 Production Mode (Podman Containers)
```powershell
.\start-all.ps1 -UsePodman
```
**Features:**
- ✅ PostgreSQL database in container
- ✅ All services containerized
- ✅ Production-like environment
- ✅ Nginx reverse proxy
- ✅ Persistent data volumes

**Services Started:**
- Backend (FastAPI) → http://127.0.0.1:8000
- Frontend (React) → http://127.0.0.1:3000
- PostgreSQL → localhost:5432
- Redis → localhost:6379
- Celery Worker
- Flower Dashboard → http://localhost:5555
- Nginx Proxy → http://localhost:80

---

## Individual Service Scripts

### Backend Only
```powershell
.\start-backend.ps1           # Port 8000 (or 8001 if 8000 busy)
```

### Frontend Only
```powershell
cd frontend
npm run dev                   # Port 5173
```

### Podman Compose (Manual)
```powershell
# Start all containers
python -m podman_compose up -d

# View logs
python -m podman_compose logs -f

# Stop all containers
python -m podman_compose down

# Restart specific service
python -m podman_compose restart backend
```

---

## Service Endpoints

### Development Mode
| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | - |
| Backend API | http://127.0.0.1:8001 | - |
| API Docs | http://127.0.0.1:8001/docs | - |
| Flower | http://localhost:5555 | admin/admin |

### Podman Mode
| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://127.0.0.1:8000 | - |
| API Docs | http://127.0.0.1:8000/docs | - |
| Flower | http://localhost:5555 | admin/changeme |
| Nginx | http://localhost:80 | - |
| PostgreSQL | localhost:5432 | physician_user/secure_password |
| Redis | localhost:6379 | redis_password |

---

## Stopping Services

### Development Mode
1. **Close individual terminal windows**, OR
2. Run: `taskkill /F /IM powershell.exe` (kills all PowerShell)

### Podman Mode
```powershell
python -m podman_compose down
```

---

## Troubleshooting

### Port Already in Use
```powershell
# Check what's using port 8000
netstat -ano | findstr ":8000"

# Kill process by PID
taskkill /F /PID <PID>
```

### Backend Won't Start
1. Check `.env` file exists in `backend/` directory
2. Verify OpenAI API key is set
3. Check logs in backend terminal window

### Podman Compose Not Found
```powershell
pip install podman-compose
```

### Database Issues (Development)
```powershell
# Reset SQLite database
.\start-all.ps1 -RecreateDb
```

### View Container Logs (Podman)
```powershell
# All services
python -m podman_compose logs -f

# Specific service
python -m podman_compose logs -f backend
python -m podman_compose logs -f frontend
python -m podman_compose logs -f db
```

---

## Default Test Credentials

**Admin User:**
- Email: `admin@natpudan.local`
- Password: `admin123`

**Doctor User:**
- Email: `doctor@natpudan.local`
- Password: `doctor123`

**Staff User:**
- Email: `staff@natpudan.local`
- Password: `staff123`

---

## Environment Variables

Create `.env` file in `backend/` directory:

```env
# Required
OPENAI_API_KEY=sk-your-api-key-here
SECRET_KEY=your-secret-key-here

# Optional - Database (Podman mode)
DATABASE_URL=postgresql://physician_user:secure_password@db:5432/physician_ai

# Optional - Redis (Podman mode)
REDIS_URL=redis://:redis_password@redis:6379/0

# Optional - Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

---

## System Requirements

### Development Mode
- Python 3.12+
- Node.js 18+
- 4GB RAM minimum
- Windows 10/11 or Linux

### Podman Mode
- All above, plus:
- Podman Desktop installed
- podman-compose: `pip install podman-compose`
- 8GB RAM recommended
- 20GB free disk space

---

## Quick Tips

✅ **Fast dev iteration**: Use development mode (local SQLite)
✅ **Test production setup**: Use Podman mode
✅ **View API docs**: Visit `/docs` endpoint
✅ **Debug issues**: Check individual terminal windows for errors
✅ **Reset everything**: `.\start-all.ps1 -RecreateDb`

---

## Need Help?

- 📖 Documentation: See `README.md` and other `.md` files in root
- 🐛 Issues: Check terminal windows for error messages
- 💡 Features: Review `ALL_FEATURES_A_TO_F.md`
- 🏥 Medical AI: See `MEDICAL_CHAT_SESSION_COMPLETE.md`
