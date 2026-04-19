# Deployment Guide

## Environments

- **Development**: SQLite + local frontend/backend processes
- **Production**: PostgreSQL + containerized backend/frontend

## Required Configuration

Backend `backend/.env` minimum:

- `SECRET_KEY`
- `DATABASE_URL`
- `OPENAI_API_KEY` (for AI features)
- `FRONTEND_URL`

Optional observability:

- `SENTRY_DSN`
- `OTEL_EXPORTER_OTLP_ENDPOINT`

## Docker Deployment

Use the project-level container build and `docker-compose.yml`.

1. Build images
2. Start services
3. Verify:
   - `/health`
   - `/health/detailed`
   - `/metrics` (if enabled)

## Rollout Checklist

- Run backend tests
- Run frontend type checks and lint
- Apply DB migrations before app rollout
- Validate OAuth callback URLs
- Verify CORS origins for production domains
- Confirm TLS certificates and reverse-proxy settings

## Post-Deploy Validation

- Authentication (login + password reset email path)
- Chat/medical endpoints
- PDF upload and search
- Monitoring endpoints
- Worker loops active in logs
