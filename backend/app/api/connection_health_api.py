"""
Connection Health API - Manual health checks and fixes

Provides endpoints for:
- Checking connection health
- Getting port configuration
- Manually triggering auto-fixes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from app.services.connection_health_monitor import get_connection_monitor

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthCheckResponse(BaseModel):
    healthy: bool
    timestamp: str
    checks: Dict[str, Any]
    issues: list
    fixes_available: list


class AutoFixResponse(BaseModel):
    fixes_attempted: int
    fixes_successful: int
    fixes_failed: int
    details: list


@router.get("/connection/health", response_model=HealthCheckResponse)
async def check_connection_health():
    """
    Check connection health and configuration
    
    Returns detailed status of:
    - Frontend .env files configuration
    - Port availability
    - CORS configuration
    """
    try:
        monitor = get_connection_monitor()
        health = monitor.check_health()
        return HealthCheckResponse(**health)
    except Exception as e:
        logger.error(f"Connection health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connection/auto-fix", response_model=AutoFixResponse)
async def trigger_auto_fix():
    """
    Manually trigger auto-fix for connection issues
    
    This will:
    1. Check for port mismatches in .env files
    2. Automatically fix them
    3. Return results
    
    Note: Frontend needs restart to pick up changes
    """
    try:
        monitor = get_connection_monitor()
        health = monitor.check_health()
        
        if health['healthy']:
            return AutoFixResponse(
                fixes_attempted=0,
                fixes_successful=0,
                fixes_failed=0,
                details=[{"message": "No issues detected, nothing to fix"}]
            )
        
        fix_result = monitor.auto_fix(health)
        return AutoFixResponse(**fix_result)
    
    except Exception as e:
        logger.error(f"Auto-fix failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connection/config")
async def get_connection_config():
    """Get current connection configuration"""
    try:
        monitor = get_connection_monitor()
        return {
            "config": monitor.config,
            "config_file": str(monitor.CONFIG_FILE),
            "frontend_dir": str(monitor.FRONTEND_DIR),
            "backend_dir": str(monitor.BACKEND_DIR)
        }
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connection/ports")
async def get_port_status():
    """Check if ports are available or in use"""
    try:
        monitor = get_connection_monitor()
        health = monitor.check_health()
        return health['checks'].get('ports', {})
    except Exception as e:
        logger.error(f"Port check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
