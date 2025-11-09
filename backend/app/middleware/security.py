"""
Security middleware for production deployment
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate and sanitize incoming requests
    """
    
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    
    async def dispatch(self, request: Request, call_next):
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_CONTENT_LENGTH:
            logger.warning(f"Request too large: {content_length} bytes from {request.client.host}")
            return Response(
                content="Request entity too large",
                status_code=413
            )
        
        # Log suspicious patterns
        path = str(request.url.path).lower()
        suspicious_patterns = [
            "../", "..\\",  # Path traversal
            "<script", "</script>",  # XSS
            "union select", "drop table",  # SQL injection
            "eval(", "exec(",  # Code injection
        ]
        
        for pattern in suspicious_patterns:
            if pattern in path:
                logger.warning(f"Suspicious pattern detected in path: {path} from {request.client.host}")
                return Response(
                    content="Invalid request",
                    status_code=400
                )
        
        response = await call_next(request)
        return response
