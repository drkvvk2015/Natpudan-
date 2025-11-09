"""
Global error handling middleware
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback
from typing import Optional

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler that catches all exceptions and returns
    consistent error responses.
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await self.handle_exception(request, exc)
    
    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle different types of exceptions with appropriate responses"""
        
        # Log the error
        logger.error(
            f"Error processing request {request.method} {request.url.path}",
            exc_info=True
        )
        
        # Determine status code and message
        if isinstance(exc, ValueError):
            status_code = status.HTTP_400_BAD_REQUEST
            detail = str(exc)
        elif isinstance(exc, PermissionError):
            status_code = status.HTTP_403_FORBIDDEN
            detail = "Permission denied"
        elif isinstance(exc, FileNotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
            detail = "Resource not found"
        elif isinstance(exc, TimeoutError):
            status_code = status.HTTP_504_GATEWAY_TIMEOUT
            detail = "Request timeout"
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            detail = "Internal server error"
        
        # Build error response
        error_response = {
            "error": {
                "message": detail,
                "type": exc.__class__.__name__,
                "path": str(request.url.path),
                "method": request.method
            }
        }
        
        # Add traceback in debug mode
        if request.app.debug:
            error_response["error"]["traceback"] = traceback.format_exc()
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )


def create_error_response(
    message: str,
    error_type: str = "Error",
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[dict] = None
) -> JSONResponse:
    """
    Create a standardized error response
    
    Args:
        message: Error message to display
        error_type: Type of error (e.g., "ValidationError", "DatabaseError")
        status_code: HTTP status code
        details: Additional error details
    
    Returns:
        JSONResponse with error information
    """
    content = {
        "error": {
            "message": message,
            "type": error_type
        }
    }
    
    if details:
        content["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )
