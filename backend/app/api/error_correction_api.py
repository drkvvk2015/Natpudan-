"""
API endpoints for Error Correction System
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from app.services.error_corrector import get_error_corrector
from app.services.code_analyzer import get_code_analyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/error-correction", tags=["Error Correction"])


class ErrorLogRequest(BaseModel):
    """Request model for logging errors"""
    error: Optional[str] = None
    stack: Optional[str] = None
    componentStack: Optional[str] = None
    errorInfo: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/log")
async def log_error(error_data: ErrorLogRequest) -> Dict[str, Any]:
    """Log an error from the frontend for auto-correction analysis"""
    try:
        error_corrector = get_error_corrector()
        
        # Extract error information
        error_message = error_data.error or "Unknown error"
        stack_trace = error_data.stack or ""
        
        # Log the error for analysis
        logger.error(f"[FRONTEND ERROR] {error_message}")
        if stack_trace:
            logger.error(f"[STACK TRACE] {stack_trace}")
        
        # Store error in error corrector for pattern analysis
        # This will be used by the self-healing system
        error_corrector.record_error(
            error_type="frontend_error",
            error_message=error_message,
            stack_trace=stack_trace,
            metadata={
                "componentStack": error_data.componentStack,
                "errorInfo": error_data.errorInfo,
                **(error_data.metadata or {})
            }
        )
        
        return {
            "status": "logged",
            "message": "Error logged successfully for analysis",
            "error_id": error_corrector.get_last_error_id()
        }
        
    except Exception as e:
        logger.error(f"[ERROR LOGGING FAILED] {str(e)}")
        # Don't fail if error logging fails - this is a monitoring feature
        return {
            "status": "failed",
            "message": f"Failed to log error: {str(e)}"
        }


@router.get("/recent")
async def get_recent_errors(limit: int = 10) -> Dict[str, Any]:
    """Get recent logged errors"""
    try:
        error_corrector = get_error_corrector()
        recent_errors = error_corrector.get_recent_errors(limit)
        
        return {
            "errors": recent_errors,
            "total": len(recent_errors)
        }
        
    except Exception as e:
        logger.error(f"[GET RECENT ERRORS FAILED] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/code-issues")
async def detect_code_issues() -> Dict[str, Any]:
    """Detect code-level issues in the system."""
    try:
        analyzer = get_code_analyzer()
        
        # Check common model issues
        issues = []
        
        # Test PatientIntake model
        try:
            from app.models import PatientIntake
            schema = analyzer.check_model_schema(PatientIntake)
            
            # Check for expected fields
            expected_fields = ['id', 'name', 'age', 'gender', 'blood_type', 'height_cm', 'weight_kg']
            missing = [f for f in expected_fields if f not in schema]
            
            if missing:
                issues.append({
                    'model': 'PatientIntake',
                    'type': 'missing_fields',
                    'missing_fields': missing,
                    'available_fields': list(schema.keys())
                })
        except Exception as e:
            logger.warning(f"Failed to check PatientIntake: {e}")
        
        return {
            "status": "ok",
            "issues": issues,
            "message": "No critical code issues detected" if not issues else f"Found {len(issues)} potential issues"
        }
    
    except Exception as e:
        logger.error(f"[CODE ANALYSIS FAILED] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/{model_name}")
async def get_model_schema(model_name: str) -> Dict[str, Any]:
    """Get schema (columns) for a specific model."""
    try:
        analyzer = get_code_analyzer()
        
        # Map model names
        model_map = {
            'patient_intake': 'app.models:PatientIntake',
            'user': 'app.models:User',
            'conversation': 'app.models:Conversation',
        }
        
        if model_name.lower() not in model_map:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
        # Import model dynamically
        module_path, class_name = model_map[model_name.lower()].split(':')
        module = __import__(module_path, fromlist=[class_name])
        model_class = getattr(module, class_name)
        
        schema = analyzer.check_model_schema(model_class)
        
        return {
            "model": model_name,
            "schema": schema,
            "field_count": len(schema)
        }
    
    except Exception as e:
        logger.error(f"[SCHEMA LOOKUP FAILED] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
