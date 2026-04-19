"""Background worker lifecycle wrappers."""

from __future__ import annotations

import asyncio
from typing import Any, Dict


async def queue_worker_loop(interval_seconds: int = 5) -> None:
    from app.services.upload_queue_processor import process_upload_queue

    while True:
        try:
            process_upload_queue()
        except Exception:
            pass
        await asyncio.sleep(interval_seconds)


async def kb_growth_loop(interval_seconds: int = 3600) -> None:
    await asyncio.sleep(60)
    while True:
        try:
            from app.services.kb_growth_orchestrator import get_kb_orchestrator

            orchestrator = get_kb_orchestrator()
            await orchestrator.periodic_online_fetch()
        except Exception:
            pass
        await asyncio.sleep(interval_seconds)


async def wearable_sync_loop(interval_seconds: int = 300) -> None:
    from app.services.wearable_sync import get_wearable_sync
    from app.database import SessionLocal
    from app.models import WearableDeviceAuth
    from datetime import datetime, timezone, timedelta

    while True:
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            due_devices = db.query(WearableDeviceAuth).filter(
                WearableDeviceAuth.is_active.is_(True),
                WearableDeviceAuth.is_revoked.is_(False),
                WearableDeviceAuth.auto_sync_enabled.is_(True),
            ).all()

            wearable_sync = get_wearable_sync()
            for auth in due_devices:
                if auth.last_sync_at:
                    next_sync = auth.last_sync_at + timedelta(minutes=auth.sync_interval_minutes)
                    if now < next_sync:
                        continue

                if auth.device_type == "fitbit":
                    result: Dict[str, Any] = await wearable_sync.fetch_fitbit_data(
                        access_token=auth.access_token,
                        user_id=auth.device_user_id,
                        data_type="heart_rate",
                    )
                    if result.get("success"):
                        auth.last_sync_at = datetime.now(timezone.utc)
                        auth.sync_error_count = 0
                    else:
                        auth.sync_error_count = (auth.sync_error_count or 0) + 1
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
        await asyncio.sleep(interval_seconds)


async def autonomous_agent_loop(interval_seconds: int = 7200) -> None:
    """
    Autonomous research agent loop - runs every 2 hours.
    """
    await asyncio.sleep(300)  # Wait 5 minutes after startup
    while True:
        try:
            from app.services.autonomous_research_agent import get_research_agent
            agent = get_research_agent()
            result = await agent.run_cycle()
            print(f"[AGENT] Autonomous cycle complete: {result}")
        except Exception as e:
            print(f"[AGENT] Loop error: {e}")
        await asyncio.sleep(interval_seconds)
