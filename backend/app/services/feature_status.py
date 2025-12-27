"""
Feature status service: provides a unified readiness report for major app features
including database, Redis/Celery, OpenAI, and the vector knowledge base.

This module is lightweight and resilient: all checks are optional and will
degrade gracefully if a dependency is not installed or not configured.
"""

from __future__ import annotations

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    import redis  # type: ignore
    REDIS_AVAILABLE = True
except Exception:
    REDIS_AVAILABLE = False


def _check_database() -> Dict[str, Any]:
    """Basic database readiness using SQLAlchemy engine disposal pattern."""
    try:
        from app.database import engine
        # Attempt a trivial connection by getting a connection and immediately closing it
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        logger.warning(f"Database check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


def _check_openai() -> Dict[str, Any]:
    """Check if OpenAI is configured via environment variable."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return {"status": "not_configured", "message": "OPENAI_API_KEY missing"}
    if api_key.startswith("sk-your"):
        return {"status": "placeholder", "message": "Replace placeholder API key"}
    if not api_key.startswith("sk-"):
        return {"status": "invalid", "message": "API key format invalid"}
    return {"status": "configured"}


def _check_redis(url: str | None) -> Dict[str, Any]:
    """Ping Redis if library available and URL configured."""
    if not REDIS_AVAILABLE:
        return {"status": "unknown", "message": "redis-py not installed"}
    if not url:
        return {"status": "not_configured"}
    try:
        client = redis.from_url(url)
        pong = client.ping()
        return {"status": "healthy" if pong else "degraded"}
    except Exception as e:
        logger.warning(f"Redis check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


def _check_vector_kb() -> Dict[str, Any]:
    """Check vector knowledge base presence and document count."""
    try:
        from app.services.vector_knowledge_base import VectorKnowledgeBase
        from app.core.config import settings
        storage_dir = str(settings.KNOWLEDGE_BASE_DIR)
        kb = VectorKnowledgeBase(storage_dir=storage_dir)
        index_exists = (kb.storage_dir / "faiss_index.bin").exists()
        return {
            "status": "healthy" if kb.document_count > 0 else ("initialized" if index_exists else "empty"),
            "document_count": kb.document_count,
            "index_exists": index_exists,
        }
    except Exception as e:
        logger.warning(f"Vector KB check failed: {e}")
        return {"status": "degraded", "error": str(e)}


def get_feature_status() -> Dict[str, Any]:
    """Aggregate readiness for major features used by the app."""
    try:
        from app.core.config import settings
        redis_url = os.getenv("REDIS_URL") or os.getenv("CELERY_BROKER_URL") or "redis://localhost:6379/0"

        status = {
            "database": _check_database(),
            "openai": _check_openai(),
            "redis": _check_redis(redis_url),
            "vector_knowledge_base": _check_vector_kb(),
            "environment": {
                "ENVIRONMENT": settings.ENVIRONMENT,
                "DEBUG": settings.DEBUG,
            }
        }

        # Derive overall status
        svc_states = [svc.get("status") for svc in [
            status["database"], status["openai"], status["redis"], status["vector_knowledge_base"]
        ]]

        if all(s in ("healthy", "configured", "initialized") for s in svc_states):
            status["overall_status"] = "healthy"
        elif any(s == "unhealthy" for s in svc_states):
            status["overall_status"] = "unhealthy"
        else:
            status["overall_status"] = "degraded"

        return status
    except Exception as e:
        logger.error(f"Feature status aggregation error: {e}")
        return {"overall_status": "error", "error": str(e)}
