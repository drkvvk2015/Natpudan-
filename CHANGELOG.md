# Changelog

## Unreleased

### Added
- Optional OpenTelemetry bootstrap utility in `backend/app/telemetry.py`
- Prometheus metrics recording and `/metrics` endpoint integration
- Backend test coverage expansion:
  - `test_readmission_predictor.py`
  - `test_voice_transcriber.py`
  - `test_hybrid_search.py`
  - `test_wearable_sync.py`
  - `test_vector_kb.py`
  - integration tests under `backend/tests/integration/`
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

### Security/Hardening
- Continued hardening work from previous pass (OAuth state, reset-token secrecy, attribution, rate limit behavior)
