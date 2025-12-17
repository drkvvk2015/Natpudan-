"""
Knowledge Base Automation API
- Feedback endpoints
- Manual sync triggers
- Integrity checks
- Freshness reporting
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from app.api.auth_new import get_current_user
from app.models import User, UserRole
from app.services.automated_kb_manager import get_automated_kb_manager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["kb-automation"])


class FeedbackRequest(BaseModel):
    answer_id: str
    query: str
    document_ids: List[str]
    rating: int  # 1-5
    comment: Optional[str] = ""


class PubMedSyncRequest(BaseModel):
    queries: List[str]
    max_results_per_query: int = 10


# ==================== FEEDBACK ENDPOINTS ====================

@router.post("/feedback/answer")
async def submit_answer_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback on an answer (1-5 star rating).
    Used to improve KB relevance over time.
    """
    try:
        manager = get_automated_kb_manager()
        feedback = manager.record_answer_feedback(
            answer_id=request.answer_id,
            query=request.query,
            document_ids=request.document_ids,
            rating=request.rating,
            user_comment=request.comment
        )
        
        return {
            "status": "recorded",
            "feedback_id": request.answer_id,
            "message": f"Feedback recorded: {request.rating}/5"
        }
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/stats")
async def get_feedback_statistics(
    current_user: User = Depends(get_current_user)
):
    """Get KB feedback statistics"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        manager = get_automated_kb_manager()
        stats = manager.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PUBMED SYNC ENDPOINTS ====================

@router.post("/sync/pubmed-manual")
async def trigger_pubmed_sync_manual(
    request: PubMedSyncRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger PubMed sync (Admin only).
    Runs in background and returns immediately.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        manager = get_automated_kb_manager()
        
        # Run in background
        async def sync_task():
            result = await manager.sync_pubmed_to_kb(
                queries=request.queries,
                max_results_per_query=request.max_results_per_query
            )
            logger.info(f"Manual PubMed sync completed: {result}")
        
        background_tasks.add_task(sync_task)
        
        return {
            "status": "sync_queued",
            "queries": request.queries,
            "message": "PubMed sync started in background"
        }
    except Exception as e:
        logger.error(f"Error starting PubMed sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/daily-refresh")
async def trigger_daily_refresh(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger daily refresh cycle (Admin only).
    - Sync PubMed
    - Check index integrity
    - Apply freshness tags
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        manager = get_automated_kb_manager()
        
        async def refresh_task():
            result = await manager.run_daily_refresh()
            logger.info(f"Daily refresh completed: {result}")
        
        background_tasks.add_task(refresh_task)
        
        return {
            "status": "refresh_queued",
            "message": "Daily refresh cycle started in background"
        }
    except Exception as e:
        logger.error(f"Error starting daily refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== INTEGRITY CHECK ENDPOINTS ====================

@router.get("/integrity/check")
async def check_kb_integrity(
    current_user: User = Depends(get_current_user)
):
    """Check KB index integrity"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        manager = get_automated_kb_manager()
        result = await manager.check_index_integrity()
        return result
    except Exception as e:
        logger.error(f"Error checking integrity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/integrity/rebuild")
async def rebuild_kb_index(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Rebuild KB index if needed (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        manager = get_automated_kb_manager()
        
        async def rebuild_task():
            result = await manager.rebuild_index_if_needed()
            logger.info(f"Index rebuild completed: {result}")
        
        background_tasks.add_task(rebuild_task)
        
        return {
            "status": "rebuild_queued",
            "message": "KB index rebuild started in background"
        }
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== FRESHNESS ENDPOINTS ====================

@router.get("/freshness/report")
async def get_freshness_report(
    current_user: User = Depends(get_current_user)
):
    """
    Get KB freshness report.
    Shows breakdown of documents by recency.
    """
    try:
        from app.services.local_vector_kb import get_local_knowledge_base
        
        local_kb = get_local_knowledge_base()
        manager = get_automated_kb_manager()
        
        freshness_breakdown = {
            "current": 0,      # < 2 years
            "aging": 0,        # 2-5 years
            "historical": 0,   # 5+ years
            "unknown": 0       # No year info
        }
        
        if hasattr(local_kb, 'documents'):
            for doc in local_kb.documents:
                if "freshness_status" in doc:
                    status = doc["freshness_status"]
                    if status in freshness_breakdown:
                        freshness_breakdown[status] += 1
                else:
                    # Calculate on the fly
                    score = manager.calculate_freshness_score(doc)
                    if score >= 0.8:
                        freshness_breakdown["current"] += 1
                    elif score >= 0.5:
                        freshness_breakdown["aging"] += 1
                    else:
                        freshness_breakdown["historical"] += 1
        
        total = sum(freshness_breakdown.values())
        
        return {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "breakdown": freshness_breakdown,
            "total_documents": total,
            "recommendations": (
                "Consider deprecating historical documents" if freshness_breakdown["historical"] > total * 0.3
                else "KB freshness is good"
            )
        }
    except Exception as e:
        logger.error(f"Error generating freshness report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
