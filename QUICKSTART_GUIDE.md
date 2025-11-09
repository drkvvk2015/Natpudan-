# 🚀 Quick Start Guide - Physician AI Assistant

## For Developers (Local Development)

### 1. Clone and Setup
```powershell
git clone https://github.com/drkvvk2015/Natpudan-.git
cd Natpudan-
```

### 2. Backend Setup
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Copy and edit environment file
cp .env.production .env
notepad .env  # Set OPENAI_API_KEY and SECRET_KEY
```

### 3. Run Backend
```powershell
python run.py
# Backend running at: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 4. Frontend Setup (New Terminal)
```powershell
cd frontend
npm install
npm run dev
# Frontend running at: http://localhost:3000
```

---

## For Production (Using Docker)

### 1. Quick Deploy
```powershell
# Clone repo
git clone https://github.com/drkvvk2015/Natpudan-.git
cd Natpudan-

# Configure environment
cp backend/.env.production backend/.env
notepad backend\.env  # Update with your settings

# Deploy with one command!
.\deploy-production.ps1 -Environment production
```

### 2. Manual Docker Deploy
```powershell
# Build and start
docker-compose build
docker-compose up -d

# Check health
curl http://localhost:8000/health

# View logs
docker-compose logs -f
```

---

## Essential Commands

### Backend
```powershell
# Start backend
cd backend
python run.py

# Run tests
pytest tests/

# Check health
curl http://localhost:8000/health
```

### Frontend
```powershell
# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Docker
```powershell
# Start all services
docker-compose up -d

# Stop all services
docker-compose stop

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart specific service
docker-compose restart backend

# Remove everything (including data!)
docker-compose down -v
```

---

## Critical Configuration

### Backend (.env)
```bash
# Required
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=generate-secure-random-key

# Database (PostgreSQL for production)
DATABASE_URL=postgresql://user:pass@localhost:5432/physician_ai

# Environment
ENVIRONMENT=production
DEBUG=False

# CORS (your domain)
CORS_ORIGINS=https://yourapp.com
```

### Generate Secret Key
```powershell
# Method 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Method 2: OpenSSL
openssl rand -base64 32
```

---

## Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Detailed metrics
curl http://localhost:8000/health/detailed

# Dependencies status
curl http://localhost:8000/health/dependencies
```

---

## Common Issues

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /PID <process-id> /F
```

### Database Connection Failed
```powershell
# Check if PostgreSQL is running
docker-compose ps db

# Restart database
docker-compose restart db
```

### Module Not Found
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or for frontend
npm install --force
```

---

## File Structure

```
Natpudan-/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── middleware/   # Security, rate limiting
│   ├── data/             # Medical documents
│   ├── .env              # Environment variables
│   └── run.py            # Application entry
├── frontend/
│   ├── src/              # React components
│   └── package.json      # Dependencies
├── docker-compose.yml    # Docker orchestration
└── deploy-production.ps1 # Deployment script
```

---

## API Endpoints

### Medical
- `POST /api/medical/diagnosis` - Generate diagnosis
- `POST /api/medical/knowledge/search` - Search medical knowledge
- `GET /api/medical/knowledge/statistics` - Knowledge base stats

### Prescription
- `POST /api/prescription/generate-plan` - Generate prescription
- `POST /api/prescription/check-interactions` - Check drug interactions
- `POST /api/prescription/dosing` - Calculate dosing

### Monitoring
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system metrics
- `GET /metrics` - Application metrics

---

## Documentation Links

- **Full Deployment**: `DEPLOYMENT_GUIDE.md`
- **Production Checklist**: `PRODUCTION_CHECKLIST.md`
- **Project Overview**: `PROJECT_README.md`
- **Production Summary**: `PRODUCTION_READY_SUMMARY.md`
- **API Documentation**: http://localhost:8000/docs

---

## Quick Tips

💡 **Development**: Use SQLite database for faster local development
💡 **Production**: Always use PostgreSQL for production deployments
💡 **Security**: Never commit `.env` files with real credentials
💡 **Testing**: Run tests before deploying: `pytest tests/`
💡 **Logs**: Check logs if something doesn't work: `docker-compose logs`
💡 **Backup**: Always backup database before major changes
💡 **SSL**: Use Let's Encrypt for free SSL certificates in production

---

## Support

🐛 **Issues**: [GitHub Issues](https://github.com/drkvvk2015/Natpudan-/issues)
📖 **Documentation**: See the guides in the root directory
🔍 **API Docs**: http://localhost:8000/docs (when server is running)

---

**Version**: 1.0.0 | **Updated**: November 2025
