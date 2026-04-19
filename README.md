# Natpudan AI Medical Assistant

A production-ready **FastAPI + React/TypeScript** full-stack medical AI platform with intelligent diagnostics, role-based access control, comprehensive patient management, and enterprise-grade predictive analytics.

[![CI](https://github.com/drkvvk2015/Natpudan-/actions/workflows/ci.yml/badge.svg)](https://github.com/drkvvk2015/Natpudan-/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## What's New in v2.0

| Feature | Description |
|---------|-------------|
| **Voice → Auto Documentation** | Record consultations, auto-transcribe with Whisper, generate SOAP notes |
| **Wearable Integration** | Connect Fitbit/Apple Watch/Garmin, real-time vital sign monitoring |
| **Predictive Readmission Alerts** | ML-powered risk scoring with intervention recommendations |
| **Knowledge Graph Visualization** | Interactive D3.js medical concept explorer |
| **Ambient Transcription** | WebSocket real-time transcription during consultations |
| **XAI Explainability** | Transparent AI reasoning with feature importance |
| **AI Treatment Recommender** | Evidence-based treatment pathways |
| **Clinical Trial Matcher** | Auto-match patients to eligible trials |
| **FHIR Healthcare Connector** | Full HL7/FHIR interoperability |
| **Multi-Language AI** | 50+ language medical translation |
| **Observability** | Prometheus metrics, OpenTelemetry tracing, Sentry error tracking |
| **Test Coverage** | Backend pytest suite, Vitest unit tests, Playwright e2e |

---

## Features

| Category | Capability |
|----------|-----------|
| **AI** | GPT-4 chat, clinical diagnosis, discharge summaries, OCR medical report parsing |
| **Voice AI** | Whisper transcription, SOAP note generation, ambient transcription |
| **Predictive ML** | Readmission risk prediction, patient trajectory forecasting |
| **Wearables** | Fitbit/Apple/Garmin OAuth, real-time vitals, background sync |
| **Knowledge Base** | Vector search (FAISS), hybrid BM25+vector, RAG queries, interactive graph visualization |
| **PDF Engine** | Large PDF upload, OCR extraction (Tesseract/pdf2image), duplicate detection, background processing queue |
| **Patient Management** | Intake forms, medical timeline, treatment plans, medication follow-ups |
| **Reports** | OPD case sheet PDF, prescription PDF, medical history PDF generation |
| **Analytics** | Demographics, disease trends, risk assessment, treatment outcomes, disease heatmaps |
| **Drug Checker** | Real-time interaction warnings with severity classification |
| **Alerts** | Clinical alerts with severity levels, acknowledgment tracking, intervention recommendations |
| **Authentication** | JWT + OAuth2 (Google, GitHub, Microsoft), multi-tab sync |
| **FHIR** | Healthcare interoperability standard (patient resources, observations, conditions), HL7 import |
| **Observability** | Prometheus `/metrics`, OpenTelemetry tracing, Sentry integration, structured logging |
| **Multi-Platform** | Web PWA, Android/iOS (Capacitor), Windows/Linux Desktop (Electron) |

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite/PostgreSQL, OpenAI API, scikit-learn
- **Frontend**: React 18, TypeScript, Vite 7, MUI v5, React Router v6, Recharts, D3.js
- **AI/ML**: OpenAI GPT-4, Whisper, FAISS vector embeddings, TinyLLama (local), Ollama (local)
- **PDF**: PyMuPDF, Tesseract OCR, pdf2image
- **Testing**: pytest + coverage (backend), Vitest + Testing Library (frontend), Playwright (e2e)
- **Observability**: Prometheus, OpenTelemetry, Sentry
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
# Create and activate Python 3.11 venv
python -m venv .venv311
.\.venv311\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
Copy-Item backend/.env.template backend/.env
# Edit backend/.env -- set OPENAI_API_KEY and SECRET_KEY

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
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OpenAI (required for AI features including voice transcription)
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o
WHISPER_MODEL=whisper-1

# AI Provider fallback chain: embedded -> ollama -> openai
AI_PROVIDER=auto
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Wearable Integration (optional)
FITBIT_CLIENT_ID=
FITBIT_CLIENT_SECRET=
FITBIT_REDIRECT_URI=http://localhost:5173/api/wearable/callback/fitbit

# Optional OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=

# Observability (optional)
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
| Voice Documentation | - | YES | YES |
| Wearable Integration | - | YES | YES |
| Knowledge Graph | - | YES | YES |
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
| `/api/voice` | Voice upload, transcription, SOAP generation |
| `/api/voice/consultation` | WebSocket ambient transcription |
| `/api/predictions` | Readmission risk, alerts, high-risk patients |
| `/api/wearable` | Device OAuth, sync, vitals data |
| `/api/knowledge-graph` | D3.js graph export, concept search, paths |
| `/api/features` | XAI, treatment recommender, clinical trials, genomics |
| `/api/reports` | OPD case sheet, prescription, medical history PDFs |
| `/api/treatment` | Treatment plan management |
| `/api/timeline` | Patient medical timeline |
| `/api/analytics` | Dashboard analytics |
| `/api/fhir` | FHIR resources |
| `/health` | Health check |
| `/health/detailed` | System metrics (CPU, memory, disk) |
| `/metrics` | Prometheus metrics exposition |

---

## Architecture

```
                    +------------+
                    |  Frontend   |  React + TypeScript + Vite
                    |  (SPA/PWA) |  MUI v5, Recharts, D3.js
                    +-----+------+
                          | HTTP / WebSocket
                    +-----v------+
                    |  FastAPI    |  JWT auth, CORS, rate limiting
                    |  Backend    |  Prometheus metrics middleware
                    +-----+------+
              +-----------+-----------+
              |           |           |
        +-----v---+ +----v----+ +---v------+
        | API     | |Services | |Background|
        | Routers | |  Layer  | | Workers  |
        +---------+ +----+----+ +----------+
                         |       - Upload queue
              +----------+-------- - Wearable sync
              |          |         - KB growth
        +-----v---+ +---v-----+
        | OpenAI  | |SQLAlchemy|
        | FAISS   | |SQLite/PG |
        | Whisper | +---------+
        +---------+
```

**Backend layers**: API routers → Service layer → Persistence (ORM) + Cross-cutting (middleware, monitoring, telemetry).

**Background workers**: Upload queue processing, wearable sync, knowledge base growth — started during app lifespan, stopped on graceful shutdown.

**Deployment targets**: Web/PWA, Android/iOS (Capacitor), Windows/Linux (Electron), Docker.

---

## v2.0 Feature Details

### Voice → Auto Documentation
- Upload audio recordings (WAV, MP3, M4A, OGG, FLAC)
- Transcription via OpenAI Whisper API
- Automatic medical entity extraction (symptoms, medications, conditions)
- SOAP note auto-generation with RAG grounding
- Create discharge summaries from voice

### Wearable Data Integration
- OAuth 2.0 for Fitbit, Apple Health, Garmin
- Background sync worker (5-minute intervals)
- Real-time heart rate, steps, sleep, SpO2 monitoring
- Time-series data visualization with Recharts

### Predictive Readmission Alerts
- Logistic regression model with 11 patient features
- Risk scoring: Critical/High/Medium/Low
- Feature importance for interpretability
- Automated intervention recommendations
- Alert acknowledgment tracking

### Knowledge Graph Visualization
- Interactive D3.js force-directed graph
- Disease → Symptom → Medication relationships
- Path finding between medical concepts
- SVG export for documentation

### Ambient Transcription
- WebSocket real-time audio streaming
- Live transcription during consultations
- Auto-population of conversation history
- Entity extraction on-the-fly

---

## Testing

```powershell
# Backend -- all tests with coverage
cd backend
pytest --cov=app

# Backend -- specific suite
pytest tests/test_api.py -v
pytest tests/test_readmission_predictor.py -v
pytest tests/test_voice_transcriber.py -v
pytest tests/integration/ -v

# Frontend -- unit tests (Vitest + Testing Library)
cd frontend
npm test

# Frontend -- e2e (Playwright)
npx playwright test
```

---

## Building for Production

```powershell
# Web build
cd frontend && npm run build:web

# Docker (full stack with PostgreSQL)
docker-compose up --build

# Android APK (requires Android Studio)
npm run build:android

# Windows Electron desktop
npm run build:windows
```

---

## Project Structure

```
Natpudan-/
+-- backend/
|   +-- app/
|   |   +-- api/                       # Route handlers
|   |   |   +-- auth_new.py            # JWT + OAuth authentication
|   |   |   +-- chat_new.py            # AI chat endpoints
|   |   |   +-- voice.py               # Voice upload and SOAP generation
|   |   |   +-- voice_consul.py        # WebSocket ambient transcription
|   |   |   +-- predictions.py         # Readmission risk and alerts
|   |   |   +-- wearable_auth.py       # Wearable OAuth
|   |   |   +-- knowledge_graph_viz.py # D3 graph export
|   |   |   +-- futuristic_features.py # XAI, trials, genomics, etc.
|   |   |   +-- health.py              # Health checks and metrics
|   |   |   +-- ...
|   |   +-- services/                  # Business logic
|   |   |   +-- voice_transcriber.py   # Whisper integration
|   |   |   +-- voice_to_soap.py       # SOAP note generation
|   |   |   +-- readmission_predictor.py # ML prediction
|   |   |   +-- ml_trainer.py          # Model training
|   |   |   +-- alert_generator.py     # Clinical alerts
|   |   |   +-- wearable_sync.py       # Device data sync
|   |   |   +-- vector_knowledge_base.py # FAISS vector search
|   |   |   +-- drug_interactions.py   # Drug interaction checker
|   |   |   +-- ...
|   |   +-- models.py                  # SQLAlchemy ORM models
|   |   +-- database.py                # DB session management
|   |   +-- main.py                    # FastAPI app entrypoint
|   |   +-- telemetry.py               # OpenTelemetry bootstrap
|   |   +-- monitoring.py              # Prometheus metrics
|   +-- tests/
|   |   +-- test_api.py
|   |   +-- test_readmission_predictor.py
|   |   +-- test_voice_transcriber.py
|   |   +-- test_hybrid_search.py
|   |   +-- test_wearable_sync.py
|   |   +-- test_vector_kb.py
|   |   +-- integration/               # Integration tests
|   +-- .env.template
|   +-- requirements.txt
+-- frontend/
|   +-- src/
|   |   +-- pages/
|   |   |   +-- VoiceDocumentation.tsx
|   |   |   +-- WearableIntegration.tsx
|   |   |   +-- KnowledgeGraphVisualizer.tsx
|   |   |   +-- Diagnosis.tsx
|   |   |   +-- DrugChecker.tsx
|   |   |   +-- ...
|   |   +-- components/
|   |   |   +-- AlertsWidget.tsx
|   |   |   +-- ErrorBoundary.tsx
|   |   |   +-- ...
|   |   +-- services/                  # API clients
|   |   +-- context/                   # Auth context
|   |   +-- test/                      # Test setup
|   +-- e2e/                           # Playwright e2e tests
|   +-- vitest.config.ts
|   +-- vite.config.ts
+-- docs/
|   +-- architecture.md
|   +-- deployment.md
|   +-- PRODUCTION_CHECKLIST.md
+-- docker-compose.yml
+-- start-app.ps1                      # One-command dev startup (Windows)
+-- CHANGELOG.md
+-- IMPLEMENTATION_SUMMARY.md
```

---

## Database Models (v2.0)

| Model | Description |
|-------|-------------|
| `User` | Authentication, roles (staff/doctor/admin) |
| `Patient` | Demographics, medical history |
| `Conversation` / `Message` | AI chat sessions |
| `TreatmentPlan` / `Medication` / `FollowUp` | Treatment management |
| `VoiceRecording` | Audio files, transcriptions, SOAP linkage |
| `WearableDeviceAuth` | OAuth tokens for wearable devices |
| `WearableDeviceData` | Time-series vital measurements |
| `WearableSyncLog` | Sync audit trail |
| `Alert` | Clinical alerts with severity and recommendations |

---

## Observability

| Endpoint | Description |
|----------|-------------|
| `/health` | Basic liveness probe |
| `/health/detailed` | System metrics — CPU, memory, disk |
| `/metrics` | Prometheus exposition format |

Optional integrations (configured via environment variables):
- **Prometheus** — per-request latency and status code metrics
- **OpenTelemetry** — distributed tracing via OTLP exporter
- **Sentry** — error tracking and performance monitoring

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port conflict on 8000 | Backend auto-tries 8001. Update `VITE_API_BASE_URL` in `frontend/.env`. |
| Missing Python packages | `pip install -r backend/requirements.txt` |
| Android build fails | Requires Android Studio + SDK. Set `ANDROID_HOME` env var. |
| AI features not working | Set `OPENAI_API_KEY` in `backend/.env`. Use `AI_PROVIDER=auto` for local fallback. |
| Voice transcription fails | Ensure valid `OPENAI_API_KEY`. Audio file size must be < 25 MB. |
| Wearable sync not working | Verify OAuth credentials. Check `backend/logs/` for errors. |

---

## Documentation

| Document | Description |
|----------|-------------|
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Complete technical overview of all 15 features |
| [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) | Feature-by-feature setup instructions |
| [DEPLOYMENT_TESTING_GUIDE.md](DEPLOYMENT_TESTING_GUIDE.md) | Development setup, testing, production deployment |
| [CHANGELOG.md](CHANGELOG.md) | Release history and unreleased changes |
| [docs/architecture.md](docs/architecture.md) | Service and runtime architecture map |
| [docs/deployment.md](docs/deployment.md) | Deployment checklist and operational validation |

---

## Known Issues

- Some advanced AI and knowledge services degrade gracefully when optional dependencies are missing (e.g., FAISS, rank-bm25, OpenTelemetry exporters).
- Local test execution may require extra dev dependencies not present in minimal runtime environments.
- `backend/app/main.py` remains a large composition root; incremental modularization is ongoing.

---

## License

MIT
