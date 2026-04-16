# Natpudan AI Medical Assistant

A production-ready **FastAPI + React/TypeScript** full-stack medical AI application with intelligent diagnostics, role-based access control, and comprehensive patient management.

## Features

| Category | Capability |
|----------|-----------|
| **AI** | GPT-4 chat, clinical diagnosis, discharge summaries, OCR medical report parsing |
| **Knowledge Base** | Vector search (FAISS), hybrid BM25+vector, RAG queries, PubMed integration |
| **PDF Engine** | Large PDF upload, OCR extraction (Tesseract/pdf2image), duplicate detection, background processing queue |
| **Patient Management** | Intake forms, medical timeline, treatment plans, medication follow-ups |
| **Reports** | OPD case sheet PDF, prescription PDF, medical history PDF generation |
| **Analytics** | Demographics, disease trends, risk assessment, treatment outcomes |
| **Drug Checker** | Real-time interaction warnings with severity classification |
| **Authentication** | JWT + OAuth2 (Google, GitHub, Microsoft), multi-tab sync |
| **FHIR** | Healthcare interoperability standard (patient resources, observations, conditions) |
| **Multi-Platform** | Web PWA, Android/iOS (Capacitor), Windows/Linux Desktop (Electron) |

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite/PostgreSQL, OpenAI API
- **Frontend**: React 18, TypeScript, Vite 7, MUI v5, React Router v6
- **AI/ML**: OpenAI GPT-4, FAISS vector embeddings, TinyLLama (local), Ollama (local)
- **PDF**: PyMuPDF, Tesseract OCR, pdf2image
- **Deploy**: Docker Compose, Capacitor (mobile), Electron (desktop)

---

## Quick Start (Windows)

```powershell
git clone https://github.com/drkvvk2015/Natpudan-.git
cd Natpudan-
.\start-app.ps1
```

Opens:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs

---

## Manual Setup

### 1. Backend

```powershell
# From project root — create & activate Python 3.11 venv
python -m venv .venv311
.\.venv311\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
Copy-Item backend/.env.example backend/.env
# Edit backend/.env — add OPENAI_API_KEY and SECRET_KEY

# Start backend
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Default Dev Login

```
Email:    admin@natpudan.local
Password: admin123
Role:     Admin
```

---

## Environment Variables

### `backend/.env`

```env
# Database (SQLite for dev, PostgreSQL for prod)
DATABASE_URL=sqlite:///./natpudan.db

# JWT
SECRET_KEY=your-secret-key   # python -c "import secrets; print(secrets.token_urlsafe(32))"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OpenAI (required for full AI features)
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o

# AI Provider fallback chain: embedded -> ollama -> openai
AI_PROVIDER=auto
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Optional OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=

FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
ENVIRONMENT=development
```

### `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## Role-Based Access Control

| Feature | Staff | Doctor | Admin |
|---------|:-----:|:------:|:-----:|
| Patient Intake | YES | YES | YES |
| AI Chat | YES | YES | YES |
| AI Diagnosis | - | YES | YES |
| Knowledge Base | - | YES | YES |
| Drug Interaction Checker | - | YES | YES |
| Treatment Plans | - | YES | YES |
| Report PDF Generation | - | YES | YES |
| Analytics Dashboard | - | YES | YES |
| FHIR Explorer | - | - | YES |
| User Management | - | - | YES |

---

## API Overview

| Prefix | Description |
|--------|-------------|
| `/api/auth` | Register, login, OAuth, password reset |
| `/api/chat` | AI chat conversations |
| `/api/medical/diagnosis` | AI diagnosis from symptoms |
| `/api/medical/knowledge` | Knowledge base search, RAG, hybrid search |
| `/api/reports` | OPD case sheet, prescription, medical history PDFs |
| `/api/treatment` | Treatment plan management |
| `/api/timeline` | Patient medical timeline |
| `/api/analytics` | Dashboard analytics |
| `/api/fhir` | FHIR resources |
| `/health` | Health check |
| `/health/detailed` | System metrics (CPU, memory, disk) |

---

## Building for Production

```powershell
# Web build
cd frontend ; npm run build:web

# Docker (full stack with PostgreSQL)
docker-compose up --build

# Android APK (requires Android Studio)
npm run build:android

# Windows Electron desktop
npm run build:windows
```

---

## Testing

```powershell
cd backend
pytest                        # all tests
pytest --cov=app              # with coverage
pytest tests/test_api.py -v   # specific file
```

---

## Project Structure

```
Natpudan-/
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers (auth, chat, diagnosis, knowledge_base, reports...)
│   │   ├── services/     # Business logic (OCR, vector KB, drug interactions, RAG...)
│   │   ├── models.py     # SQLAlchemy ORM models
│   │   ├── database.py   # DB session management + auto-migrations
│   │   └── main.py       # FastAPI app entrypoint
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/        # React page components
│   │   ├── components/   # Shared UI components
│   │   ├── services/     # API clients (apiClient, opdCaseSheetService...)
│   │   └── context/      # Auth context
│   └── vite.config.ts
├── start-app.ps1             # One-command dev startup (Windows)
└── docker-compose.yml        # Production deployment
```

---

## Troubleshooting

**Port conflict on 8000**
Backend auto-tries 8001. Update `VITE_API_BASE_URL` in `frontend/.env` if needed.

**Missing Python packages**
```powershell
pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart pydantic-settings psutil openai PyMuPDF faiss-cpu Pillow pytesseract pdf2image
```

**Android build fails**
Requires Android Studio with SDK. Set the `ANDROID_HOME` environment variable.

**AI features not working**
Set `OPENAI_API_KEY` in `backend/.env`. Use `AI_PROVIDER=auto` to fall back to local models (Ollama/TinyLLama).

---

## License

MIT
