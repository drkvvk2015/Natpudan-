"""KB Growth Monitoring API - Track the self-improving knowledge base"""

from fastapi import APIRouter, HTTPException
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/kb-growth", tags=["kb-growth"])


@router.get("/metrics")
async def get_growth_metrics():
    """Get comprehensive KB growth metrics"""
    try:
        from app.services.kb_growth_orchestrator import get_kb_orchestrator
        orchestrator = get_kb_orchestrator()
        orchestrator.initialize()
        return orchestrator.get_growth_metrics()
    except Exception as e:
        logger.error(f"[KB_GROWTH] Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gaps")
async def get_knowledge_gaps():
    """Get current knowledge gaps (topics KB can't answer well)"""
    try:
        from app.services.kb_gap_detector import get_gap_detector
        detector = get_gap_detector()
        return {
            "statistics": detector.get_statistics(),
            "priority_gaps": detector.get_priority_gaps(limit=20),
        }
    except Exception as e:
        logger.error(f"[KB_GROWTH] Gaps error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-now")
async def trigger_online_fetch():
    """Manually trigger online knowledge fetch"""
    try:
        from app.services.kb_growth_orchestrator import get_kb_orchestrator
        orchestrator = get_kb_orchestrator()
        orchestrator.initialize()
        result = await orchestrator.periodic_online_fetch()
        return {"status": "completed", "result": result}
    except Exception as e:
        logger.error(f"[KB_GROWTH] Manual fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fill-gaps")
async def fill_knowledge_gaps():
    """Manually trigger gap-filling from online sources"""
    try:
        from app.services.kb_growth_orchestrator import get_kb_orchestrator
        orchestrator = get_kb_orchestrator()
        orchestrator.initialize()

        if not orchestrator._ingester or not orchestrator._kb or not orchestrator._gap_detector:
            return {"status": "not_ready", "message": "Services not fully initialized"}

        result = await orchestrator._ingester.acquire_gap_knowledge(
            kb=orchestrator._kb,
            gap_detector=orchestrator._gap_detector,
            max_topics=10,
        )
        return {"status": "completed", "result": result}
    except Exception as e:
        logger.error(f"[KB_GROWTH] Gap fill error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/seed-status")
async def get_seed_status():
    """Check if KB has been seeded"""
    try:
        from app.services.kb_auto_seeder import is_seeded, _get_seed_marker_path
        import json
        import os

        marker_path = _get_seed_marker_path()
        if is_seeded():
            with open(marker_path, "r") as f:
                data = json.load(f)
            return {"seeded": True, **data}
        else:
            return {"seeded": False}
    except Exception as e:
        return {"seeded": False, "error": str(e)}
