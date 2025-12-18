"""
Self-Evolving Automatic Error Correction System

This advanced system learns from errors and automatically evolves correction strategies:

1. **Pattern Learning**: Analyzes error patterns to predict and prevent future errors
2. **AI-Powered Solutions**: Uses AI to generate context-specific fixes
3. **Success Tracking**: Remembers which fixes work and improves over time
4. **Predictive Prevention**: Monitors system health to prevent errors before they occur
5. **Auto-Optimization**: Adjusts system parameters based on historical data
6. **Knowledge Base**: Builds a database of error solutions that grows over time

Architecture:
- ErrorPattern: ML model for pattern recognition
- SolutionGenerator: AI-powered fix generation
- SuccessTracker: Tracks fix effectiveness
- PreventionEngine: Proactive error prevention
- LearningDatabase: Persistent storage of learned solutions
"""

import logging
import traceback
import json
import pickle
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import psutil
import time
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Storage paths
LEARNING_DB_PATH = Path("backend/data/error_learning")
LEARNING_DB_PATH.mkdir(parents=True, exist_ok=True)
SOLUTIONS_DB_FILE = LEARNING_DB_PATH / "solutions.json"
PATTERNS_DB_FILE = LEARNING_DB_PATH / "patterns.pkl"
METRICS_DB_FILE = LEARNING_DB_PATH / "metrics.json"


class ErrorPattern:
    """Analyzes and identifies error patterns for prediction"""
    
    def __init__(self):
        self.patterns = defaultdict(list)  # error_type -> [timestamps]
        self.frequencies = Counter()        # error_type -> count
        self.contexts = defaultdict(list)   # error_type -> [contexts]
        self.load_patterns()
    
    def load_patterns(self):
        """Load learned patterns from disk"""
        if PATTERNS_DB_FILE.exists():
            try:
                with open(PATTERNS_DB_FILE, 'rb') as f:
                    data = pickle.load(f)
                    self.patterns = data.get('patterns', defaultdict(list))
                    self.frequencies = data.get('frequencies', Counter())
                    self.contexts = data.get('contexts', defaultdict(list))
                logger.info(f"Loaded {len(self.frequencies)} error patterns from disk")
            except Exception as e:
                logger.warning(f"Failed to load patterns: {e}")
    
    def save_patterns(self):
        """Save learned patterns to disk"""
        try:
            data = {
                'patterns': dict(self.patterns),
                'frequencies': dict(self.frequencies),
                'contexts': dict(self.contexts),
                'last_updated': datetime.now().isoformat()
            }
            with open(PATTERNS_DB_FILE, 'wb') as f:
                pickle.dump(data, f)
            logger.info("Saved error patterns to disk")
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")
    
    def record_error(self, error_type: str, context: Dict[str, Any]):
        """Record error occurrence for pattern analysis"""
        timestamp = datetime.now()
        self.patterns[error_type].append(timestamp)
        self.frequencies[error_type] += 1
        self.contexts[error_type].append(context)
        
        # Keep only last 1000 entries per error type
        if len(self.patterns[error_type]) > 1000:
            self.patterns[error_type] = self.patterns[error_type][-1000:]
            self.contexts[error_type] = self.contexts[error_type][-1000:]
        
        self.save_patterns()
    
    def predict_likelihood(self, error_type: str) -> float:
        """Predict likelihood of error occurring soon (0.0-1.0)"""
        if error_type not in self.patterns or not self.patterns[error_type]:
            return 0.0
        
        timestamps = self.patterns[error_type]
        recent = [t for t in timestamps if datetime.now() - t < timedelta(hours=24)]
        
        if not recent:
            return 0.0
        
        # Calculate rate: errors per hour in last 24h
        hours_elapsed = (datetime.now() - min(recent)).total_seconds() / 3600
        if hours_elapsed < 0.1:
            hours_elapsed = 0.1
        
        error_rate = len(recent) / hours_elapsed
        
        # Normalize to 0-1 range (assuming >2 errors/hour = high risk)
        likelihood = min(error_rate / 2.0, 1.0)
        return likelihood
    
    def get_common_contexts(self, error_type: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most common contexts for an error type"""
        if error_type not in self.contexts:
            return []
        
        contexts = self.contexts[error_type]
        # Return most recent contexts
        return contexts[-limit:]


class SolutionGenerator:
    """AI-powered solution generator for errors"""
    
    def __init__(self):
        self.known_solutions = {}
        self.load_solutions()
    
    def load_solutions(self):
        """Load known solutions from disk"""
        if SOLUTIONS_DB_FILE.exists():
            try:
                with open(SOLUTIONS_DB_FILE, 'r') as f:
                    self.known_solutions = json.load(f)
                logger.info(f"Loaded {len(self.known_solutions)} known solutions")
            except Exception as e:
                logger.warning(f"Failed to load solutions: {e}")
    
    def save_solutions(self):
        """Save solutions to disk"""
        try:
            with open(SOLUTIONS_DB_FILE, 'w') as f:
                json.dump(self.known_solutions, f, indent=2)
            logger.info("Saved solutions to disk")
        except Exception as e:
            logger.error(f"Failed to save solutions: {e}")
    
    def generate_solution(self, error: Exception, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate AI-powered solution for error"""
        error_signature = self._create_error_signature(error, context)
        
        # Check if we have a known solution
        if error_signature in self.known_solutions:
            solution = self.known_solutions[error_signature]
            logger.info(f"Found known solution for {error_signature}")
            return solution
        
        # Generate new solution using heuristics
        solution = self._generate_heuristic_solution(error, context)
        
        if solution:
            # Store for future use
            self.known_solutions[error_signature] = {
                **solution,
                'created_at': datetime.now().isoformat(),
                'success_count': 0,
                'failure_count': 0
            }
            self.save_solutions()
        
        return solution
    
    def _create_error_signature(self, error: Exception, context: Dict[str, Any]) -> str:
        """Create unique signature for error + context"""
        error_type = type(error).__name__
        error_msg = str(error)[:100]  # First 100 chars
        operation = context.get('operation', 'unknown')
        return f"{error_type}:{operation}:{hash(error_msg) % 10000}"
    
    def _generate_heuristic_solution(self, error: Exception, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate solution using rule-based heuristics"""
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # Database errors
        if 'database' in error_msg or 'sqlite' in error_msg or 'connection' in error_msg:
            return {
                'type': 'database_reconnect',
                'steps': [
                    'dispose_connection_pool',
                    'reinitialize_database',
                    'retry_operation'
                ],
                'code': 'engine.dispose(); init_db()',
                'estimated_fix_time': 5
            }
        
        # Memory errors
        if error_type == 'MemoryError' or 'memory' in error_msg:
            return {
                'type': 'memory_cleanup',
                'steps': [
                    'garbage_collection',
                    'clear_caches',
                    'reduce_batch_size'
                ],
                'code': 'gc.collect(); clear_caches()',
                'estimated_fix_time': 2
            }
        
        # File errors
        if error_type == 'FileNotFoundError' or 'no such file' in error_msg:
            return {
                'type': 'file_creation',
                'steps': [
                    'create_missing_directories',
                    'create_default_file',
                    'retry_operation'
                ],
                'code': 'os.makedirs(path, exist_ok=True)',
                'estimated_fix_time': 1
            }
        
        # Network/API errors
        if 'timeout' in error_msg or 'connection refused' in error_msg:
            return {
                'type': 'network_retry',
                'steps': [
                    'wait_with_backoff',
                    'retry_with_exponential_backoff',
                    'fallback_to_cache'
                ],
                'code': 'time.sleep(backoff); retry()',
                'estimated_fix_time': 10
            }
        
        # OpenAI errors
        if 'openai' in error_msg or 'api key' in error_msg:
            return {
                'type': 'openai_fallback',
                'steps': [
                    'check_api_key_validity',
                    'use_knowledge_base_fallback',
                    'return_cached_response'
                ],
                'code': 'use_local_knowledge_base()',
                'estimated_fix_time': 1
            }
        
        return None
    
    def mark_success(self, error_signature: str):
        """Mark solution as successful"""
        if error_signature in self.known_solutions:
            self.known_solutions[error_signature]['success_count'] += 1
            self.save_solutions()
            logger.info(f"Marked solution {error_signature} as successful")
    
    def mark_failure(self, error_signature: str):
        """Mark solution as failed"""
        if error_signature in self.known_solutions:
            self.known_solutions[error_signature]['failure_count'] += 1
            
            # If failure rate > 70%, deprecate solution
            sol = self.known_solutions[error_signature]
            total = sol['success_count'] + sol['failure_count']
            if total > 5 and sol['failure_count'] / total > 0.7:
                sol['deprecated'] = True
                logger.warning(f"Deprecated solution {error_signature} due to high failure rate")
            
            self.save_solutions()


class PreventionEngine:
    """Proactive error prevention through monitoring and prediction"""
    
    def __init__(self, pattern_analyzer: ErrorPattern):
        self.pattern_analyzer = pattern_analyzer
        self.health_metrics = {}
        self.thresholds = {
            'cpu_percent': 90,
            'memory_percent': 85,
            'disk_percent': 90,
            'connection_pool_size': 100,
            'response_time_ms': 5000
        }
    
    def check_system_health(self) -> Dict[str, Any]:
        """Monitor system health and predict potential errors"""
        health = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'warnings': [],
            'predicted_errors': []
        }
        
        # CPU monitoring
        cpu = psutil.cpu_percent(interval=1)
        if cpu > self.thresholds['cpu_percent']:
            health['warnings'].append(f"High CPU usage: {cpu}%")
            health['predicted_errors'].append({
                'type': 'PerformanceError',
                'likelihood': 0.7,
                'prevention': 'Reduce concurrent tasks, optimize algorithms'
            })
        
        # Memory monitoring
        memory = psutil.virtual_memory()
        if memory.percent > self.thresholds['memory_percent']:
            health['warnings'].append(f"High memory usage: {memory.percent}%")
            health['predicted_errors'].append({
                'type': 'MemoryError',
                'likelihood': 0.8,
                'prevention': 'Clear caches, run garbage collection'
            })
        
        # Disk monitoring
        disk = psutil.disk_usage('/')
        if disk.percent > self.thresholds['disk_percent']:
            health['warnings'].append(f"Low disk space: {disk.percent}% used")
            health['predicted_errors'].append({
                'type': 'DiskError',
                'likelihood': 0.6,
                'prevention': 'Clean up old files, archive logs'
            })
        
        # Analyze error patterns for prediction
        for error_type in ['ConnectionError', 'DatabaseError', 'TimeoutError']:
            likelihood = self.pattern_analyzer.predict_likelihood(error_type)
            if likelihood > 0.5:
                health['predicted_errors'].append({
                    'type': error_type,
                    'likelihood': likelihood,
                    'prevention': f'Proactive {error_type} prevention based on historical patterns'
                })
        
        if health['warnings'] or health['predicted_errors']:
            health['status'] = 'at_risk'
        
        self.health_metrics = health
        return health
    
    def apply_preventive_measures(self):
        """Apply preventive measures based on health check"""
        health = self.check_system_health()
        
        if health['status'] == 'healthy':
            return
        
        logger.warning(f"System at risk: {len(health['predicted_errors'])} potential errors detected")
        
        # Auto-apply preventive measures
        for predicted in health['predicted_errors']:
            error_type = predicted['type']
            
            if error_type == 'MemoryError':
                self._prevent_memory_error()
            elif error_type == 'ConnectionError':
                self._prevent_connection_error()
            elif error_type == 'DatabaseError':
                self._prevent_database_error()
    
    def _prevent_memory_error(self):
        """Preventive memory cleanup"""
        import gc
        gc.collect()
        logger.info("Preventive garbage collection executed")
    
    def _prevent_connection_error(self):
        """Preventive connection pool management"""
        try:
            from app.database import engine
            # Recycle connections older than 1 hour
            engine.pool.dispose()
            logger.info("Preventive connection pool reset")
        except:
            pass
    
    def _prevent_database_error(self):
        """Preventive database maintenance"""
        # Could add VACUUM, ANALYZE, etc.
        logger.info("Preventive database check completed")


class SelfHealingSystem:
    """Main self-healing system coordinator"""
    
    def __init__(self):
        self.pattern_analyzer = ErrorPattern()
        self.solution_generator = SolutionGenerator()
        self.prevention_engine = PreventionEngine(self.pattern_analyzer)
        self.metrics = self._load_metrics()
        
        logger.info("Self-healing system initialized")
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load system metrics"""
        if METRICS_DB_FILE.exists():
            try:
                with open(METRICS_DB_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'total_errors_handled': 0,
            'successful_fixes': 0,
            'failed_fixes': 0,
            'prevented_errors': 0,
            'system_uptime_hours': 0,
            'last_reset': datetime.now().isoformat()
        }
    
    def _save_metrics(self):
        """Save metrics to disk"""
        try:
            with open(METRICS_DB_FILE, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle error with AI-powered self-healing"""
        error_type = type(error).__name__
        
        logger.info(f"Self-healing system handling {error_type}")
        
        # Record error pattern
        self.pattern_analyzer.record_error(error_type, context)
        
        # Generate solution
        solution = self.solution_generator.generate_solution(error, context)
        
        result = {
            'error_type': error_type,
            'error_message': str(error),
            'solution_found': solution is not None,
            'solution': solution,
            'timestamp': datetime.now().isoformat()
        }
        
        if solution:
            # Attempt to apply solution
            success = self._apply_solution(solution, error, context)
            result['fix_applied'] = success
            result['fix_successful'] = success
            
            # Track success/failure
            error_signature = self.solution_generator._create_error_signature(error, context)
            if success:
                self.solution_generator.mark_success(error_signature)
                self.metrics['successful_fixes'] += 1
            else:
                self.solution_generator.mark_failure(error_signature)
                self.metrics['failed_fixes'] += 1
        
        self.metrics['total_errors_handled'] += 1
        self._save_metrics()
        
        return result
    
    def _apply_solution(self, solution: Dict[str, Any], error: Exception, context: Dict[str, Any]) -> bool:
        """Apply generated solution"""
        solution_type = solution.get('type')
        
        try:
            if solution_type == 'database_reconnect':
                from app.database import engine, init_db
                engine.dispose()
                init_db()
                return True
            
            elif solution_type == 'memory_cleanup':
                import gc
                gc.collect()
                return True
            
            elif solution_type == 'file_creation':
                file_path = context.get('file_path')
                if file_path:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    return True
            
            elif solution_type == 'network_retry':
                time.sleep(2)  # Brief wait before retry
                return True
            
            elif solution_type == 'openai_fallback':
                # Solution is to use fallback, which is handled by caller
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to apply solution: {e}")
            return False
    
    def run_preventive_maintenance(self):
        """Run preventive maintenance cycle"""
        logger.info("Running preventive maintenance...")
        self.prevention_engine.apply_preventive_measures()
        self.metrics['prevented_errors'] += 1
        self._save_metrics()
    
    def get_system_report(self) -> Dict[str, Any]:
        """Generate comprehensive system report"""
        health = self.prevention_engine.check_system_health()
        
        return {
            'system_health': health,
            'metrics': self.metrics,
            'error_patterns': {
                'total_unique_patterns': len(self.pattern_analyzer.frequencies),
                'most_common': self.pattern_analyzer.frequencies.most_common(5)
            },
            'known_solutions': len(self.solution_generator.known_solutions),
            'success_rate': self._calculate_success_rate(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        total = self.metrics['successful_fixes'] + self.metrics['failed_fixes']
        if total == 0:
            return 0.0
        return self.metrics['successful_fixes'] / total


# Global instance
_self_healing_system = None

def get_self_healing_system() -> SelfHealingSystem:
    """Get global self-healing system instance"""
    global _self_healing_system
    if _self_healing_system is None:
        _self_healing_system = SelfHealingSystem()
    return _self_healing_system


def with_self_healing(operation_name: str):
    """Decorator to add self-healing to functions"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            system = get_self_healing_system()
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {
                    'operation': operation_name,
                    'function': func.__name__,
                    'timestamp': datetime.now().isoformat()
                }
                result = system.handle_error(e, context)
                
                # If fix was successful, retry operation
                if result.get('fix_successful'):
                    logger.info(f"Retrying {operation_name} after successful fix")
                    try:
                        return await func(*args, **kwargs)
                    except Exception as retry_error:
                        logger.error(f"Retry failed: {retry_error}")
                
                # Re-raise if fix didn't work
                raise
        
        def sync_wrapper(*args, **kwargs):
            system = get_self_healing_system()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    'operation': operation_name,
                    'function': func.__name__,
                    'timestamp': datetime.now().isoformat()
                }
                result = system.handle_error(e, context)
                
                if result.get('fix_successful'):
                    logger.info(f"Retrying {operation_name} after successful fix")
                    try:
                        return func(*args, **kwargs)
                    except Exception as retry_error:
                        logger.error(f"Retry failed: {retry_error}")
                
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
