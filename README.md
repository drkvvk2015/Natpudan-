# Physician AI Assistant

End-to-end FastAPI + React application with role-based access (RBAC) for staff, doctors, and admins. Includes chat, patient intake, diagnosis, knowledge base, analytics, FHIR explorer, timelines, and treatment planning.

## Quickstart

- Backend (FastAPI):
  - Env: copy `backend/.env` (see variables below).
  - Install deps (Windows PowerShell):
    
    ```powershell
    # from repo root
    & .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
    # run API
    Push-Location .\backend; & ..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; Pop-Location
    ```
 
- Frontend (React + Vite):
  - Ensure `frontend/package.json` exists (Dockerfile expects it). If missing, reconstruct or pull latest.
  - Build (Docker multi-stage):
    
    ```powershell
    docker build -t physician-ui .\frontend
    docker run --rm -p 3000:3000 physician-ui
    ```

## RBAC

- Staff: patient data entry, chat.
- Doctor: chat, diagnosis, knowledge base, analytics, FHIR.
- Admin: full access.

## Environment Variables (backend/.env)

- `ENVIRONMENT=development|production`
- `DEBUG=true|false`
- `SECRET_KEY=<random>`
- `DATABASE_URL=sqlite:///./physician_ai.db` (or Postgres URL)
- `OPENAI_API_KEY=<key>`
- CORS: `CORS_ORIGINS=http://localhost:3000`
- Rate limiting: `RATE_LIMIT_CALLS`, `RATE_LIMIT_PERIOD`

## Security

- Python deps pinned in `backend/requirements.txt`.
- Patched: Starlette `0.49.1` for Range header DoS.
- Known advisory without fix: `ecdsa` (GHSA-wj6h-64fc-37mp). Low risk here unless using `SigningKey.sign_digest()`; no direct use in app. Monitor upstream for fix.
- Review Dependabot alerts in GitHub Security tab.

## Testing

```powershell
Push-Location .\backend; & ..\..\.venv\Scripts\python.exe -m pytest -q; Pop-Location
```

## API

- Base: `http://localhost:8000/api`
- Auth: JWT; registration includes `role` and optional `license_number` (doctor).
- WebSocket chat: `ws://localhost:8000/ws/chat`

## Notes

- Large assets (PDF books, DB files, node_modules) are ignored to keep repo clean.
- Use Docker Compose (`docker-compose.yml`) for full stack once frontend manifest is present.
