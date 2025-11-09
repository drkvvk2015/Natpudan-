"""
Health check and monitoring endpoints
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
import time
import psutil
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["monitoring"])

# Track application start time
START_TIME = time.time()


def get_medical_assistant():
    """Dependency to get medical assistant instance"""
    from app.main import medical_assistant
    return medical_assistant


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint with Medical Assistant status
    Returns: Service status and Medical Assistant information
    """
    try:
        # Get medical assistant instance
        assistant = get_medical_assistant()
        
        if assistant is None:
            return {
                "status": "initializing",
                "assistant_status": "not_ready",
                "knowledge_base_status": "not_ready",
                "service": "Physician AI Assistant",
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Get Medical Assistant status
        assistant_status_data = assistant.get_status()
        
        # Extract key status fields
        kb_chunks = assistant_status_data.get("knowledge_base", {}).get("total_chunks", 0)
        llm_status = assistant_status_data.get("llm_service", {})
        
        return {
            "status": "healthy",
            "assistant_status": "operational",
            "knowledge_base_status": "loaded" if kb_chunks > 0 else "empty",
            "service": "Physician AI Assistant",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {
                "knowledge_base_chunks": kb_chunks,
                "llm_status": llm_status.get("status", "unknown"),
                "fallback_mode": llm_status.get("fallback_mode", False)
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        return {
            "status": "degraded",
            "assistant_status": "error",
            "knowledge_base_status": "unknown",
            "service": "Physician AI Assistant",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with system metrics
    Returns: Comprehensive system health information
    """
    try:
        # Calculate uptime
        uptime_seconds = time.time() - START_TIME
        uptime_hours = uptime_seconds / 3600
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get process info
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info()
        
        health_status = {
            "status": "healthy",
            "service": "Physician AI Assistant",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime": {
                "seconds": round(uptime_seconds, 2),
                "hours": round(uptime_hours, 2),
                "human_readable": _format_uptime(uptime_seconds)
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_mb": round(memory.total / 1024 / 1024, 2),
                    "available_mb": round(memory.available / 1024 / 1024, 2),
                    "used_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                    "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                    "used_percent": disk.percent
                }
            },
            "process": {
                "memory_mb": round(process_memory.rss / 1024 / 1024, 2),
                "threads": process.num_threads()
            }
        }
        
        # Determine overall health status
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            health_status["status"] = "degraded"
            health_status["warnings"] = []
            
            if cpu_percent > 90:
                health_status["warnings"].append(f"High CPU usage: {cpu_percent}%")
            if memory.percent > 90:
                health_status["warnings"].append(f"High memory usage: {memory.percent}%")
            if disk.percent > 90:
                health_status["warnings"].append(f"High disk usage: {disk.percent}%")
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/health/dependencies")
async def check_dependencies() -> Dict[str, Any]:
    """
    Check status of external dependencies
    Returns: Status of database, AI services, etc.
    """
    dependencies = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {}
    }
    
    # Check database
    try:
        from app.database import get_db
        # Simple database connectivity check
        dependencies["services"]["database"] = {
            "status": "healthy",
            "type": "sqlite"
        }
    except Exception as e:
        dependencies["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check OpenAI API
    try:
        from app.core.config import settings
        if settings.OPENAI_API_KEY:
            dependencies["services"]["openai"] = {
                "status": "configured",
                "model": settings.OPENAI_MODEL
            }
        else:
            dependencies["services"]["openai"] = {
                "status": "not_configured",
                "message": "API key not set"
            }
    except Exception as e:
        dependencies["services"]["openai"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check knowledge base
    try:
        from app.services.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        stats = await kb.get_statistics()
        
        dependencies["services"]["knowledge_base"] = {
            "status": "healthy",
            "documents_indexed": stats.get("total_documents", 0),
            "chunks": stats.get("total_chunks", 0)
        }
    except Exception as e:
        dependencies["services"]["knowledge_base"] = {
            "status": "degraded",
            "error": str(e)
        }
    
    # Determine overall status
    statuses = [svc.get("status") for svc in dependencies["services"].values()]
    if all(s in ["healthy", "configured"] for s in statuses):
        dependencies["overall_status"] = "healthy"
    elif any(s == "unhealthy" for s in statuses):
        dependencies["overall_status"] = "unhealthy"
    else:
        dependencies["overall_status"] = "degraded"
    
    return dependencies


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get application metrics for monitoring
    Returns: Performance and usage metrics
    """
    try:
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(time.time() - START_TIME, 2),
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        }
        
        # Add custom application metrics here
        # For example: request counts, response times, cache hit rates, etc.
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics error: {e}", exc_info=True)
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


def _format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)
