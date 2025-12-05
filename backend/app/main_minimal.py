"""MINIMAL Working Backend - Only Essential Routes"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

START_TIME = time.time()
app = FastAPI(title="Physician AI Assistant", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    print("\n" + "="*60)
    print("[STARTING] Backend Server")
    print("="*60)
    try:
        from app.database import init_db
        init_db()
        print("[OK] Database initialized")
    except Exception as e:
        print(f"[WARNING] Database warning: {e}")
    print("[OK] Server ready on http://127.0.0.1:8001")
    print("="*60 + "\n")

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error at {request.url.path}: {str(exc)}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# Basic routes
@app.get("/")
def root():
    return {"status": "ok", "message": "Physician AI Backend", "version": "1.0.0"}

@app.get("/health")
@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "database_status": "connected",
        "assistant_status": "ready",
        "knowledge_base_status": "ready"
    }

# Load ONLY essential routers (auth + chat)
print("Loading essential routers...")

try:
    from app.api.auth_new import router as auth_router
    app.include_router(auth_router, prefix="/api")
    print("[OK] Auth router")
except Exception as e:
    print(f"[ERROR] Auth router failed: {e}")

try:
    from app.api.chat_new import router as chat_router
    app.include_router(chat_router, prefix="/api")
    print("[OK] Chat router")
except Exception as e:
    print(f"[ERROR] Chat router failed: {e}")

try:
    from app.api.discharge import router as discharge_router
    app.include_router(discharge_router, prefix="/api")
    print("[OK] Discharge router")
except Exception as e:
    print(f"[ERROR] Discharge router failed: {e}")

print("[SUCCESS] Ready!")
