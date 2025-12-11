"""
Celery Configuration for Background Tasks
Handles scheduled knowledge base updates and other long-running tasks
"""

import os
import logging

logger = logging.getLogger(__name__)

# Redis broker URL (change to your Redis server)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery configuration
class CeleryConfig:
    broker_url = REDIS_URL
    result_backend = REDIS_URL
    
    # Task settings
    task_serializer = "json"
    accept_content = ["json"]
    result_serializer = "json"
    timezone = "UTC"
    enable_utc = True
    
    # Task timeouts
    task_soft_time_limit = 3600  # 1 hour soft limit
    task_time_limit = 7200  # 2 hour hard limit
    
    # Result settings
    result_expires = 86400  # Results expire after 24 hours
    
    # Worker settings
    worker_prefetch_multiplier = 1
    worker_max_tasks_per_child = 1000
    
    # Retry settings
    task_acks_late = True
    task_reject_on_worker_lost = True
    
    # Beat scheduler settings (for periodic tasks)
    beat_scheduler = "celery.beat:PersistentScheduler"

def init_celery(app):
    """Initialize Celery with FastAPI app"""
    from celery import Celery
    
    celery_app = Celery(
        app.title if hasattr(app, 'title') else "natpudan",
        broker=CeleryConfig.broker_url,
        backend=CeleryConfig.result_backend
    )
    
    # Load configuration
    celery_app.config_from_object(CeleryConfig)
    
    # Auto-discover tasks from all registered modules
    celery_app.autodiscover_tasks([
        "app.tasks"
    ])
    
    logger.info(f"[CELERY] Initialized with broker: {REDIS_URL}")
    
    return celery_app

# Create global celery app instance
try:
    from celery import Celery
    celery_app = Celery(
        "natpudan",
        broker=REDIS_URL,
        backend=REDIS_URL
    )
    celery_app.config_from_object(CeleryConfig)
    logger.info("[CELERY] Configuration loaded")
except Exception as e:
    logger.warning(f"[CELERY] Warning during initialization: {e}")
    celery_app = None

def get_celery_app():
    """Get Celery app instance"""
    global celery_app
    if celery_app is None:
        from celery import Celery
        celery_app = Celery(
            "natpudan",
            broker=REDIS_URL,
            backend=REDIS_URL
        )
        celery_app.config_from_object(CeleryConfig)
    return celery_app
