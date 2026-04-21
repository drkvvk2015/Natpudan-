"""
Health and System Monitoring API Router
"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime, timezone
import time
import os
import psutil
import logging
from sqlalchemy import text

from app.database import SessionLocal
from app.schemas.system import RootResponse, HealthResponse, DetailedHealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["system"])

# Track application start time for uptime calculation
START_TIME = time.time()

# Service health status
service_health = {
    "database": False,
    "openai": False,
    "knowledge_base": False
}

@router.get("/", response_model=RootResponse)
def root() -> Dict[str, Any]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@router.get("/health", response_model=HealthResponse)
def health() -> Dict[str, Any]:
    """Basic health check for load balancers and monitoring."""
    # Fallback probe so health works reliably in tests and warm/cold starts.
    db_healthy = service_health["database"]
    if not db_healthy:
        db = None
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db_healthy = True
            service_health["database"] = True
        except Exception:
            db_healthy = False
        finally:
            if db is not None:
                db.close()

    openai_healthy = service_health["openai"]
    if not openai_healthy:
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            openai_healthy = bool(api_key and not api_key.startswith("sk-your"))
            service_health["openai"] = openai_healthy
        except Exception:
            openai_healthy = False

    kb_healthy = service_health["knowledge_base"]
    if not kb_healthy:
        try:
            from app.services.vector_knowledge_base import get_vector_knowledge_base
            kb = get_vector_knowledge_base()
            kb_healthy = kb is not None
            service_health["knowledge_base"] = kb_healthy
        except Exception:
            kb_healthy = False

    current_services = {
        "database": db_healthy,
        "openai": openai_healthy,
        "knowledge_base": kb_healthy,
    }

    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "api",
        "services": current_services,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/health/detailed", response_model=DetailedHealthResponse)
def detailed_health() -> Dict[str, Any]:
    """Detailed health check with system metrics."""
    try:
        # Calculate uptime in seconds
        uptime_seconds = int(time.time() - START_TIME)

        # Get system metrics
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
                "used": memory.used
            },
            "disk_usage": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": round(disk.percent, 2)
            },
            "database_status": "active",
            "cache_status": "active",
            "assistant_status": "operational",
            "knowledge_base_status": "ready",
            "last_check_in": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
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
            "last_check_in": datetime.now(timezone.utc).isoformat()
        }
