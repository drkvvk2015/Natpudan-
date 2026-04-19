"""App lifespan orchestration helpers."""

from __future__ import annotations

from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import FastAPI

from app.core.config import settings
from app.monitoring import init_monitoring
from app.telemetry import init_telemetry
from app.database import init_db
from app.workers import queue_worker_loop, wearable_sync_loop, kb_growth_loop

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(_app: FastAPI):
    """Centralized startup/shutdown orchestration."""
    queue_task = None
    wearable_task = None
    kb_task = None

    settings.validate()
    init_monitoring()
    init_telemetry(service_name="natpudan-backend")

    try:
        init_db()
    except Exception as exc:
        logger.warning("Database init failed during lifespan startup: %s", exc)

    try:
        from app.services.upload_queue_processor import get_queue_processor

        processor = get_queue_processor()
        processor.start()
    except Exception as exc:
        logger.warning("Queue processor start failed: %s", exc)

    # Initialize futuristic KB components
    try:
        from app.services.kb_growth_orchestrator import get_kb_orchestrator
        orchestrator = get_kb_orchestrator()
        orchestrator.initialize()
        orchestrator.seed_if_needed()
        logger.info("✓ Futuristic KB orchestrator initialized")
    except Exception as exc:
        logger.warning("Futuristic KB init failed: %s", exc)

    queue_task = asyncio.create_task(queue_worker_loop())
    wearable_task = asyncio.create_task(wearable_sync_loop())
    kb_task = asyncio.create_task(kb_growth_loop())

    try:
        yield
    finally:
        try:
            from app.services.upload_queue_processor import get_queue_processor

            get_queue_processor().stop()
        except Exception:
            pass

        for task in (queue_task, wearable_task, kb_task):
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
