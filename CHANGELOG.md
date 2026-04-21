# Changelog

## Unreleased

### Added
- Optional OpenTelemetry bootstrap utility in `backend/app/telemetry.py`
- Prometheus metrics recording and `/metrics` endpoint integration
- Modular backend routers:
  - `backend/app/api/medical.py`
  - `backend/app/api/upload.py`
- Diagnosis UI subcomponents under `frontend/src/components/diagnosis/`:
  - `ComplaintForm.tsx`
  - `DiagnosticOutput.tsx`
  - `InvestigationHub.tsx`
  - `PhysicalExam.tsx`
  - `ResearchDashboard.tsx`
  - `VitalsPanel.tsx`
- Repository documentation refresh in `README.md` covering:
  - current validation status
  - canonical health endpoints
  - modular diagnosis architecture
  - autonomous research agent visibility
- Backend test coverage expansion:
  - `test_readmission_predictor.py`
  - `test_voice_transcriber.py`
  - `test_hybrid_search.py`
  - `test_wearable_sync.py`
  - `test_vector_kb.py`
  - integration tests under `backend/tests/integration/`
- Backend smoke coverage modernization in `backend/tests/test_enhanced_kb.py`
- Frontend test scaffolding:
  - unit test setup with Vitest + Testing Library
  - initial `ErrorBoundary` component test
  - Playwright smoke e2e test scaffold
- Documentation additions:
  - `docs/architecture.md`
  - `docs/deployment.md`

### Changed
- `frontend/src/App.tsx` now wraps route tree in `ErrorBoundary`
- `backend/app/main.py` now records per-request Prometheus metrics
- `backend/app/main.py` module header updated for production intent clarity
- `backend/app/main.py` now exposes canonical `/`, `/health`, `/health/detailed`, and `/metrics` contracts through the main app entrypoint
- `backend/app/container.py` now registers modular medical and upload routers
- `backend/app/core/config.py` now accepts both JSON-array and comma-separated `CORS_ORIGINS` values
- `backend/app/api/treatment.py` now carries its router prefix internally
- `frontend/src/components/ErrorBoundary.tsx` was modernized for cleaner TypeScript/runtime behavior
- `frontend/src/pages/Diagnosis.tsx` was refactored toward a modular diagnosis workspace

### Security/Hardening
- Continued hardening work from previous pass (OAuth state, reset-token secrecy, attribution, rate limit behavior)
- Password reset responses in `backend/app/api/auth_new.py` no longer expose reset tokens
- Demo wearable seed/token paths in `backend/app/api/wearable_auth.py` now carry explicit security annotations for static analysis clarity
- CI workflow updated toward least-privilege / current-action standards in `.github/workflows/ci.yml`
