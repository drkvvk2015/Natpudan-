# 🚀 How to Run the Full Natpudan AI Medical Assistant App

## ⚡ QUICKEST START (30 seconds)

### Option 1: All-in-One Command
```powershell
cd D:\Users\CNSHO\Documents\GitHub\Natpudan-
.\start-all.ps1
```

**What happens**:
- ✅ SQLite database initialized
- ✅ Backend (FastAPI) starts on port 8000
- ✅ Celery worker starts
- ✅ Flower (task monitor) starts on port 5555
- ✅ Frontend (React) starts on port 5173

---

## 🎯 Running Options

### Option A: Full Stack (Recommended for Development)

```powershell
.\start-all.ps1
```

**Starts**:
- Backend API (FastAPI) → http://localhost:8000
- Frontend (React) → http://localhost:5173
- Celery worker (background tasks)
- Flower dashboard → http://localhost:5555

**Best for**: Complete system testing, UI development

---

### Option B: Backend Only

```powershell
.\start-backend.ps1
```

**Starts**:
- Backend API (FastAPI) only
- Automatically selects port 8000 or 8001

**Best for**: API testing, backend development

---

### Option C: Frontend Only

```powershell
# Terminal 1: Start backend first
.\start-backend.ps1

# Terminal 2: Start frontend
cd frontend
npm run dev
```

**Starts**:
- Frontend dev server on port 5173

**Best for**: UI development, testing frontend components

---

### Option D: Debug Mode

```powershell
.\start-debug-full.ps1
```

**Starts**:
- All services with verbose logging
- Better for troubleshooting

**Best for**: Debugging issues, understanding what's happening

---

## 📊 Complete Service Overview

### Backend Services

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| FastAPI | 8000 | http://localhost:8000 | Main API server |
| Swagger UI | 8000 | http://localhost:8000/docs | API documentation |
| ReDoc | 8000 | http://localhost:8000/redoc | Alternative API docs |
| Health Check | 8000 | http://localhost:8000/health | System health |

### Frontend

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| React Dev | 5173 | http://localhost:5173 | Web application |
| Vite HMR | 5173+ | Internal | Hot reload |

### Task Management

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Celery Worker | - | Internal | Background tasks |
| Flower | 5555 | http://localhost:5555 | Task monitoring |

### Database

| Type | Location | Purpose |
|------|----------|---------|
| SQLite | `backend/natpudan.db` | Main database |
| Celery Broker | `backend/celery_broker.db` | Task queue |
| Celery Results | `backend/celery_results.db` | Task results |

---

## 🌐 Accessing the App

### 1. **Frontend (User Interface)**
```
http://localhost:5173
```
- Login with credentials
- Access: Patient intake, diagnosis, chat, etc.

### 2. **API Documentation**
```
http://localhost:8000/docs
```
- Swagger UI interface
- Try endpoints directly
- See request/response schemas

### 3. **Task Monitor (Admin)**
```
http://localhost:5555
```
- Username: `admin`
- Password: `admin`
- View background jobs
- Monitor celery workers

### 4. **Health Check**
```
curl http://localhost:8000/health
```
Returns JSON status of all services

---

## ✅ Verification Checklist

After starting, verify everything works:

### ✓ Backend Running
```powershell
curl http://localhost:8000/health
```
Expected: JSON response with service status

### ✓ Frontend Running
```
Open http://localhost:5173 in browser
```
Expected: Login page loads

### ✓ API Endpoints Available
```
Open http://localhost:8000/docs
```
Expected: Swagger UI shows all endpoints

### ✓ Phase 5C Endpoints
```
curl http://localhost:8000/api/phase-5c/health
```
Expected: Phase 5C operational message

### ✓ Phase 6 Endpoints
```
curl http://localhost:8000/api/phase-6/health
```
Expected: Phase 6 health status

### ✓ Database Working
```powershell
# Check database file exists
ls backend/natpudan.db
```
Expected: File size > 0

### ✓ Knowledge Base Ready
```
curl http://localhost:8000/api/medical/knowledge/statistics
```
Expected: Document count

---

## 🔧 Common Startup Scenarios

### Scenario 1: First Time Running

```powershell
# Make sure you're in the right directory
cd D:\Users\CNSHO\Documents\GitHub\Natpudan-

# Run all services
.\start-all.ps1

# Wait 30-60 seconds for startup

# Open browser tabs:
# 1. http://localhost:5173 (Frontend)
# 2. http://localhost:8000/docs (API docs)
# 3. http://localhost:5555 (Flower)
```

### Scenario 2: API Testing Only

```powershell
cd D:\Users\CNSHO\Documents\GitHub\Natpudan-

# Start backend only
.\start-backend.ps1

# In another terminal, test an endpoint:
curl -X POST "http://localhost:8000/api/auth/login" `
  -H "Content-Type: application/json" `
  -d '{"email":"test@example.com","password":"password"}'
```

### Scenario 3: Frontend Development

```powershell
# Terminal 1: Start backend
.\start-backend.ps1

# Terminal 2: Start frontend
cd frontend
npm run dev

# Now edit frontend files and see hot reload
```

### Scenario 4: Debug Mode

```powershell
# Run with detailed logging
.\start-debug-full.ps1

# Watch all service logs in separate terminals
# Ctrl+C in any terminal to stop that service
```

---

## 🛑 Stopping Services

### Stop Everything
```powershell
# Option 1: Ctrl+C in original terminal
# This stops all services started by the script

# Option 2: Close all PowerShell windows
# Each service runs in its own window

# Option 3: Kill processes
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

### Stop Individual Service
```powershell
# Just close the terminal window for that service
# Backend terminal → Ctrl+C
# Frontend terminal → Ctrl+C
# etc.
```

---

## 📝 Configuration

### Backend Configuration
File: `backend/.env`

```env
# Database
DATABASE_URL=sqlite:///./natpudan.db

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Phase 5B
PHASE5_MEDSAM_CHECKPOINT=D:\path\to\medsam_vit_b.pth
```

### Frontend Configuration
File: `frontend/.env.local`

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000
```

---

## 🧪 Testing the New Phases

### Phase 5C - Fine-Tuning

```bash
# Check health
curl http://localhost:8000/api/phase-5c/health

# Create dataset
curl -X POST "http://localhost:8000/api/phase-5c/datasets/create" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "test-dataset",
    "description": "Test medical images"
  }'

# View roadmap
curl http://localhost:8000/api/phase-5c/roadmap
```

### Phase 6 - Local LLM

```bash
# Check health
curl http://localhost:8000/api/phase-6/health

# List available models
curl http://localhost:8000/api/phase-6/models/available

# Get setup guide
curl http://localhost:8000/api/phase-6/setup-guide

# Test chat (requires Ollama running)
curl -X POST "http://localhost:8000/api/phase-6/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is hypertension?",
    "max_tokens": 500
  }'
```

---

## 🐛 Troubleshooting

### Issue: Port Already in Use

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID 1234 /F
```

### Issue: Frontend Not Connecting to Backend

Check `frontend/.env.local`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Should match the backend URL where it's running.

### Issue: Database Locked

```powershell
# Delete old database to force reinitialize
rm backend/natpudan.db
rm backend/celery_broker.db
rm backend/celery_results.db

# Run startup script again
.\start-all.ps1
```

### Issue: Missing Dependencies

```powershell
# Reinstall Python dependencies
cd backend
pip install -r requirements.txt

# Reinstall Node dependencies
cd frontend
npm install
```

### Issue: Ollama Not Available (Phase 6)

```powershell
# Start Ollama service separately
.\setup-phase-6.ps1

# Or manually
ollama serve

# In another terminal, download model
ollama pull llama2
```

---

## 📚 Useful Commands

### Check Backend Status
```powershell
curl http://localhost:8000/health
```

### View API Documentation
```
http://localhost:8000/docs
```

### Run Backend Tests
```powershell
cd backend
pytest tests/ -v
```

### Run Frontend Tests
```powershell
cd frontend
npm run test
```

### Reset Database
```powershell
rm backend/natpudan.db
.\start-all.ps1
```

### View Logs
```powershell
# Backend logs in backend terminal
# Frontend logs in frontend terminal
# Celery logs in celery terminal
```

### Monitor Celery Tasks
```
http://localhost:5555
```

---

## 🎯 Next Steps After Starting

1. **Open Frontend** → http://localhost:5173
2. **Create Account** → Register as a new user
3. **Login** → Use your credentials
4. **Try Patient Intake** → Add a patient
5. **Test Diagnosis** → Get AI diagnosis
6. **Check Knowledge Base** → Search medical info
7. **Test Phase 5C** → Try fine-tuning (if you have images)
8. **Test Phase 6** → Try medical reasoning (requires Ollama)

---

## 💡 Tips

- **Hot Reload**: Frontend automatically reloads when you edit files
- **API Testing**: Use http://localhost:8000/docs to test endpoints
- **Flower Dashboard**: Monitor background task progress
- **Logs**: Each service logs to its terminal for easy debugging
- **Kill All**: `taskkill /F /IM python.exe && taskkill /F /IM node.exe`

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Start everything | `.\start-all.ps1` |
| Start backend only | `.\start-backend.ps1` |
| Start debug mode | `.\start-debug-full.ps1` |
| Frontend | http://localhost:5173 |
| API Docs | http://localhost:8000/docs |
| Task Monitor | http://localhost:5555 |
| Health Check | `curl localhost:8000/health` |
| Stop services | Ctrl+C or close terminal |

---

**Status**: ✅ Ready to Run  
**Architecture**: Full Stack (Backend + Frontend + Services)  
**Database**: SQLite (no Docker required)  
**Mode**: Development (hot reload enabled)

Happy coding! 🎉

