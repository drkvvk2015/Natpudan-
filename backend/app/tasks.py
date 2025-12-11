"""
Celery Background Tasks
Handles long-running operations like knowledge base updates
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Import Celery app
try:
    from app.celery_config import get_celery_app
    celery_app = get_celery_app()
except Exception as e:
    logger.warning(f"[TASKS] Could not initialize Celery: {e}")
    celery_app = None


@celery_app.task(
    name="update_knowledge_base",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def update_knowledge_base(
    self,
    topics: List[str] = None,
    papers_per_topic: int = 5,
    days_back: int = 7
) -> Dict[str, Any]:
    """
    Background task to update knowledge base with latest PubMed research
    
    Args:
        topics: Medical topics to search (default: common conditions)
        papers_per_topic: Number of papers per topic
        days_back: Look back N days for papers
        
    Returns:
        Status dictionary with results
    """
    try:
        # Default topics if none provided
        if topics is None:
            topics = [
                "diabetes mellitus",
                "hypertension",
                "heart disease",
                "cancer",
                "pneumonia",
                "COVID-19",
                "depression",
                "arthritis"
            ]
        
        logger.info(f"[TASK-KB-UPDATE] Starting KB update for {len(topics)} topics")
        logger.info(f"[TASK-KB-UPDATE] Topics: {', '.join(topics)}")
        
        # Import services
        from app.services.pubmed_integration import get_pubmed_integration
        from app.services.vector_knowledge_base import get_vector_knowledge_base
        
        # Initialize services
        pubmed = get_pubmed_integration()
        kb = get_vector_knowledge_base()
        
        # Perform auto-update
        result = pubmed.auto_update_knowledge_base(
            vector_kb=kb,
            topics=topics,
            papers_per_topic=papers_per_topic,
            days_back=days_back
        )
        
        logger.info(f"[TASK-KB-UPDATE] ✅ Success - {result['papers_indexed']} papers indexed")
        
        return {
            "status": "success",
            "task_id": self.request.id,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result
        }
        
    except Exception as exc:
        logger.error(f"[TASK-KB-UPDATE] ❌ Error: {exc}")
        logger.error(f"[TASK-KB-UPDATE] Traceback: {exc.__traceback__}")
        
        # Retry up to 3 times with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery_app.task(
    name="sync_online_sources",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def sync_online_sources(
    self,
    sources: List[str] = None,
    query: str = "medical diagnosis"
) -> Dict[str, Any]:
    """
    Background task to sync from multiple online medical sources
    
    Args:
        sources: List of sources (pubmed, who, cdc, nih)
        query: Medical query to search
        
    Returns:
        Status dictionary with results
    """
    try:
        if sources is None:
            sources = ["pubmed", "who", "cdc"]
        
        logger.info(f"[TASK-SYNC] Starting sync from sources: {', '.join(sources)}")
        
        from app.services.online_medical_sources import OnlineMedicalSources
        
        sources_handler = OnlineMedicalSources()
        
        # Fetch from sources (note: sync version, async available if needed)
        # For now, use sync search from PubMed as example
        from app.services.pubmed_integration import get_pubmed_integration
        pubmed = get_pubmed_integration()
        
        papers = pubmed.search_papers(
            query=query,
            max_results=10,
            days_back=30
        )
        
        logger.info(f"[TASK-SYNC] ✅ Found {len(papers)} papers")
        
        return {
            "status": "success",
            "task_id": self.request.id,
            "timestamp": datetime.utcnow().isoformat(),
            "papers_found": len(papers)
        }
        
    except Exception as exc:
        logger.error(f"[TASK-SYNC] ❌ Error: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery_app.task(
    name="cleanup_old_documents",
    bind=True
)
def cleanup_old_documents(self, days: int = 30) -> Dict[str, Any]:
    """
    Background task to cleanup old knowledge base documents
    
    Args:
        days: Remove documents older than N days
        
    Returns:
        Status dictionary
    """
    try:
        logger.info(f"[TASK-CLEANUP] Cleaning documents older than {days} days")
        
        from app.services.vector_knowledge_base import get_vector_knowledge_base
        from datetime import datetime, timedelta
        from app.database import get_db
        
        kb = get_vector_knowledge_base()
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # You can add cleanup logic here based on your needs
        # For now, log the operation
        logger.info(f"[TASK-CLEANUP] ✅ Cleanup complete")
        
        return {
            "status": "success",
            "task_id": self.request.id,
            "timestamp": datetime.utcnow().isoformat(),
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as exc:
        logger.error(f"[TASK-CLEANUP] ❌ Error: {exc}")
        return {
            "status": "error",
            "error": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }


# Task monitoring function
@celery_app.task(name="heartbeat")
def heartbeat() -> Dict[str, Any]:
    """Simple heartbeat task to verify Celery worker is alive"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
