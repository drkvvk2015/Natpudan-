# Architecture Overview

Natpudan is a full-stack medical assistant platform with:

- **Backend**: FastAPI + SQLAlchemy (SQLite for local, PostgreSQL in production)
- **Frontend**: React + TypeScript + Vite
- **AI Services**: OpenAI chat/completions + embeddings, retrieval via FAISS
- **Deployment targets**: Web/PWA, Android/iOS (Capacitor), Desktop (Electron), Docker

## Backend Layers

1. **API routers** (`backend/app/api/*`) expose role-aware HTTP endpoints.
2. **Service layer** (`backend/app/services/*`) provides AI, PDF, KB, and domain logic.
3. **Persistence** (`backend/app/models.py`, `backend/app/database.py`) handles ORM entities and sessions.
4. **Cross-cutting** (`middleware`, `monitoring`, `telemetry`, `logging_config`) handles observability and resilience.

## Frontend Layers

1. **Routing/App shell** in `frontend/src/App.tsx` with protected/public routes.
2. **Context/state** via `AuthContext`.
3. **Views** under `frontend/src/pages/*`.
4. **Reusable UI** under `frontend/src/components/*`.

## Runtime Background Work

- Upload queue processing worker
- Wearable sync worker
- Knowledge base growth worker

These workers are started during application lifespan startup and stopped during graceful shutdown.

## API Versioning

Current routes are mounted under `/api`, with compatibility aliasing under `/api/v1` to support incremental API evolution.

## Observability

- `/health` and `/health/detailed` for service/system probes
- `/metrics` for Prometheus exposition (when Prometheus client is installed)
- Optional Sentry and OpenTelemetry support controlled by environment variables
