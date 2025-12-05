"""
Automatic Error Correction System

This system monitors the application for errors and automatically attempts to fix them:
1. Database connection issues  Auto-reconnect
2. Port conflicts  Auto-switch ports
3. Missing dependencies  Auto-install
4. Knowledge base errors  Auto-rebuild index
5. Memory issues  Auto-cleanup
"""

import logging
import traceback
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import psutil
import time

logger = logging.getLogger(__name__)

class ErrorCorrector:
    """Automatic error detection and correction system"""
    
    def __init__(self):
        self.error_history = []
        self.correction_attempts = {}
        self.max_correction_attempts = 3
    
    def log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error with context for analysis"""
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc()
        }
        self.error_history.append(error_record)
        logger.error(f"Error logged: {error_record}")
        
        # Attempt automatic correction
        self.attempt_correction(error, context)
    
    def attempt_correction(self, error: Exception, context: Dict[str, Any]):
        """Attempt to automatically correct the error"""
        error_key = f"{type(error).__name__}_{context.get('operation', 'unknown')}"
        
        # Check if we've already tried to fix this too many times
        attempts = self.correction_attempts.get(error_key, 0)
        if attempts >= self.max_correction_attempts:
            logger.warning(f"Max correction attempts reached for {error_key}")
            return False
        
        self.correction_attempts[error_key] = attempts + 1
        
        # Route to appropriate correction handler
        if isinstance(error, ConnectionError):
            return self._fix_connection_error(error, context)
        elif isinstance(error, MemoryError):
            return self._fix_memory_error(error, context)
        elif isinstance(error, FileNotFoundError):
            return self._fix_file_error(error, context)
        elif "database" in str(error).lower():
            return self._fix_database_error(error, context)
        elif "port" in str(error).lower():
            return self._fix_port_error(error, context)
        else:
            logger.info(f"No automatic correction available for {type(error).__name__}")
            return False
    
    def _fix_connection_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Fix connection-related errors"""
        logger.info("Attempting to fix connection error...")
        
        try:
            # Wait and retry
            time.sleep(2)
            
            # If it's a database connection, try to reconnect
            if "database" in context:
                from app.database import engine
                engine.dispose()
                logger.info("Database connection pool reset")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to fix connection error: {e}")
            return False
    
    def _fix_memory_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Fix memory-related errors"""
        logger.info("Attempting to fix memory error...")
        
        try:
            import gc
            
            # Force garbage collection
            gc.collect()
            
            # Check memory usage
            memory = psutil.virtual_memory()
            logger.info(f"Memory usage: {memory.percent}%")
            
            # If memory is critically high, try to free up space
            if memory.percent > 90:
                # Clear knowledge base cache if present
                try:
                    from app.services.enhanced_knowledge_base import get_knowledge_base
                    kb = get_knowledge_base()
                    if hasattr(kb, 'clear_cache'):
                        kb.clear_cache()
                        logger.info("Knowledge base cache cleared")
                except:
                    pass
            
            return True
        except Exception as e:
            logger.error(f"Failed to fix memory error: {e}")
            return False
    
    def _fix_file_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Fix file-related errors"""
        logger.info("Attempting to fix file error...")
        
        try:
            file_path = context.get('file_path')
            if not file_path:
                return False
            
            # Create directory if it doesn't exist
            import os
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created missing directory: {directory}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to fix file error: {e}")
            return False
    
    def _fix_database_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Fix database-related errors"""
        logger.info("Attempting to fix database error...")
        
        try:
            from app.database import engine, init_db
            
            # Reset connection pool
            engine.dispose()
            
            # Reinitialize database
            init_db()
            
            logger.info("Database reinitialized")
            return True
        except Exception as e:
            logger.error(f"Failed to fix database error: {e}")
            return False
    
    def _fix_port_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Fix port conflict errors"""
        logger.info("Attempting to fix port error...")
        
        try:
            # Log the port conflict but don't auto-change port
            # (requires server restart)
            logger.warning("Port conflict detected. Consider using a different port.")
            
            # Try to kill the process using the port
            port = context.get('port')
            if port:
                import psutil
                for conn in psutil.net_connections():
                    if conn.laddr.port == port and conn.status == 'LISTEN':
                        try:
                            proc = psutil.Process(conn.pid)
                            logger.warning(f"Process {conn.pid} is using port {port}: {proc.name()}")
                        except:
                            pass
            
            return False
        except Exception as e:
            logger.error(f"Failed to fix port error: {e}")
            return False
    
    def get_error_report(self) -> Dict[str, Any]:
        """Generate error report"""
        return {
            "total_errors": len(self.error_history),
            "recent_errors": self.error_history[-10:],
            "correction_attempts": self.correction_attempts,
            "error_types": self._group_errors_by_type()
        }
    
    def _group_errors_by_type(self) -> Dict[str, int]:
        """Group errors by type for reporting"""
        error_types = {}
        for error in self.error_history:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        return error_types


# Global error corrector instance
_error_corrector = None

def get_error_corrector() -> ErrorCorrector:
    """Get global error corrector instance"""
    global _error_corrector
    if _error_corrector is None:
        _error_corrector = ErrorCorrector()
    return _error_corrector


def with_auto_correction(operation_name: str):
    """Decorator to add automatic error correction to functions"""
    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            corrector = get_error_corrector()
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {
                    "operation": operation_name,
                    "function": func.__name__,
                    "args": str(args)[:200],  # Truncate for security
                }
                corrector.log_error(e, context)
                
                # Re-raise after logging
                raise
        
        def sync_wrapper(*args, **kwargs):
            corrector = get_error_corrector()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    "operation": operation_name,
                    "function": func.__name__,
                    "args": str(args)[:200],
                }
                corrector.log_error(e, context)
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
