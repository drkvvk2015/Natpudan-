# Natpudan AI Medical Assistant

A full-stack **FastAPI + React/TypeScript** medical AI platform for clinical workflows, patient management, knowledge-assisted diagnosis, and multi-platform delivery across web, mobile, and desktop.

[![CI](https://github.com/drkvvk2015/Natpudan-/actions/workflows/ci.yml/badge.svg)](https://github.com/drkvvk2015/Natpudan-/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Current Repository Status (April 2026)

This repository has recently been debugged and hardened against the project’s current standards.

| Area | Current status |
|------|----------------|
| Frontend lint | Verified passing |
| Frontend typecheck | Verified passing |
| Frontend production build | Verified passing |
| Frontend unit tests | Verified passing |
| Backend startup + contract smoke tests | Verified passing |
| Canonical health endpoints | `/`, `/health`, `/health/detailed`, `/metrics` available in `backend/app/main.py` |
| Static checks | Trunk active issues reduced to `0` in the latest validation pass |

> Note: a subset of older backend auth/API tests is still being modernized, so the full backend suite is improved but not yet fully green.

---

## Highlights

| Area | Capability |
|------|------------|
| **Clinical AI** | Symptom-based diagnosis, live diagnosis workflows, discharge summaries, treatment recommendation hooks |
| **Knowledge Systems** | FAISS vector search, hybrid search, RAG-style querying, knowledge graph features |
| **Autonomous Research** | Gap-driven literature review, synthesis, validation, and KB enrichment via `autonomous_research_agent.py` |
| **Patient Workflows** | Intake, timeline, treatment plans, follow-up, reports, analytics |
| **Voice & Documents** | Whisper transcription, report parsing, PDF upload/indexing, SOAP-oriented flows |
| **Device & Interop** | Wearable integration, FHIR support, multi-platform deployment |
| **Observability** | Prometheus metrics, health endpoints, telemetry hooks, structured logging |

---

## Recent Engineering Updates

- Canonical backend contracts restored in `backend/app/main.py` for `/`, `/health`, `/health/detailed`, and `/metrics`
- Backend routing modularized further with dedicated `backend/app/api/medical.py` and `backend/app/api/upload.py`
- `CORS_ORIGINS` parsing hardened in `backend/app/core/config.py` to support both JSON arrays and comma-separated `.env` values
- `frontend/src/pages/Diagnosis.tsx` is being split into smaller diagnosis-focused UI components under `frontend/src/components/diagnosis/`
- `frontend/src/components/ErrorBoundary.tsx` was modernized and fixed for TypeScript/runtime correctness
- Password-reset flow in `backend/app/api/auth_new.py` no longer returns reset tokens in API responses

---

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite/PostgreSQL, OpenAI integrations, scikit-learn
- **Frontend**: React 18, TypeScript, Vite 7, MUI v5, React Router v6, Recharts
- **AI/ML**: OpenAI models, Whisper, FAISS, local/embedded fallbacks, Ollama support
- **PDF / OCR**: PyMuPDF, Tesseract OCR, pdf2image
- **Testing**: pytest, pytest-asyncio, Vitest, Testing Library, Playwright
- **Operations**: Docker Compose, Capacitor, Electron, Prometheus, OpenTelemetry, Sentry hooks

---

## Quick Start (Windows)

```powershell
git clone https://github.com/drkvvk2015/Natpudan-.git
cd Natpudan-
.\start-app.ps1
```

Typical local endpoints:

- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`

---

## Manual Setup

### Backend

```powershell
python -m venv .venv311
.\.venv311\Scripts\Activate.ps1
pip install -r backend/requirements.txt
Copy-Item backend/.env.template backend/.env
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

---

## Environment Variables

### `backend/.env`

```env
DATABASE_URL=sqlite:///./natpudan.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o
WHISPER_MODEL=whisper-1

AI_PROVIDER=auto
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000

FITBIT_CLIENT_ID=
FITBIT_CLIENT_SECRET=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=

SENTRY_DSN=
OTEL_EXPORTER_OTLP_ENDPOINT=
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
| Analytics Dashboard | - | YES | YES |
| FHIR Explorer | - | - | YES |
| User Management | - | - | YES |

---

## API Overview

| Prefix | Description |
|--------|-------------|
| `/api/auth` | Register, login, OAuth, password reset |
| `/api/chat` | AI chat conversations |
| `/api/medical/diagnosis` | Diagnosis suggestions from symptoms |
| `/api/medical/live-diagnosis` | Rich clinical-context diagnosis workflow |
| `/api/medical/live-diagnosis/suggest-treatment` | Treatment recommendation compatibility endpoint |
| `/api/medical/knowledge/*` | Knowledge search, RAG, PubMed, hybrid search, graph features |
| `/api/upload` | Knowledge/document upload and document management |
| `/api/treatment` | Treatment plan management |
| `/api/timeline` | Patient medical timeline |
| `/api/analytics` | Dashboard analytics |
| `/api/fhir` | FHIR resources |
| `/health` | Basic health probe |
| `/health/detailed` | Detailed system metrics |
| `/metrics` | Prometheus metrics exposition |

---

## Architecture

```text
Frontend (React + TypeScript + Vite)
        |
        | HTTP / WebSocket
        v
FastAPI application (`backend/app/main.py`)
        |
        +-- Modular API routers (`backend/app/api/*`)
        +-- Services layer (`backend/app/services/*`)
        +-- Persistence (`backend/app/models.py`, `database.py`)
        +-- Monitoring / telemetry / metrics
```

### Notable backend modules

- `backend/app/api/medical.py` — diagnosis, ICD lookup, KB, RAG, graph endpoints
- `backend/app/api/upload.py` — document upload and KB management
- `backend/app/services/autonomous_research_agent.py` — gap-driven research and KB enrichment loop
- `backend/app/services/readmission_predictor.py` — risk scoring and intervention recommendations

### Notable frontend modules

- `frontend/src/pages/Diagnosis.tsx` — diagnosis workspace entry point
- `frontend/src/components/diagnosis/ComplaintForm.tsx`
- `frontend/src/components/diagnosis/VitalsPanel.tsx`
- `frontend/src/components/diagnosis/PhysicalExam.tsx`
- `frontend/src/components/diagnosis/InvestigationHub.tsx`
- `frontend/src/components/diagnosis/DiagnosticOutput.tsx`

---

## Testing

```powershell
# Backend smoke / contract checks
cd backend
pytest tests/test_startup.py -q
pytest tests/test_contracts.py -q
pytest tests/test_enhanced_kb.py -q

# Backend broader suite (still being modernized)
pytest tests -q

# Frontend quality gates
cd ..\frontend
npm run lint
npm run typecheck
npm run build:web
npm test
npm run test:unit

# Frontend e2e
npm run test:e2e
```

### Verified in the latest debug pass

- `npm run lint`
- `npm run typecheck`
- `npm run build:web`
- `npm run test:unit`
- backend startup and contract smoke tests

---

## Build Targets

```powershell
# Web
npm run build:web

# Android
npm run build:android

# Windows desktop
npm run build:windows

# Linux desktop
npm run build:linux

# Full stack via Docker
docker-compose up --build
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend port conflict | Backend may fall back to `8001`; update `VITE_API_BASE_URL` if needed |
| Missing Python packages | Reinstall with `pip install -r backend/requirements.txt` |
| AI features unavailable | Set `OPENAI_API_KEY` in `backend/.env` |
| CORS issues in dev | Check `CORS_ORIGINS` formatting in `backend/.env` |
| Android IDE shows duplicate Gradle/plugin errors | These can be editor/indexing artifacts even when the actual Capacitor/Gradle build succeeds |

---

## Documentation

| Document | Description |
|----------|-------------|
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | High-level technical overview |
| [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) | Feature-by-feature setup guidance |
| [DEPLOYMENT_TESTING_GUIDE.md](DEPLOYMENT_TESTING_GUIDE.md) | Development setup, testing, deployment |
| [CHANGELOG.md](CHANGELOG.md) | Release history and recent changes |
| [docs/architecture.md](docs/architecture.md) | Runtime and service architecture |
| [docs/deployment.md](docs/deployment.md) | Deployment guidance |

---

## Known Issues

- Some advanced AI and KB features degrade gracefully when optional dependencies are unavailable.
- Local test execution may require additional dev dependencies in non-standard Python environments.
- `backend/app/main.py` is still a large composition root; modular cleanup is in progress.
- A subset of older backend auth/API tests still uses live-server assumptions and is being refactored toward self-contained test-client patterns.

---

## License

MIT
