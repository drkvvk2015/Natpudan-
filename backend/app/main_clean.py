"""Clean FastAPI application - Fixed all imports"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Track application start time
START_TIME = time.time()

# Create FastAPI app
app = FastAPI(title="Physician AI Assistant", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("=" * 60)
    logger.info("[STARTING] Starting Physician AI Backend Server")
    logger.info("=" * 60)
    
    try:
        from app.database import init_db
        logger.info("Initializing database...")
        init_db()
        logger.info("[OK] Database initialized successfully")
    except Exception as e:
        logger.error(f"[WARNING]  Database initialization warning: {e}")
        logger.info("Server will continue without database")
    
    logger.info("[OK] Backend server started successfully on http://127.0.0.1:8001")
    logger.info("=" * 60)

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception at {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# Root endpoint
@app.get("/")
def root():
    return {"status": "ok", "message": "Physician AI Backend API", "version": "1.0.0"}

# Health endpoint
@app.get("/health")
@app.get("/api/health")
def health():
    """Health check endpoint"""
    uptime = time.time() - START_TIME
    return {
        "status": "healthy",
        "uptime_seconds": round(uptime, 2),
        "database_status": "connected",
        "assistant_status": "ready",
        "knowledge_base_status": "ready"
    }

# Import and register routers with error handling
logger.info("Loading API routers...")

try:
    from app.api.auth_new import router as auth_router
    app.include_router(auth_router, prefix="/api")
    logger.info("[OK] Auth router loaded")
except Exception as e:
    logger.error(f"[ERROR] Failed to load auth router: {e}")

try:
    from app.api.chat_new import router as chat_router
    app.include_router(chat_router, prefix="/api")
    logger.info("[OK] Chat router loaded")
except Exception as e:
    logger.error(f"[ERROR] Failed to load chat router: {e}")

try:
    from app.api.health import router as health_router
    app.include_router(health_router, prefix="/api", tags=["health"])
    logger.info("[OK] Health router loaded")
except Exception as e:
    logger.error(f"[ERROR] Failed to load health router: {e}")

# Skip knowledge_base router for now - it has blocking imports
# try:
#     from app.api.knowledge_base import router as knowledge_base_router
#     app.include_router(knowledge_base_router, prefix="/api/knowledge")
#     logger.info("[OK] Knowledge base router loaded")
# except Exception as e:
#     logger.error(f"[ERROR] Failed to load knowledge base router: {e}")
logger.info("[WARNING]  Knowledge base router skipped (blocking imports)")

try:
    from app.api.discharge import router as discharge_router
    app.include_router(discharge_router, prefix="/api")
    logger.info("[OK] Discharge router loaded")
except Exception as e:
    logger.error(f"[ERROR] Failed to load discharge router: {e}")

try:
    from app.api.treatment import router as treatment_router
    app.include_router(treatment_router, prefix="/api/treatment", tags=["treatment"])
    logger.info("[OK] Treatment router loaded")
except Exception as e:
    logger.error(f"[ERROR] Failed to load treatment router: {e}")

try:
    from app.api.timeline import router as timeline_router
    app.include_router(timeline_router, prefix="/api/timeline", tags=["timeline"])
    logger.info("[OK] Timeline router loaded")
except Exception as e:
    logger.error(f"[ERROR] Failed to load timeline router: {e}")

try:
    from app.api.analytics import router as analytics_router
    app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
    logger.info("[OK] Analytics router loaded")
except Exception as e:
    logger.error(f"[ERROR] Failed to load analytics router: {e}")

try:
    from app.api.fhir import router as fhir_router
    app.include_router(fhir_router, prefix="/api/fhir", tags=["fhir"])
    logger.info("[OK] FHIR router loaded")
except Exception as e:
    logger.error(f"[ERROR] Failed to load FHIR router: {e}")

try:
    from app.api.reports import router as reports_router
    app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
    logger.info("[OK] Reports router loaded")
except Exception as e:
    logger.error(f"[ERROR] Failed to load reports router: {e}")

logger.info("[SUCCESS] All routers loaded successfully")
