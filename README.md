# Natpudan AI Medical Assistant

A production-ready FastAPI + React full-stack application for medical professionals with AI-powered diagnostics, role-based access control (RBAC), and comprehensive patient management capabilities.

## Features

✅ **AI Chat Assistant** - OpenAI GPT-4 / Local TinyLLama / Ollama integration for medical consultations  
✅ **AI Diagnosis** - Intelligent clinical case analysis and recommendations  
✅ **Discharge Summary** - AI-powered generation with voice typing support  
✅ **Role-Based Access Control** - Staff, Doctor, and Admin roles with fine-grained permissions  
✅ **Secure Authentication** - JWT + OAuth2 (Google, GitHub, Microsoft)  
✅ **Database Persistence** - SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)  
✅ **Patient Management** - Intake forms, medical history, treatment plans, follow-ups  
✅ **Analytics Dashboard** - Demographics, disease trends, treatment outcomes  
✅ **Knowledge Base** - Vector embeddings (FAISS) for medical literature search  
✅ **Drug Interaction Checker** - Real-time medication interaction warnings  
✅ **FHIR Integration** - Healthcare data interoperability standards  
✅ **Medical Timeline** - Comprehensive patient event tracking and history  
✅ **Multi-Platform** - Web, PWA, Android/iOS (Capacitor), Desktop (Electron)

## Quick Start

### Prerequisites

- **Python** 3.11+ (tested with 3.11, 3.12, 3.13)
- **Node.js** 20+ (LTS recommended)
- **Git**
- **OpenAI API Key** (required for AI features) - get it at [platform.openai.com](https://platform.openai.com/api-keys)

### Fastest Way to Start (Windows PowerShell)

```powershell
# Clone and navigate
git clone https://github.com/drkvvk2015/Natpudan-.git
cd Natpudan-

# Run the unified startup script (handles venv, dependencies, both servers)
.\start-app.ps1
```

The app will open:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173  
- **API Docs**: http://localhost:8000/docs

### Manual Setup (All Platforms)

#### Step 1: Backend Setup

```powershell
# Create virtual environment
cd backend
python -m venv .venv  # or: py -3.11 -m venv .venv

# Activate (Windows)
.\.venv\Scripts\Activate.ps1
# Or Linux/Mac:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-db.txt

# Create .env from example
Copy-Item .env.example .env
# Edit .env to add: OPENAI_API_KEY, SECRET_KEY, DATABASE_URL

# Run migrations
python -m alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 2: Frontend Setup

```powershell
# In a new terminal, from project root
cd frontend

# Install dependencies
npm install

# Create .env from example
Copy-Item .env.example .env
# Edit .env to point to backend: VITE_API_BASE_URL=http://localhost:8000

# Start dev server
npm run dev
```

#### Step 3: Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Default Login (Development Only)

```
Username: admin@natpudan.local
Password: admin123
Role: Admin
```

### Backend Troubleshooting

If backend startup fails due to Python/venv issues:

```powershell
cd backend
.\repair-backend-env.ps1 -Install
# Optional: Add -RunTests for smoke tests
./repair-backend-env.ps1 -Install -RunTests
```

### Database Management

```powershell
cd backend

# View current migration version
python -m alembic current

# Create a new migration for schema changes
python -m alembic revision --autogenerate -m "Add new table"

# Apply migrations
python -m alembic upgrade head

# Or use the migration script:
.\migrate.ps1 -Command current
.\migrate.ps1 -Command upgrade
```

### Testing

```powershell
cd backend

# Run all tests (excluding manual/integration tests)
pytest

# Run specific test file
pytest tests/test_contracts.py -v

# Run with coverage
pytest --cov=app
```

### Frontend Build & Deployment

```powershell
cd frontend

# Production build (optimized)
npm run build:web

# Preview production build locally
npm run preview

# Type checking
npm run typecheck

# Lint code
npm run lint
```

## Role-Based Access Control (RBAC)

Natpudan uses three role levels with hierarchical permissions:

| Feature | Staff | Doctor | Admin |
|---------|-------|--------|-------|
| Patient Intake | ✅ | ✅ | ✅ |
| Chat with AI | ✅ | ✅ | ✅ |
| AI Diagnosis | ❌ | ✅ | ✅ |
| Knowledge Base Search | ❌ | ✅ | ✅ |
| Drug Interactions | ❌ | ✅ | ✅ |
| Treatment Plans | ❌ | ✅ | ✅ |
| Analytics Dashboard | ❌ | ✅ | ✅ |
| FHIR Explorer | ❌ | ✅ | ✅ |
| User Management | ❌ | ❌ | ✅ |
| System Settings | ❌ | ❌ | ✅ |

## Configuration

### AI Provider Options

The app supports multiple AI providers with automatic fallback:

| Provider | Best For | Setup | Cost | Privacy |
|----------|----------|-------|------|---------|
| **TinyLLama** (Embedded) | Development, demos, privacy-first | ~5 min | 🆓 Free | ✅ 100% local |
| **Ollama** (Local) | Production, better accuracy | ~15 min | 🆓 Free | ✅ 100% local |
| **OpenAI** | Critical medical decisions, best accuracy | API key | 💰 Per-token | ⚠️ API-based |

**Quick Start:** Use `AI_PROVIDER=auto` to automatically try embedded → ollama → openai

**TinyLLama Setup:** See [TINYLLAMA_SETUP.md](TINYLLAMA_SETUP.md) for complete instructions

### Backend Environment Variables

Create `backend/.env` file with the following:

#### Required Variables

```env
# Database Configuration
# For development: SQLite (automatic)
DATABASE_URL=sqlite:///./natpudan.db

# For production: PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/natpudan_db

# JWT Authentication
SECRET_KEY=generate-with:-python -c "import secrets; print(secrets.token_urlsafe(32))"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OpenAI (Required for all AI features)
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o

# AI Provider Configuration (Optional - for local/embedded models)
# Options: "auto" (embedded→ollama→openai), "embedded" (TinyLLama), "ollama", "openai"
AI_PROVIDER=auto

# For TinyLLama Embedded Model (lightweight, local, no API key needed)
# Download guide: See TINYLLAMA_SETUP.md
EMBEDDED_MODEL_PATH=models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf  # Optional
MODEL_GPU_LAYERS=0  # 0 for CPU only, 10-33 for GPU acceleration

# For Ollama Server (if running locally)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Application URLs
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
ENVIRONMENT=development
```

#### Optional: OAuth Providers

```env
# Google
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret

# GitHub
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-secret

# Microsoft
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-secret
```

#### Optional: Monitoring

```env
# Sentry (error tracking)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### Frontend Environment Variables

Create `frontend/.env` file:

```env
# Backend API location
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Optional: Sentry monitoring
VITE_SENTRY_DSN=
```

### Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Get OpenAI API Key

1. Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key with appropriate permissions
3. Add to `backend/.env` as `OPENAI_API_KEY`
4. Monitor usage at [platform.openai.com/usage](https://platform.openai.com/usage)

##  Security Features

- **Password Security**: Bcrypt hashing for secure password storage
- **JWT Authentication**: Secure token-based authentication
- **OAuth2 Integration**: Social login with Google, GitHub, Microsoft
- **Database Security**: SQL injection protection via SQLAlchemy ORM
- **Environment Variables**: Sensitive credentials stored in `.env` (never committed)
- **CORS Configuration**: Controlled cross-origin access
- **Dependencies**: Regularly updated via Dependabot alerts

### Security Best Practices

- Never commit `.env` files to version control
- Rotate API keys regularly
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Review GitHub Security tab for vulnerabilities

##  Architecture

### Backend (FastAPI)

- **Database**: SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)
- **Models**: User, Conversation, Message, DischargeSummary
- **Authentication**: JWT + OAuth2 with bcrypt password hashing
- **AI Integration**: OpenAI GPT-4 for medical assistance
- **API Structure**:
  - `/api/auth/*` - Authentication endpoints
  - `/api/chat/*` - AI chat with conversation history
  - `/api/discharge-summary/*` - Discharge summary CRUD + AI generation
  - `/api/medical/*` - Medical features (diagnosis, knowledge base)
  - `/api/treatment/*` - Treatment plan management
  - `/api/analytics/*` - Analytics dashboard
  - `/api/fhir/*` - FHIR integration

### Frontend (React + TypeScript)

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 7
- **UI Library**: Material-UI (MUI) v5
- **Routing**: React Router v6
- **State Management**: React Context API
- **API Client**: Axios
- **Features**:
  - Responsive design
  - Voice typing (Web Speech API)
  - Real-time AI chat
  - OAuth social login
  - Professional medical forms

##  User Roles

### Staff Role

- Patient data entry
- Basic chat access
- View patient records

### Doctor Role

- Full chat access with AI
- Diagnosis assistance
- Discharge summary generation
- Treatment plan creation
- Knowledge base access
- Analytics viewing

### Admin Role

- All doctor permissions
- User management
- System configuration
- Full analytics access

##  API Testing

### Using curl

```powershell
# Register new user
curl -X POST http://127.0.0.1:8001/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"doctor@test.com\",\"password\":\"SecurePass123!\",\"full_name\":\"Dr. Test\",\"role\":\"doctor\",\"license_number\":\"MD12345\"}'

# Login
curl -X POST http://127.0.0.1:8001/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"doctor@test.com\",\"password\":\"SecurePass123!\"}'

# Chat (requires token)
curl -X POST http://127.0.0.1:8001/api/chat/message `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_TOKEN_HERE" `
  -d '{\"message\":\"What are the symptoms of pneumonia?\"}'
```

## [EMOJI] Database

### SQLite (Development)

Database file: `backend/natpudan.db`

View with DB Browser for SQLite: <https://sqlitebrowser.org/>

### PostgreSQL (Production)

Update `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/natpudan_db
```

### Database Migrations

```powershell
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

##  Logo Usage

Professional logo system with medical cross + AI circuit design:

- **Icon**: `frontend/public/logo-icon.svg` (80x80px)
- **Full Logo**: `frontend/public/logo-full.svg` (400x100px with text)
- **React Component**: `frontend/src/components/NatpudanLogo.tsx`

See `LOGO_USAGE.md` for detailed branding guidelines.

## [EMOJI] Troubleshooting

### Backend won't start

```powershell
# Check if all dependencies are installed
cd backend
pip install -r requirements.txt
pip install -r requirements-db.txt

# Check if .env file exists with required variables
cat .env

# Check if port 8001 is available
netstat -an | findstr :8001
```

### Frontend won't start

```powershell
# Reinstall dependencies
cd frontend
Remove-Item -Recurse -Force node_modules
npm install

# Clear cache
npm cache clean --force
```

### Database errors

```powershell
# Delete and recreate database
cd backend
Remove-Item natpudan.db
# Restart backend - database will auto-initialize
```

### OpenAI API errors

- Verify API key is correct in `.env`
- Check API quota at <https://platform.openai.com/usage>
- Ensure proper billing setup

##  Documentation

- API Docs: <http://127.0.0.1:8001/docs> (Swagger UI)
- ReDoc: <http://127.0.0.1:8001/redoc>
- Logo Guidelines: `LOGO_USAGE.md`

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## [EMOJI] License

See `LICENSE` file for details.

##  Acknowledgments

- OpenAI GPT-4 for AI capabilities
- FastAPI framework
- React and Material-UI teams
- Medical professionals for domain expertise

##  Project Structure

```
Natpudan-/
├── backend/                      # FastAPI server
│   ├── app/
│   │   ├── main.py              # Application entry point
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── database.py          # Database configuration
│   │   ├── api/                 # API route handlers
│   │   │   ├── auth_new.py      # Authentication (JWT, OAuth2)
│   │   │   ├── chat_new.py      # Chat and AI conversations
│   │   │   ├── discharge.py     # Discharge summary generation
│   │   │   ├── treatment.py     # Treatment plans
│   │   │   ├── timeline.py      # Patient timelines
│   │   │   ├── analytics.py     # Dashboard analytics
│   │   │   └── fhir.py          # FHIR integration
│   │   ├── services/            # Business logic
│   │   │   ├── vector_knowledge_base.py    # Vector embeddings (FAISS)
│   │   │   ├── drug_interactions.py        # Medication checker
│   │   │   ├── rag_service.py             # Retrieval-augmented generation
│   │   │   └── icd10_service.py           # ICD-10 code mapping
│   │   └── websocket_handlers.py # Real-time streaming
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Unit and integration tests
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables (create manually)
│
├── frontend/                     # React + Vite web app
│   ├── src/
│   │   ├── main.tsx             # React entry point
│   │   ├── App.tsx              # Router setup
│   │   ├── pages/               # Page components
│   │   ├── components/          # Reusable UI components
│   │   ├── services/            # API client and utilities
│   │   ├── context/             # React Context (auth, etc.)
│   │   └── styles/              # Global styles
│   ├── vite.config.ts           # Vite build configuration
│   ├── package.json             # NPM dependencies
│   └── tsconfig.json            # TypeScript configuration
│
├── data/                        # Knowledge base and resources
│   ├── knowledge_base/          # Medical PDFs and FAISS index
│   └── icd_codes/               # ICD-10 code database
│
├── docs/                        # Documentation
├── scripts/                     # Helper scripts
├── docker-compose.yml           # Docker composition for production
├── start-app.ps1               # PowerShell startup script
├── init_db_manual.py           # Manual database initialization
└── README.md                   # This file
```

## Repository Cleanup

This repository has been cleaned to remove unnecessary build artifacts and virtual environments that bloat repository size:

### Files Removed

- **`frontend/release/`** - Electron packaged app binaries (dist: ~190+ MB)
- **`.venv/`, `.venv311/`, `backend/.venv/`** - Python virtual environment caches (~500 MB total)

### Why These Were Removed

- **Build artifacts** are regenerated during deployment; storing them in version control wastes storage and slows down clones
- **Virtual environments** are machine-specific and platform-dependent; they should be recreated locally using `python -m venv` and `pip install -r requirements.txt`

### Keeping the Repository Clean

```bash
# Don't commit virtual environments
echo ".venv/
.venv311/
backend/.venv/
venv/"  >> .gitignore

# Don't commit build outputs
echo "frontend/release/
frontend/dist/
backend/dist/
*.egg-info/
__pycache__/
*.pyc"  >> .gitignore

# Clean up if accidentally added
git rm -r --cached .venv/ backend/.venv/ frontend/release/ 2>/dev/null
git commit -m "chore: remove virtual environments and build artifacts"
```

### Dependency Installation

Always reproduce dependencies locally:

```bash
# Backend
cd backend
python -m venv .venv
.venv/Scripts/activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m alembic upgrade head

# Frontend
cd frontend
npm ci  # Use npm ci instead of npm install for reproducible builds
```

##  Support

For issues and questions:

- GitHub Issues: <https://github.com/drkvvk2015/Natpudan-/issues>
- Check existing documentation and troubleshooting guide first

---

**Note**: This application is for educational and professional use. Always verify AI-generated medical information with qualified healthcare professionals.
