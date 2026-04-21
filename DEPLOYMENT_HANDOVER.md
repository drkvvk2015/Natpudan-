# Natpudan AI: Deployment Handover

## 1. System Overview
Natpudan AI has been significantly refactored from an earlier monolithic structure into a modular full-stack medical assistant. This document summarizes current deployment posture and operational expectations.

### Core Architecture
- **Backend**: FastAPI with modular router design and service-oriented backend logic.
- **Frontend**: React (TypeScript) with Vite. Monolithic pages have been split into Atomic Components.
- **AI Engine**: Integrated Autonomous Research Agent (PubMed/Literature) and predictive ML models.
- **Database/Storage**: SQLite or PostgreSQL (depending on environment), plus vector knowledge base for semantic search.

## 2. Key Refactoring & Security (Completed)
- **Modularization**:
    - `main.py` reduced from 1,000+ lines to a lean initialization script.
    - `Diagnosis.tsx` deconstructed into 6 reusable sub-components.
- **Security Hardening**:
    - **Stable Sessions**: Random `SECRET_KEY` generation fixed to prevent session drops.
    - **Token Protection**: Password reset tokens removed from API responses (Email-only delivery).
    - **OAuth**: State validation implemented to prevent CSRF.
- **Resilience**:
    - Global **React Error Boundaries** prevent UI crashes.
    - **Skeleton Loaders** and **Toast Notifications** added for professional UX.

## 3. AI Self-Reliance Model
The system includes autonomous research and enrichment capabilities:
- **Live Research**: The UI now fetches latest medical papers via PubMed as the physician types a diagnosis.
- **Knowledge Growth**: Background workers automatically identify "Knowledge Gaps" and fetch research to fill them.
- **Predictive Risk**: `ReadmissionPredictor` provides clinical risk scores with confidence intervals and intervention suggestions.

## 4. Deployment Instructions

### Prerequisites
- Docker & Docker Compose
- OpenAI API Key
- SMTP Credentials (for password reset emails)

### Production Launch
1. **Configure Environment**:
   Update `backend/.env.production` with:
   - `SECRET_KEY`: A long random string
   - `REDIS_URL`: `redis://redis:6379/0`
   - `DATABASE_URL`: Your PostgreSQL connection string

2. **Build and Start**:
   ```bash
   docker-compose up -d --build
   ```

3. **Database Migrations**:
   The system uses Alembic. Run migrations:
   ```bash
   docker exec physician-ai-backend alembic upgrade head
   ```

## 5. Maintenance & Monitoring
- **Health Checks**: Access `/health` for basic heartbeats or `/health/detailed` for expanded system metrics.
- **CI/CD**: Any push/PR to configured repository branches triggers automated checks via GitHub Actions.
- **Logs**: Structured JSON logging is enabled for integration with ELK or CloudWatch.

---
**Status:** Deployment-ready with ongoing hardening  
**Version:** 1.0.0  
**Date:** 2026-04-21
