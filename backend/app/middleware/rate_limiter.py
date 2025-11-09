"""
Rate limiting middleware for API endpoints
"""
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class RateLimiter(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter for API endpoints.
    For production, consider using Redis-based rate limiting.
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Number of calls allowed
        self.period = period  # Time period in seconds
        self.clients: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health check and docs
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Get current time
        now = time.time()
        
        # Clean old entries
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if now - timestamp < self.period
        ]
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            logger.warning(f"Rate limit exceeded for {client_ip} on {request.url.path}")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds."
            )
        
        # Add current request timestamp
        self.clients[client_ip].append(now)
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.calls - len(self.clients[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(now + self.period))
        
        return response


class EndpointRateLimiter:
    """
    Decorator-based rate limiter for specific endpoints.
    Can be applied to individual routes for custom limits.
    """
    
    def __init__(self, calls: int = 10, period: int = 60):
        self.calls = calls
        self.period = period
        self.clients: Dict[str, list] = defaultdict(list)
    
    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs
            request = kwargs.get('request') or next(
                (arg for arg in args if isinstance(arg, Request)), None
            )
            
            if not request:
                return await func(*args, **kwargs)
            
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            
            # Clean old entries
            self.clients[client_ip] = [
                timestamp for timestamp in self.clients[client_ip]
                if now - timestamp < self.period
            ]
            
            # Check rate limit
            if len(self.clients[client_ip]) >= self.calls:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded for this endpoint. Try again in {self.period} seconds."
                )
            
            # Add current request
            self.clients[client_ip].append(now)
            
            return await func(*args, **kwargs)
        
        return wrapper
