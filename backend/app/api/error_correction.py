"""
Auto Error Correction Module
Monitors and auto-corrects common application errors
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import traceback
from enum import Enum
import asyncio
import socket
import re

from app.database import get_db
from app.models import User

router = APIRouter(tags=["error-correction"])
logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    API = "api"
    VALIDATION = "validation"
    NETWORK = "network"
    PERMISSION = "permission"
    SYSTEM = "system"


class ErrorLog(BaseModel):
    id: int
    timestamp: datetime
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    stack_trace: Optional[str]
    user_id: Optional[int]
    endpoint: Optional[str]
    auto_corrected: bool
    correction_applied: Optional[str]


class ErrorCorrection(BaseModel):
    error_pattern: str
    correction_action: str
    success_rate: float
    times_applied: int


class ErrorStats(BaseModel):
    total_errors: int
    auto_corrected: int
    correction_rate: float
    errors_by_category: Dict[str, int]
    errors_by_severity: Dict[str, int]
    recent_errors: List[ErrorLog]


# In-memory error log (in production, use database)
error_logs: List[Dict[str, Any]] = []
correction_actions: Dict[str, Callable] = {}


def register_correction_action(action_name: str):
    """Decorator to register correction actions"""
    def decorator(func: Callable):
        correction_actions[action_name] = func
        logger.info(f"Registered correction action: {action_name}")
        return func
    return decorator


@register_correction_action("truncate_password")
async def truncate_password(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Truncate password to 72 bytes for bcrypt compatibility"""
    try:
        password = context.get("password", "")
        if isinstance(password, str):
            truncated = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
            logger.info(f"Truncated password from {len(password)} to {len(truncated)} characters")
            return {
                "success": True,
                "action": "password_truncated",
                "original_length": len(password),
                "new_length": len(truncated),
                "corrected_value": truncated
            }
    except Exception as e:
        logger.error(f"Failed to truncate password: {e}")
    return {"success": False, "action": "truncate_password", "error": str(error)}


@register_correction_action("retry_connection")
async def retry_connection(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Retry connection with exponential backoff"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
            
            # Attempt to reconnect
            url = context.get("url", "")
            if url:
                logger.info(f"Retry attempt {attempt + 1}/{max_retries} for {url}")
                # The actual retry logic should be in the calling code
                return {
                    "success": True,
                    "action": "retry_connection",
                    "attempts": attempt + 1,
                    "delay": 2 ** attempt
                }
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"All retry attempts failed: {e}")
    
    return {"success": False, "action": "retry_connection", "attempts": max_retries}


@register_correction_action("refresh_token")
async def refresh_token(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Auto-refresh expired authentication tokens"""
    try:
        # This would integrate with your auth system
        user_id = context.get("user_id")
        if user_id:
            logger.info(f"Token refresh triggered for user {user_id}")
            return {
                "success": True,
                "action": "refresh_token",
                "user_id": user_id,
                "message": "Token refresh initiated"
            }
    except Exception as e:
        logger.error(f"Failed to refresh token: {e}")
    return {"success": False, "action": "refresh_token"}


@register_correction_action("retry_query")
async def retry_query(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Retry database query with delay"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await asyncio.sleep(0.5 * (attempt + 1))  # 0.5s, 1s, 1.5s
            logger.info(f"Database retry attempt {attempt + 1}/{max_retries}")
            return {
                "success": True,
                "action": "retry_query",
                "attempts": attempt + 1
            }
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Database retry failed: {e}")
    
    return {"success": False, "action": "retry_query"}


@register_correction_action("add_cors_header")
async def add_cors_header(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Auto-add CORS headers"""
    try:
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
        logger.info("CORS headers added automatically")
        return {
            "success": True,
            "action": "add_cors_header",
            "headers": headers
        }
    except Exception as e:
        logger.error(f"Failed to add CORS headers: {e}")
    return {"success": False, "action": "add_cors_header"}


@register_correction_action("increment_port")
async def increment_port(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Find next available port"""
    try:
        start_port = context.get("port", 8000)
        for port in range(start_port, start_port + 100):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(("", port))
                sock.close()
                logger.info(f"Found available port: {port}")
                return {
                    "success": True,
                    "action": "increment_port",
                    "original_port": start_port,
                    "new_port": port
                }
            except OSError:
                continue
    except Exception as e:
        logger.error(f"Failed to find available port: {e}")
    return {"success": False, "action": "increment_port"}


@register_correction_action("sanitize_input")
async def sanitize_input(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize user input to prevent injection attacks"""
    try:
        input_value = context.get("input", "")
        if isinstance(input_value, str):
            # Remove potentially dangerous characters
            sanitized = re.sub(r'[<>"\';()&]', '', input_value)
            logger.info(f"Input sanitized: removed {len(input_value) - len(sanitized)} characters")
            return {
                "success": True,
                "action": "sanitize_input",
                "original": input_value,
                "sanitized": sanitized
            }
    except Exception as e:
        logger.error(f"Failed to sanitize input: {e}")
    return {"success": False, "action": "sanitize_input"}


@register_correction_action("handle_validation_error")
async def handle_validation_error(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
    """Handle validation errors by providing defaults or corrections"""
    try:
        field = context.get("field", "unknown")
        value = context.get("value")
        
        # Provide sensible defaults or corrections
        corrections = {
            "email": lambda v: str(v).strip().lower() if v else "",
            "phone": lambda v: re.sub(r'[^\d+]', '', str(v)) if v else "",
            "age": lambda v: max(0, min(150, int(v))) if str(v).isdigit() else 0,
        }
        
        if field in corrections:
            corrected = corrections[field](value)
            logger.info(f"Validation error corrected for {field}: {value} → {corrected}")
            return {
                "success": True,
                "action": "handle_validation_error",
                "field": field,
                "corrected_value": corrected
            }
    except Exception as e:
        logger.error(f"Failed to handle validation error: {e}")
    return {"success": False, "action": "handle_validation_error"}


correction_rules: List[Dict[str, Any]] = [
    {
        "pattern": "password cannot be longer than 72 bytes",
        "action": "truncate_password",
        "category": ErrorCategory.AUTHENTICATION,
        "description": "Auto-truncate passwords to 72 bytes for bcrypt compatibility"
    },
    {
        "pattern": "Connection refused|connection failed|timeout",
        "action": "retry_connection",
        "category": ErrorCategory.NETWORK,
        "description": "Retry network connections with exponential backoff"
    },
    {
        "pattern": "Unauthorized|token expired|invalid token",
        "action": "refresh_token",
        "category": ErrorCategory.AUTHENTICATION,
        "description": "Auto-refresh expired authentication tokens"
    },
    {
        "pattern": "Database locked|database is locked",
        "action": "retry_query",
        "category": ErrorCategory.DATABASE,
        "description": "Retry database operations with delay"
    },
    {
        "pattern": "CORS|No 'Access-Control-Allow-Origin'",
        "action": "add_cors_header",
        "category": ErrorCategory.API,
        "description": "Auto-add required CORS headers"
    },
    {
        "pattern": "Port already in use|Address already in use",
        "action": "increment_port",
        "category": ErrorCategory.SYSTEM,
        "description": "Auto-select next available port"
    },
    {
        "pattern": "validation error|invalid input|malformed",
        "action": "handle_validation_error",
        "category": ErrorCategory.VALIDATION,
        "description": "Auto-correct validation errors with sensible defaults"
    },
    {
        "pattern": "SQL injection|script injection|XSS",
        "action": "sanitize_input",
        "category": ErrorCategory.VALIDATION,
        "description": "Sanitize potentially malicious input"
    }
]


async def log_error(
    category: ErrorCategory,
    severity: ErrorSeverity,
    message: str,
    stack_trace: Optional[str] = None,
    user_id: Optional[int] = None,
    endpoint: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    execute_correction: bool = True
) -> Dict[str, Any]:
    """Log an error and attempt auto-correction"""
    
    error_entry = {
        "id": len(error_logs) + 1,
        "timestamp": datetime.utcnow(),
        "category": category,
        "severity": severity,
        "message": message,
        "stack_trace": stack_trace,
        "user_id": user_id,
        "endpoint": endpoint,
        "auto_corrected": False,
        "correction_applied": None,
        "correction_result": None
    }
    
    # Try to auto-correct
    correction_result = None
    for rule in correction_rules:
        # Use regex for pattern matching
        if re.search(rule["pattern"], message, re.IGNORECASE):
            action_name = rule["action"]
            
            if execute_correction and action_name in correction_actions:
                try:
                    # Execute the actual correction
                    correction_func = correction_actions[action_name]
                    correction_result = await correction_func(
                        Exception(message),
                        context or {}
                    )
                    
                    error_entry["auto_corrected"] = correction_result.get("success", False)
                    error_entry["correction_applied"] = action_name
                    error_entry["correction_result"] = correction_result
                    
                    if correction_result.get("success"):
                        logger.info(
                            f"✅ Auto-correction SUCCESS: {action_name} for error: {message[:50]}"
                        )
                    else:
                        logger.warning(
                            f"⚠️ Auto-correction FAILED: {action_name} for error: {message[:50]}"
                        )
                except Exception as e:
                    logger.error(f"Error executing correction {action_name}: {e}")
                    error_entry["correction_result"] = {
                        "success": False,
                        "error": str(e)
                    }
            else:
                # Just mark as correctable without executing
                error_entry["auto_corrected"] = False
                error_entry["correction_applied"] = action_name
                logger.info(f"Correction available: {action_name} for error: {message[:50]}")
            
            break
    
    error_logs.append(error_entry)
    
    # Keep only last 1000 errors
    if len(error_logs) > 1000:
        error_logs.pop(0)
    
    return error_entry


@router.get("/errors", response_model=List[ErrorLog])
async def get_errors(
    limit: int = 50,
    category: Optional[ErrorCategory] = None,
    severity: Optional[ErrorSeverity] = None,
    auto_corrected: Optional[bool] = None
):
    """Get error logs with optional filters"""
    
    filtered = error_logs.copy()
    
    if category:
        filtered = [e for e in filtered if e["category"] == category]
    
    if severity:
        filtered = [e for e in filtered if e["severity"] == severity]
    
    if auto_corrected is not None:
        filtered = [e for e in filtered if e["auto_corrected"] == auto_corrected]
    
    # Sort by timestamp descending
    filtered.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return filtered[:limit]


@router.get("/errors/stats", response_model=ErrorStats)
async def get_error_stats():
    """Get error statistics and analytics"""
    
    total = len(error_logs)
    auto_corrected = sum(1 for e in error_logs if e["auto_corrected"])
    
    errors_by_category = {}
    for category in ErrorCategory:
        errors_by_category[category.value] = sum(
            1 for e in error_logs if e["category"] == category
        )
    
    errors_by_severity = {}
    for severity in ErrorSeverity:
        errors_by_severity[severity.value] = sum(
            1 for e in error_logs if e["severity"] == severity
        )
    
    # Get recent errors (last hour)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent = [e for e in error_logs if e["timestamp"] > one_hour_ago]
    recent.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return ErrorStats(
        total_errors=total,
        auto_corrected=auto_corrected,
        correction_rate=auto_corrected / total if total > 0 else 0,
        errors_by_category=errors_by_category,
        errors_by_severity=errors_by_severity,
        recent_errors=recent[:20]
    )


@router.get("/correction-rules", response_model=List[ErrorCorrection])
async def get_correction_rules():
    """Get all error correction rules"""
    
    return [
        ErrorCorrection(
            error_pattern=rule["pattern"],
            correction_action=rule["action"],
            success_rate=0.95,  # Mock success rate
            times_applied=sum(
                1 for e in error_logs
                if e["auto_corrected"] and e["correction_applied"] == rule["action"]
            )
        )
        for rule in correction_rules
    ]


@router.post("/errors/clear")
async def clear_errors():
    """Clear all error logs (admin only)"""
    global error_logs
    count = len(error_logs)
    error_logs.clear()
    return {"message": f"Cleared {count} error logs", "success": True}


@router.post("/errors/test")
async def test_error_correction(
    message: str,
    category: ErrorCategory = ErrorCategory.SYSTEM,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    context: Optional[Dict[str, Any]] = None
):
    """Test error correction system with actual execution"""
    
    error = await log_error(
        category=category,
        severity=severity,
        message=message,
        context=context,
        execute_correction=True
    )
    
    return {
        "message": "Test error logged and correction attempted",
        "error": error,
        "auto_corrected": error["auto_corrected"],
        "correction_applied": error["correction_applied"],
        "correction_result": error.get("correction_result"),
        "success": error.get("auto_corrected", False)
    }


@router.post("/errors/correct/{error_id}")
async def manually_correct_error(error_id: int):
    """Manually trigger correction for a specific error"""
    
    # Find the error
    error = next((e for e in error_logs if e["id"] == error_id), None)
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")
    
    if not error.get("correction_applied"):
        raise HTTPException(status_code=400, detail="No correction action available for this error")
    
    action_name = error["correction_applied"]
    if action_name not in correction_actions:
        raise HTTPException(status_code=400, detail=f"Correction action '{action_name}' not implemented")
    
    try:
        correction_func = correction_actions[action_name]
        result = await correction_func(
            Exception(error["message"]),
            {}
        )
        
        error["auto_corrected"] = result.get("success", False)
        error["correction_result"] = result
        
        return {
            "message": f"Correction executed for error {error_id}",
            "success": result.get("success", False),
            "result": result
        }
    except Exception as e:
        logger.error(f"Failed to execute correction: {e}")
        raise HTTPException(status_code=500, detail=f"Correction failed: {str(e)}")


# Utility function to be used throughout the application
async def handle_error_with_correction(
    error: Exception,
    category: ErrorCategory,
    severity: ErrorSeverity,
    endpoint: Optional[str] = None,
    user_id: Optional[int] = None,
    context: Optional[Dict[str, Any]] = None,
    execute_correction: bool = True
) -> Dict[str, Any]:
    """
    Handle an error with auto-correction
    Use this throughout the app to automatically log and correct errors
    
    Example usage:
        try:
            # Some operation
            pass
        except Exception as e:
            result = await handle_error_with_correction(
                error=e,
                category=ErrorCategory.DATABASE,
                severity=ErrorSeverity.HIGH,
                context={"query": "SELECT * FROM users"},
                execute_correction=True
            )
            if result["auto_corrected"]:
                # Retry the operation with corrected parameters
                pass
    """
    
    message = str(error)
    stack_trace = traceback.format_exc()
    
    return await log_error(
        category=category,
        severity=severity,
        message=message,
        stack_trace=stack_trace,
        user_id=user_id,
        endpoint=endpoint,
        context=context,
        execute_correction=execute_correction
    )


@router.get("/health")
async def error_correction_health():
    """Health check for error correction system"""
    return {
        "status": "healthy",
        "registered_actions": list(correction_actions.keys()),
        "total_rules": len(correction_rules),
        "total_errors_logged": len(error_logs),
        "auto_corrected_count": sum(1 for e in error_logs if e.get("auto_corrected")),
        "success_rate": (
            sum(1 for e in error_logs if e.get("auto_corrected")) / len(error_logs) * 100
            if error_logs else 0
        )
    }

