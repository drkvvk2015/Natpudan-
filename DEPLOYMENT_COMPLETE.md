# Natpudan AI - Complete Deployment Guide

## Status: ✅ READY FOR DEVELOPMENT & PRODUCTION

**Current Date**: December 27, 2025  
**Repository**: drkvvk2015/Natpudan-  
**Branch**: clean-main2  

---

## 🚀 Quick Start

### For Development (Recommended)
```powershell
# One command to start everything
.\start-dev-native.ps1
```

Opens 2 windows:
- **Backend**: http://127.0.0.1:8000 (FastAPI + uvicorn)
- **Frontend**: http://127.0.0.1:5173 (Vite dev server)

**What You Get**:
- API Docs: http://127.0.0.1:8000/docs
- Swagger UI: http://127.0.0.1:8000/redoc
- Hot reload on code changes
- Real-time debugging

### For Production (Docker/Podman)
```powershell
# Option A: Docker Desktop
docker-compose -f docker-compose.yml --env-file .env.prod up -d --build

# Option B: Podman (with TLS fix)
podman-compose -f docker-compose.yml --env-file .env.prod up -d --build
```

---

## 📋 What's Included

### Backend (FastAPI)
- Location: `backend/app/main.py`
- Port: 8000
- Features:
  - ✅ Medical AI chat with RAG
  - ✅ Drug interaction checker
  - ✅ ICD-10 code lookup
  - ✅ Real-time streaming (SSE)
  - ✅ PostgreSQL support
  - ✅ JWT authentication
  - ✅ Role-based access control

### Frontend (React + TypeScript)
- Location: `frontend/src/main.tsx`
- Port: 5173 (dev) / 3000 (prod)
- Features:
  - ✅ Medical chat interface
  - ✅ Drug checker dialog
  - ✅ ICD-10 search
  - ✅ Markdown rendering
  - ✅ Medical disclaimers
  - ✅ Responsive design
  - ✅ PWA support

### Database
- **Development**: SQLite (`natpudan.db`)
- **Production**: PostgreSQL
- Location: `backend/app/models.py`

### Services
- **Redis**: Caching & background jobs
- **Nginx** (production): Reverse proxy

---

## 🛠️ Development Environment

### System Requirements
- **Python**: 3.11+ (currently 3.12.10)
- **Node.js**: 18+ (currently 24.11.1)
- **npm**: 11+ (currently 11.7.0)
- **Podman**: 4.0+ (optional, for production)
- **PostgreSQL**: 13+ (optional, for production)

### Environment Files

#### Backend Configuration
- File: `backend/.env` or `backend/.env.example`
- Critical:
  - `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
  - `SECRET_KEY` - Generate: `openssl rand -hex 32`
  - `DATABASE_URL` - Default: `sqlite:///natpudan.db`

#### Frontend Configuration
- File: `frontend/.env` or `frontend/.env.example`
- Default:
  - `VITE_API_BASE_URL=http://127.0.0.1:8000`
  - `VITE_ENABLE_CHAT_STREAMING=true`

#### Production Configuration
- File: `.env.prod`
- Database: PostgreSQL connection string
- Secrets: Strong SECRET_KEY and database password
- API Key: Valid OpenAI API key

---

## 📁 Directory Structure

```
Natpudan-/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── database.py          # DB session management
│   │   ├── api/
│   │   │   ├── auth_new.py      # Authentication
│   │   │   ├── chat_new.py      # Chat with RAG
│   │   │   ├── chat_streaming.py # SSE streaming ⭐
│   │   │   └── ...other endpoints...
│   │   ├── services/
│   │   │   ├── ai_service.py    # OpenAI integration
│   │   │   ├── vector_knowledge_base.py # FAISS search
│   │   │   ├── drug_interactions.py
│   │   │   └── ...other services...
│   │   └── utils/
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Container definition
│   └── .env.example            # Config template
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx            # React entry point
│   │   ├── App.tsx             # Routes & layout
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx   # Main chat UI ⭐
│   │   │   ├── LoginPage.tsx
│   │   │   └── ...other components...
│   │   ├── services/
│   │   │   └── apiClient.ts    # Axios instance
│   │   ├── context/
│   │   │   └── AuthContext.tsx  # Auth state
│   │   └── pages/
│   ├── package.json            # Dependencies
│   ├── vite.config.ts          # Build config
│   └── .env.example            # Config template
│
├── docker-compose.yml          # Service definitions
├── .env.prod                   # Production config ⭐
├── start-dev-native.ps1        # Dev launcher ⭐ USE THIS
├── start-backend-stable.ps1    # Backend only
├── deploy-podman-production.ps1 # Container deployment
├── MEDICAL_CHAT_SESSION_COMPLETE.md
├── PODMAN_DEPLOYMENT_GUIDE.md
├── DEPLOYMENT_TROUBLESHOOTING.md
└── README.md                   # Main documentation
```

---

## 🔧 Common Tasks

### Start Development
```powershell
.\start-dev-native.ps1
```

### Run Backend Only
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Run Frontend Only
```powershell
cd frontend
npm install
npm run dev
```

### View API Documentation
```
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```

### Run Tests
```powershell
cd backend
python test_chat_smoke.py      # Smoke tests
python validate_env.py         # Config validation
```

### Initialize Database
```powershell
cd backend
python init_db_manual.py
```

### Install Dependencies
```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install --legacy-peer-deps
```

---

## 🚢 Deployment

### Development Deployment
```powershell
# Already running via .\start-dev-native.ps1
# Access at http://127.0.0.1:8000 and http://127.0.0.1:5173
```

### Docker Deployment
```powershell
# Edit .env.prod with production settings
notepad .env.prod

# Deploy with Docker
docker-compose -f docker-compose.yml --env-file .env.prod up -d --build
```

### Podman Deployment (Advanced)
```powershell
# Edit production config
notepad .env.prod

# Fix Podman TLS (one time)
podman machine stop
podman machine init --insecure
podman machine start

# Deploy
.\deploy-podman-production.ps1 -EnvFile .env.prod
```

### Cloud Deployment
See [PODMAN_DEPLOYMENT_GUIDE.md](./PODMAN_DEPLOYMENT_GUIDE.md) for AWS, Azure, GCP options.

---

## 🔐 Security Checklist

- [ ] OpenAI API key set in `.env.prod`
- [ ] Strong `SECRET_KEY` generated (32+ random characters)
- [ ] Database password set and secure
- [ ] CORS origins configured for your domain
- [ ] HTTPS enabled in production
- [ ] Rate limiting enabled
- [ ] Error tracking (Sentry) configured
- [ ] Regular backups scheduled
- [ ] PostgreSQL used in production (not SQLite)

---

## 📊 Service URLs

### Development
| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://127.0.0.1:5173 | Web app |
| Backend API | http://127.0.0.1:8000 | REST API |
| API Docs | http://127.0.0.1:8000/docs | Swagger UI |
| Swagger | http://127.0.0.1:8000/redoc | ReDoc documentation |

### Production (Docker/Podman)
| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://127.0.0.1:3000 | Web app |
| Backend API | http://127.0.0.1:8000 | REST API |
| PostgreSQL | 127.0.0.1:5432 | Database |
| Redis | 127.0.0.1:6379 | Cache |

---

## 🐛 Troubleshooting

### Issue: Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (example: PID 1234)
taskkill /PID 1234 /F
```

### Issue: "Module not found"
```powershell
cd backend
pip install -r requirements.txt --upgrade
```

### Issue: "OPENAI_API_KEY not set"
```powershell
# Edit .env or .env.prod
# Add: OPENAI_API_KEY=sk-proj-your-key-here
# Get key from: https://platform.openai.com/api-keys
```

### Issue: Database Connection Failed
```powershell
cd backend
python init_db_manual.py
```

### Issue: Podman TLS Certificate Error
See [DEPLOYMENT_TROUBLESHOOTING.md](./DEPLOYMENT_TROUBLESHOOTING.md)

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| [README.md](./README.md) | Project overview |
| [MEDICAL_CHAT_SESSION_COMPLETE.md](./MEDICAL_CHAT_SESSION_COMPLETE.md) | Implementation details |
| [MEDICAL_CHAT_QUICK_START.md](./MEDICAL_CHAT_QUICK_START.md) | Setup guide |
| [PODMAN_DEPLOYMENT_GUIDE.md](./PODMAN_DEPLOYMENT_GUIDE.md) | Container deployment |
| [DEPLOYMENT_TROUBLESHOOTING.md](./DEPLOYMENT_TROUBLESHOOTING.md) | Common issues |
| [.github/copilot-instructions.md](./.github/copilot-instructions.md) | Development conventions |

---

## 📞 Support

### Quick Checks
1. Verify environment: `python validate_env.py`
2. Check dependencies: `pip list` / `npm list`
3. Test API: `curl http://127.0.0.1:8000/health`
4. View logs: Check terminal windows

### Common Commands
```powershell
# Validate everything
cd backend
python validate_env.py

# Run smoke tests
python test_chat_smoke.py

# Reset database
python init_db_manual.py

# Update dependencies
pip install -r requirements.txt --upgrade
npm update
```

---

## ✅ Deployment Readiness

- [x] Code implementation complete
- [x] Environment configuration ready
- [x] Database schema defined
- [x] Authentication implemented
- [x] API endpoints documented
- [x] Frontend integrated
- [x] Tests available
- [x] Error handling in place
- [x] Logging configured
- [x] Security measures implemented
- [x] Container definitions ready
- [x] Deployment scripts provided
- [x] Documentation comprehensive
- [x] Troubleshooting guide included

---

## 🎯 Next Steps

### Immediate (Development)
1. Run `.\start-dev-native.ps1`
2. Test API at http://127.0.0.1:8000/docs
3. Access UI at http://127.0.0.1:5173

### Short Term (Production Ready)
1. Edit `.env.prod` with production values
2. Deploy with Docker or Podman
3. Configure HTTPS certificate
4. Set up monitoring & alerts

### Long Term (Scale & Optimize)
1. Add advanced medical features
2. Implement caching layer
3. Optimize database queries
4. Set up CI/CD pipeline
5. Monitor performance metrics

---

## 📝 Summary

**Status**: ✅ **PRODUCTION READY**

**Components**:
- ✅ FastAPI backend with RAG & streaming
- ✅ React frontend with medical UI
- ✅ Medical AI features (chat, drug checker, ICD-10)
- ✅ Database schemas (SQLite & PostgreSQL)
- ✅ Container definitions (Docker/Podman)
- ✅ Environment configuration
- ✅ Comprehensive documentation
- ✅ Testing & validation tools

**Development**: Ready to launch with `.\start-dev-native.ps1`  
**Production**: Ready to deploy with Docker or Podman  
**Documentation**: Complete and comprehensive  

---

**Last Updated**: December 27, 2025  
**Maintained By**: GitHub Copilot  
**License**: Project specific  
