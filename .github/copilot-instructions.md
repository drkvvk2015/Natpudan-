# Natpudan AI Medical Assistant - AI Agent Instructions

## Project Overview
Full-stack medical AI assistant with FastAPI backend + React/TypeScript frontend. Multi-platform deployment (Web/PWA, Android/iOS via Capacitor, Windows/Linux via Electron). Features AI-powered medical diagnosis, prescription generation, knowledge base search, and patient management with RBAC (staff/doctor/admin roles).

## Architecture

### Backend (FastAPI)
- **Entry point**: `backend/app/main.py` - Includes all routers, CORS middleware, startup DB initialization
- **Database**: SQLAlchemy ORM with SQLite (dev) or PostgreSQL (prod). Models in `backend/app/models.py`
  - Uses `backend/app/database.py` for session management (`get_db()` dependency)
  - Initialize schema: `init_db()` called on startup event
- **API Structure**: Modular routers in `backend/app/api/`:
  - `auth_new.py` - JWT authentication (login/register/OAuth)
  - `chat_new.py` - Chat with AI assistant
  - `discharge.py` - Discharge summary generation
  - `treatment.py` - Treatment plans, medications, follow-ups
  - `timeline.py` - Patient medical timeline/events
  - `analytics.py` - Demographics, disease trends
  - `fhir.py` - FHIR data integration
  - `health.py` - Health checks and system metrics
- **Services** (`backend/app/services/`):
  - `vector_knowledge_base.py` - OpenAI embeddings + FAISS for medical PDF search
  - `drug_interactions.py` - Rule-based drug interaction checker with severity classification
  - `rag_service.py` - Retrieval-augmented generation for medical queries
  - `icd10_service.py` - ICD-10 code mapping
  - `pdf_generator.py` - Medical document generation
- **WebSocket**: Real-time streaming in `backend/app/websocket_handlers.py` - `ConnectionManager` class for user sessions

### Frontend (React + TypeScript + Vite)
- **Entry**: `frontend/src/main.tsx` [RIGHT] `App.tsx` (React Router setup)
- **Routing**: Role-based protected routes via `ProtectedRoute` component
  - Public: Login, Register, Password Reset
  - Staff: Patient intake, chat
  - Doctor: All of staff + diagnosis, drugs, knowledge base, treatment plans, analytics
  - Admin: Full access including FHIR explorer
- **State**: `AuthContext` for user authentication state
- **API Config**: Vite proxy (`vite.config.ts`) routes `/api` and `/health` to backend
  - Default backend: `http://127.0.0.1:8000` (configurable via `VITE_API_BASE_URL`)
- **Multi-Platform**:
  - PWA: `service-worker.js`, `pwa-utils.ts` (offline support, install prompts)
  - Native: `native-utils.ts` (Capacitor plugins: Camera, Geolocation, Haptics, etc.)

## Development Workflows

### Starting the Application
**Use PowerShell scripts** (Windows environment):
- **Full stack**: `.\start-dev.ps1` - Orchestrates backend + frontend, waits for health check
- **Backend only**: `.\start-backend.ps1` - Auto-selects port 8000 (fallback 8001), activates venv
- **Ports**: Backend typically on 8000, Frontend dev on 5173, Frontend preview on 3000

### Environment Setup
1. Backend: Create `.env` in `backend/` with:
   - `DATABASE_URL` - SQLite or PostgreSQL connection string
   - `OPENAI_API_KEY` - Required for AI features
   - `SECRET_KEY` - JWT signing key
   - OAuth credentials (optional): `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, etc.
2. Frontend: Uses Vite env vars (`VITE_API_BASE_URL`, `VITE_WS_URL`)

### Database Operations
- **Initialize**: Auto-runs on backend startup via `init_db()` in `main.py`
- **Manual init**: `backend/init_db_manual.py`
- **Migrations**: Alembic-ready (see `alembic/` if present)
- **Schema**: All models inherit from `Base` in `models.py`

### Testing
- **Backend tests**: `backend/tests/` - Uses pytest with `conftest.py` fixtures
  - Run: `pytest backend/tests/`
  - Test categories: `test_api.py`, `test_medical_report_parsing.py`, `test_websocket.py`
- **Test utilities**: `backend/test_*.py` scripts for integration testing (e.g., `test_patient_intake.ps1`)

### Building Multi-Platform
- **Web**: `npm run build:web` (outputs to `frontend/dist/`)
- **Android**: `npm run build:android` [RIGHT] `gradlew assembleRelease` (APK in `frontend/android/app/build/outputs/`)
- **Windows/Linux**: Electron builder - `npm run build:windows`, `npm run build:linux`
- **Docker**: `docker-compose.yml` includes backend, frontend, PostgreSQL. Deploy via `.\deploy-production.ps1`

## Key Conventions & Patterns

### API Endpoints
- **Prefix**: All API routes under `/api/` namespace (proxied by Vite)
- **Router registration**: Routers imported and included in `main.py` with prefixes:
  - `/api/auth` - Authentication (login, register, OAuth, password reset)
  - `/api/chat` - Chat conversations
  - `/api/discharge` - Discharge summaries
  - `/api/treatment-plans` - Treatment management
  - `/api/timeline` - Patient timelines
  - `/api/analytics` - Dashboard analytics
  - `/api/fhir` - FHIR resources
  - `/api/medical` - Medical operations (diagnosis, knowledge base search)
- **Health checks**: `/health` (basic), `/health/detailed` (system metrics with psutil)
- **Authentication**: JWT tokens via `Authorization: Bearer <token>` header
  - Token creation: `jwt.encode()` with `SECRET_KEY`, `ALGORITHM`, expiry
  - OAuth2: `OAuth2PasswordBearer(tokenUrl="api/auth/login")`
- **Request/Response**: Pydantic `BaseModel` for validation (e.g., `RegisterRequest`, `LoginRequest`, `TokenResponse`)
- **Error handling**: Raise `HTTPException` with appropriate status codes

### Database Patterns
- **Sessions**: Always use `db: Session = Depends(get_db)` in route handlers
  - `get_db()` yields session, automatically closes after request
  - SQLite: Uses `StaticPool`, `check_same_thread=False`
  - PostgreSQL: Uses `pool_pre_ping=True` for connection health checks
- **Relationships**: Defined in models with `relationship()`, use `back_populates`
  - Example: `User.conversations` ↔ `Conversation.user`
  - Cascade deletes: `cascade="all, delete-orphan"`
- **Enums**: Python `str, enum.Enum` for status fields
  - `UserRole`: STAFF, DOCTOR, ADMIN
  - `TreatmentStatus`: ACTIVE, COMPLETED, DISCONTINUED, ON_HOLD
  - `MedicationFrequency`: ONCE_DAILY, TWICE_DAILY, AS_NEEDED, etc.
  - `MedicationRoute`: ORAL, INTRAVENOUS, TOPICAL, etc.
  - `FollowUpStatus`: SCHEDULED, COMPLETED, MISSED, CANCELLED
- **CRUD pattern**: Functions in `backend/app/crud.py` (e.g., `get_user_by_email`, `create_user`, `authenticate_user`)
- **Timestamps**: `created_at`, `updated_at` with `default=datetime.utcnow`, `onupdate=datetime.utcnow`

### Frontend API Calls
- **API Client**: Uses `frontend/src/services/apiClient.ts` - preconfigured axios instance
- **Auth pattern**: `localStorage.getItem('token')` [RIGHT] `Authorization: Bearer <token>` header
  - `AuthContext` automatically sets/removes token in axios defaults
  - Multi-tab sync via `storage` event listener
- **Error handling**: Try/catch with user-friendly error messages
- **Custom events**: `authStateChanged` event dispatched on login/logout for component synchronization

### Role-Based Access Control
- **Enforcement**: Frontend via `ProtectedRoute` component checking `allowedRoles` prop
- **Backend**: Can add `Depends(get_current_user)` with role checks (partially implemented)
- **User model**: `User.role` enum (staff/doctor/admin)

### Medical AI Integration
- **OpenAI**: Primary LLM for diagnosis, chat, prescription generation
  - Model: `gpt-4-turbo-preview` (configurable via `OPENAI_MODEL` env var)
  - API key: Required in `OPENAI_API_KEY` env var
- **Embeddings**: `text-embedding-3-small` for semantic search (cached in `VectorKnowledgeBase`)
  - Cache directory: `backend/cache/online_knowledge/`
  - FAISS index: `backend/data/knowledge_base/faiss.index`
- **Knowledge base**: PDFs in `backend/data/knowledge_base/` [RIGHT] chunked (500-1000 chars) [RIGHT] FAISS index
  - Statistics endpoint: `/api/medical/knowledge/statistics`
  - Search endpoint: `/api/medical/knowledge/search` (POST with `{"query": "...", "top_k": 5}`)
- **ICD-10 codes**: Service in `icd10_service.py` - suggests codes from symptoms
- **Drug interactions**: Rule-based system with hardcoded interaction database
  - `DrugInteractionChecker` class with severity classification (HIGH/MODERATE/LOW)
  - Endpoint: `/api/prescription/check-interactions`
- **Advanced services** (in `backend/app/services/`):
  - `rag_service.py` - Retrieval-augmented generation
  - `hybrid_search.py` - Combines vector + keyword search
  - `medical_entity_extractor.py` - Extract entities from medical text
  - `pubmed_integration.py` - PubMed article search
  - `knowledge_graph.py` - Medical knowledge graph

## Critical Integration Points

### WebSocket for Real-Time Features
- **Endpoint**: `/ws/{user_id}` - Managed by `ConnectionManager` in `websocket_handlers.py`
- **Connection lifecycle**:
  - `connect()` - Accepts WebSocket, stores in `active_connections` dict, sends confirmation
  - `disconnect()` - Removes from connections and sessions
  - Tracks session metadata: `connected_at`, `messages_sent`, `current_session_id`
- **Message types**: `connection`, `stream`, `progress`, `diagnosis`, `prescription`
- **Methods**:
  - `send_message()` - Send JSON to specific user
  - `send_stream_chunk()` - Streaming content with metadata
  - `send_progress()` - Progress updates with stage/percentage
- **Usage**: Live diagnosis streaming, real-time chat updates, prescription generation progress

### File Upload & Processing
- **PDFs**: Large file handling with session-based chunking (see `app/main.py` upload endpoints)
- **Medical reports**: Parsed via PyMuPDF [RIGHT] entity extraction [RIGHT] structured data

### FHIR Integration
- **Purpose**: Healthcare interoperability standard
- **API**: `backend/app/api/fhir.py` - Patient resources, observations, conditions
- **Frontend**: `FHIRExplorer` page for viewing/exporting FHIR data

## Common Pitfalls & Notes

- **Port conflicts**: Backend auto-switches 8000[RIGHT]8001 if needed (see `start-backend.ps1`)
  - Frontend Vite proxy defaults to `http://127.0.0.1:8000`
  - Override via `VITE_API_BASE_URL` or `VITE_BACKEND_URL` env var
  - WebSocket proxy automatically converts `http` [RIGHT] `ws`
- **CORS**: Configured in `main.py` for localhost origins (`localhost:5173`, `localhost:3000`, `127.0.0.1:5173`, `127.0.0.1:3000`)
  - Update `allow_origins` list for production domains
  - Includes `allow_credentials=True` for cookie support
- **OpenAI costs**: Embeddings cached in `backend/cache/`, but diagnosis/chat calls are NOT cached - monitor usage
- **SQLite limitations**: Single-writer, no concurrent writes - use PostgreSQL for production
  - Development: `DATABASE_URL=sqlite:///./natpudan.db`
  - Production: `DATABASE_URL=postgresql://user:password@host:5432/database`
- **Capacitor native features**: Only work in native builds, not in browser
  - Check platform: `isNative()` from `native-utils.ts`
  - Platform detection: `platform()` returns `'android' | 'ios' | 'web'`
- **Service worker**: Only registers in production mode (`npm run build` + `npm run preview`)
  - PWA features (install prompt, offline) only work after build
  - Development mode uses Vite's HMR instead
- **Multi-platform builds**: Require platform-specific SDKs
  - Android: Android Studio + Gradle (APK: `gradlew assembleRelease`)
  - iOS: Xcode + CocoaPods (requires macOS)
  - Windows: Electron builder (NSIS installer)
  - Linux: Electron builder (AppImage/deb/rpm)
- **Environment variables**: Backend reads from `backend/.env`, frontend from Vite env vars (`VITE_*`)
  - Frontend cannot access non-`VITE_` prefixed vars for security
- **Authentication state**: Persisted in `localStorage.token`
  - Multi-tab sync via `storage` event listener in `AuthContext`
  - Token automatically added to all axios requests via `apiClient` interceptor

## Key Files Reference
- **Backend entrypoint**: `backend/app/main.py`
- **Frontend entrypoint**: `frontend/src/main.tsx` [RIGHT] `App.tsx`
- **Database schema**: `backend/app/models.py`
- **Auth logic**: `backend/app/api/auth_new.py`, `frontend/src/context/AuthContext.tsx`
- **Startup scripts**: `start-dev.ps1`, `start-backend.ps1`
- **Build configs**: `vite.config.ts`, `capacitor.config.json`, `docker-compose.yml`
- **Documentation**: `README.md`, `QUICKSTART_GUIDE.md`, `CURRENT_STATUS.md`

## Current Development Status
- [OK] Core features functional: Auth, Chat, Diagnosis, Drug checker, Knowledge base, Patient management, Treatment plans, Analytics
- 🚧 Partial implementation: Drug interaction logic (rule-based, needs external API), Knowledge base search (needs full semantic search)
- [EMOJI] Not yet integrated: Full OAuth flow, Production-ready auth middleware, Comprehensive error handling
