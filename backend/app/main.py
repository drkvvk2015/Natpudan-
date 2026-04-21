"""FastAPI application entrypoint.

This module prioritizes test compatibility and stable API behavior while the
service layer continues to evolve. Endpoints here should remain deterministic,
well-validated, and operational across local and CI environments.
"""

from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException, Request, status
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response as StarletteResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
import os
import psutil
import logging
import tempfile

from app.core.config import settings
from app.logging_config import setup_logging, get_logger
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.rate_limiter import RateLimiter
from app.monitoring import record_http_metrics, render_prometheus_metrics
from app.telemetry import instrument_fastapi_app
from app.schemas.system import RootResponse, HealthResponse, DetailedHealthResponse
from app.container import register_api_routers
from app.lifespan import app_lifespan

setup_logging(getattr(logging, settings.LOG_LEVEL, logging.INFO))
logger = get_logger(__name__)

# Import error correction system
from app.services.error_corrector import get_error_corrector

error_corrector = get_error_corrector()

from app.database import SessionLocal
from sqlalchemy import text

# Track application start time for uptime calculation
START_TIME = time.time()

app = FastAPI(
    title="Physician AI Assistant",
    version="1.0.0",
    lifespan=app_lifespan
)
instrument_fastapi_app(app)

app.add_middleware(RequestContextMiddleware)

if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimiter,
        calls=settings.RATE_LIMIT_CALLS,
        period=settings.RATE_LIMIT_PERIOD,
    )

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and provide graceful error responses"""
    error_id = f"error_{int(time.time())}"
    logger.error(
        f"[{error_id}] Unhandled exception at {request.method} {request.url.path}:",
        exc_info=True
    )

    # Log to error corrector
    error_corrector.log_error(exc, {
        "operation": "api_request",
        "method": request.method,
        "path": str(request.url.path),
        "error_id": error_id
    })

    # Determine user-friendly error message
    error_msg = "An unexpected error occurred. Please try again."
    status_code = 500

    if "openai" in str(exc).lower():
        error_msg = "AI service temporarily unavailable. Please try again or use knowledge base search."
    elif "database" in str(exc).lower():
        error_msg = "Database connection issue. Please try again in a moment."
    elif "timeout" in str(exc).lower():
        error_msg = "Request timeout. Please try again with a simpler query."
        status_code = 504

    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_msg,
            "error_id": error_id,
            "detail": str(exc)[:200] if logger.level == logging.DEBUG else None
        }
    )


@app.post("/api/error-correction/log")
async def log_frontend_error(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Accept frontend error reports without failing the client."""
    error_corrector.log_error(
        Exception(payload.get("message", "Frontend error")),
        {
            "operation": "frontend_error",
            "url": payload.get("url"),
            "component_stack": payload.get("componentStack"),
            "timestamp": payload.get("timestamp"),
        },
    )
    return {"success": True}

# CORS middleware - allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


def _check_database_health() -> bool:
    db = None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
    finally:
        if db is not None:
            db.close()


def _check_openai_health() -> bool:
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        return bool(api_key and not api_key.startswith("sk-your"))
    except Exception:
        return False


def _check_knowledge_base_health() -> bool:
    try:
        from app.services.vector_knowledge_base import get_vector_knowledge_base

        kb = get_vector_knowledge_base()
        return kb is not None
    except Exception:
        return False


@app.get("/", response_model=RootResponse)
def root() -> Dict[str, Any]:
    """Root contract used by tests, uptime checks, and lightweight clients."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/health", response_model=HealthResponse)
def health() -> Dict[str, Any]:
    """Basic health contract for load balancers and smoke tests."""
    services = {
        "database": _check_database_health(),
        "openai": _check_openai_health(),
        "knowledge_base": _check_knowledge_base_health(),
    }
    return {
        "status": "healthy" if services["database"] else "degraded",
        "service": "api",
        "services": services,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/detailed", response_model=DetailedHealthResponse)
def detailed_health() -> Dict[str, Any]:
    """Detailed health contract for diagnostics and operational checks."""
    try:
        uptime_seconds = int(time.time() - START_TIME)
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(os.path.abspath(os.sep))

        return {
            "status": "healthy",
            "uptime": uptime_seconds,
            "cpu_usage": round(cpu_percent, 2),
            "memory_usage": {
                "total": memory.total,
                "available": memory.available,
                "percent": round(memory.percent, 2),
                "used": memory.used,
            },
            "disk_usage": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": round(disk.percent, 2),
            },
            "database_status": "active" if _check_database_health() else "degraded",
            "cache_status": "active",
            "assistant_status": "operational",
            "knowledge_base_status": "ready" if _check_knowledge_base_health() else "degraded",
            "last_check_in": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        logger.error("Detailed health check failed: %s", exc)
        return {
            "status": "error",
            "uptime": 0,
            "cpu_usage": 0,
            "memory_usage": {"total": 0, "available": 0, "percent": 0, "used": 0},
            "disk_usage": {"total": 0, "used": 0, "free": 0, "percent": 0},
            "database_status": "unknown",
            "cache_status": "unknown",
            "assistant_status": "unknown",
            "knowledge_base_status": "unknown",
            "last_check_in": datetime.now(timezone.utc).isoformat(),
        }

@app.middleware("http")
async def log_requests(request: Request, call_next: RequestResponseEndpoint) -> StarletteResponse:
    started_at = time.perf_counter()
    response: StarletteResponse = await call_next(request)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    record_http_metrics(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        started_at=started_at,
    )
    logger.info(
        "request_completed method=%s path=%s status=%s duration_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response

@app.get("/metrics")
def metrics() -> StarletteResponse:
    """Prometheus metrics endpoint."""
    payload = render_prometheus_metrics()
    if payload is None:
        raise HTTPException(status_code=503, detail="Metrics backend unavailable")
    return StarletteResponse(content=payload, media_type="text/plain; version=0.0.4")


# Main API Router
api_router = APIRouter(prefix="/api")

# Register all modular routers from container
register_api_routers(api_router)

# Compatibility redirect for legacy v1 path
@app.api_route("/api/v1/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def api_v1_compat(full_path: str, request: Request):
    """Compatibility layer: route legacy /api/v1/* requests to /api/* endpoints."""
    target = f"/api/{full_path}"
    if request.url.query:
        target = f"{target}?{request.url.query}"
    return RedirectResponse(url=target, status_code=307)

# Include the main API router in the app
app.include_router(api_router)

# Trigger queue processing endpoint (legacy support)
@app.post("/api/queue/process")
def trigger_queue_processing() -> Dict[str, Any]:
    """
    Trigger PDF upload queue processing
    Can be called by an external scheduler
    """
    try:
        from app.services.upload_queue_processor import process_upload_queue
        result: Dict[str, Any] = process_upload_queue()
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"[QUEUE] Error triggering processing: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
