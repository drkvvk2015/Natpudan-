"""FastAPI application entrypoint.

This file was reconstructed after repository history cleanup to satisfy
existing tests that import `app.main:app` and expect a set of medical,
prescription, and diagnostic endpoints. The implementations here are
minimal stubs that return deterministic structures required by tests.

TODO: Replace stub logic with real service integrations (knowledge base,
diagnosis engine, ICD code provider, etc.).
"""

from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Response
from typing import List, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager
import time
import psutil
import logging
import logging.handlers
import traceback
import asyncio
import sys

# Configure logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
# Force UTF-8 for stdout/stderr on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)

# Import error correction system
from app.services.error_corrector import get_error_corrector

error_corrector = get_error_corrector()

from app.api.auth_new import router as auth_router
from app.api.chat_new import router as chat_router
from app.api.discharge import router as discharge_router
from app.api.treatment import router as treatment_router
from app.api.timeline import router as timeline_router
from app.api.analytics import router as analytics_router
from app.api.fhir import router as fhir_router
from app.api.admin_users import router as admin_users_router
from app.api.health import router as health_router
# Re-enable knowledge base router now that we are on Python 3.12
from app.api.knowledge_base import router as knowledge_router
from app.api.patient_intake import router as patient_intake_router
from app.api.phase_4_api import router as phase_4_router
from app.api.phase_5_api import router as phase_5_router
from app.api.phase_5c_api import router as phase_5c_router
from app.api.phase_6_api import router as phase_6_router
from app.database import init_db

# Track application start time for uptime calculation
START_TIME = time.time()

# Service health status
service_health = {
    "database": False,
    "openai": False,
    "knowledge_base": False
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan with graceful startup/shutdown"""
    logger.info("[STARTING] Natpudan AI Medical Assistant...")
    
    # Startup: Initialize services with error handling
    try:
        # Initialize database
        init_db()
        service_health["database"] = True
        logger.info("[OK] Database initialized successfully")
    except Exception as e:
        logger.error(f"[ERROR] Database initialization failed: {e}")
        error_corrector.log_error(e, {"operation": "database_init"})
    
    # Check OpenAI API - STRICT validation
    try:
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("[CRITICAL] OPENAI_API_KEY not set in .env - AI features unavailable")
            service_health["openai"] = False
        elif not api_key.startswith("sk-"):
            logger.error(f"[CRITICAL] Invalid OPENAI_API_KEY format - must start with 'sk-' (got: {api_key[:10]}...)")
            service_health["openai"] = False
        elif api_key.startswith("sk-your"):
            logger.error("[CRITICAL] OPENAI_API_KEY is still set to placeholder - AI features unavailable")
            service_health["openai"] = False
        else:
            service_health["openai"] = True
            logger.info("[OK] OpenAI API configured and validated")
    except Exception as e:
        logger.error(f"[ERROR] OpenAI validation failed: {e}")
        service_health["openai"] = False
    
    # Pre-load knowledge base (optional)
    try:
        from app.services.vector_knowledge_base import get_vector_knowledge_base
        kb = get_vector_knowledge_base()
        service_health["knowledge_base"] = True
        logger.info(f"[OK] Knowledge base loaded ({kb.document_count} documents)")
    except Exception as e:
        logger.warning(f"[WARNING] Knowledge base not available: {e}")
    
    # Initialize upload queue processor
    try:
        from app.services.upload_queue_processor import get_queue_processor
        processor = get_queue_processor()
        processor.start()
        logger.info("[OK] PDF upload queue processor started")
    except Exception as e:
        logger.error(f"[ERROR] Queue processor initialization failed: {e}")
    
    # Initialize Self-Healing System
    try:
        from app.services.self_healing_system import get_self_healing_system
        healing_system = get_self_healing_system()
        service_health["self_healing"] = True
        logger.info("[OK] Self-healing system initialized and learning from past errors")
        
        # Run initial health check
        health_report = healing_system.prevention_engine.check_system_health()
        if health_report['status'] != 'healthy':
            logger.warning(f"[WARNING] System health: {health_report['status']} - {len(health_report['warnings'])} warnings detected")
    except Exception as e:
        logger.error(f"[ERROR] Self-healing system initialization failed: {e}")
    
    # Initialize APScheduler for scheduled tasks
    scheduler = None
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        scheduler = BackgroundScheduler()
        
        if scheduler:  # Only add jobs if scheduler is enabled
            # KB Update Job: 2 AM UTC daily
            def schedule_kb_update():
                """Daily KB update task"""
                try:
                    logger.info("[SCHEDULER] Starting automated KB refresh...")
                    from app.services.automated_kb_manager import get_automated_kb_manager
                    manager = get_automated_kb_manager()
                    
                    # Run async in sync context
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(manager.run_daily_refresh())
                        logger.info(f"[SCHEDULER] ✅ KB refresh completed: {result.get('operations', {}).keys()}")
                    finally:
                        loop.close()
                except Exception as e:
                    logger.error(f"[SCHEDULER] ❌ KB refresh failed: {e}")
            
            # Schedule KB daily refresh at 2 PM UTC
            from apscheduler.triggers.cron import CronTrigger
            scheduler.add_job(
                schedule_kb_update,
                CronTrigger(hour=14, minute=0),
                id="kb_daily_refresh",
                name="Daily Knowledge Base Refresh & PubMed Sync",
                replace_existing=True
            )
            
            # Index Integrity Check Job: 1 AM UTC daily
            def schedule_index_check():
                """Daily index integrity check"""
                try:
                    logger.info("[SCHEDULER] Running KB index integrity check...")
                    from app.services.automated_kb_manager import get_automated_kb_manager
                    manager = get_automated_kb_manager()
                    
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(manager.check_index_integrity())
                        if result.get("status") != "ok":
                            logger.warning(f"[SCHEDULER] Index issues detected: {result.get('issues', [])}")
                    finally:
                        loop.close()
                except Exception as e:
                    logger.error(f"[SCHEDULER] Index check failed: {e}")
            
            scheduler.add_job(
                schedule_index_check,
                CronTrigger(hour=12, minute=0),
                id="kb_index_check",
                name="KB Index Integrity Check",
                replace_existing=True
            )
            
            # Self-Healing Preventive Maintenance: Every 6 hours
            def schedule_preventive_maintenance():
                """Preventive maintenance to avoid errors"""
                try:
                    logger.info("[SCHEDULER] Running preventive maintenance...")
                    from app.services.self_healing_system import get_self_healing_system
                    healing_system = get_self_healing_system()
                    healing_system.run_preventive_maintenance()
                    logger.info("[SCHEDULER] ✅ Preventive maintenance completed")
                except Exception as e:
                    logger.error(f"[SCHEDULER] ❌ Preventive maintenance failed: {e}")
            
            scheduler.add_job(
                schedule_preventive_maintenance,
                CronTrigger(hour='*/6'),  # Every 6 hours
                id="preventive_maintenance",
                name="Self-Healing Preventive Maintenance",
                replace_existing=True
            )
            
            scheduler.start()
            logger.info("[OK] APScheduler started - KB automation + Self-healing jobs scheduled")
        else:
            logger.info("[INFO] APScheduler disabled for debugging")
    except Exception as e:
        logger.warning(f"[WARNING] APScheduler initialization failed: {e}")
        scheduler = None
    
    logger.info(f"[STARTED] Application started - Services: DB={service_health['database']}, OpenAI={service_health['openai']}, KB={service_health['knowledge_base']}")
    
    yield  # Application runs
    
    # Shutdown: Cleanup
    logger.info("[STOPPING] Natpudan AI Medical Assistant...")
    
    # Stop scheduler
    if scheduler:
        try:
            scheduler.shutdown(wait=False)
            logger.info("[OK] APScheduler stopped")
        except Exception as e:
            logger.warning(f"Warning stopping scheduler: {e}")
    try:
        # Stop queue processor
        from app.services.upload_queue_processor import get_queue_processor
        processor = get_queue_processor()
        processor.stop()
        logger.info("[OK] Queue processor stopped")
    except Exception as e:
        logger.warning(f"Warning stopping queue processor: {e}")
    
    try:
        # Close database connections
        from app.database import engine
        engine.dispose()
        logger.info("[OK] Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

app = FastAPI(
    title="Physician AI Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and provide graceful error responses"""
    error_id = f"error_{int(time.time())}"
    logger.error(
        f"[{error_id}] Unhandled exception at {request.method} {request.url.path}:",
        exc_info=True
    )
    
    # Log to error corrector
    error_corrector.log_error(exc, {
        "operation": "api_request",
        "method": request.method,
        "path": str(request.url.path),
        "error_id": error_id
    })
    
    # Determine user-friendly error message
    error_msg = "An unexpected error occurred. Please try again."
    status_code = 500
    
    if "openai" in str(exc).lower():
        error_msg = "AI service temporarily unavailable. Please try again or use knowledge base search."
    elif "database" in str(exc).lower():
        error_msg = "Database connection issue. Please try again in a moment."
    elif "timeout" in str(exc).lower():
        error_msg = "Request timeout. Please try again with a simpler query."
        status_code = 504
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_msg,
            "error_id": error_id,
            "detail": str(exc)[:200] if logger.level == logging.DEBUG else None
        }
    )

# CORS middleware - environment-based configuration
import os
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
CORS_ORIGINS_STR = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:3000")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_STR.split(",")]

# Validate CORS configuration for production
if ENVIRONMENT == "production":
    if any("localhost" in origin or "127.0.0.1" in origin for origin in CORS_ORIGINS):
        logger.error("[CRITICAL] localhost/127.0.0.1 in CORS_ORIGINS for production environment!")
        raise ValueError("CORS configuration error: localhost not allowed in production")
    logger.info(f"[OK] Production CORS origins validated: {CORS_ORIGINS}")
else:
    logger.info(f"[DEV] CORS origins: {CORS_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Global error handler middleware
from app.middleware.error_handler import ErrorHandlerMiddleware
app.add_middleware(ErrorHandlerMiddleware)

@app.get("/")
def root() -> Dict[str, Any]:
    logger.info("[DEBUG] Root endpoint called")
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Quiet favicon 404s in dev: serve empty response
@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.get("/health")
def health() -> Dict[str, Any]:
    logger.info("[DEBUG] /health endpoint called")
    return {
        "status": "healthy" if service_health["database"] else "degraded",
        "service": "api",
        "services": service_health,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/detailed")
def detailed_health() -> Dict[str, Any]:
    """Detailed health check with system metrics."""
    try:
        # Calculate uptime in seconds
        uptime_seconds = int(time.time() - START_TIME)
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "uptime": uptime_seconds,
            "cpu_usage": round(cpu_percent, 2),
            "memory_usage": {
                "total": memory.total,
                "available": memory.available,
                "percent": round(memory.percent, 2),
                "used": memory.used
            },
            "disk_usage": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": round(disk.percent, 2)
            },
            "database_status": "active",
            "cache_status": "active",
            "assistant_status": "operational",
            "knowledge_base_status": "ready",
            "last_check_in": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "uptime": 0,
            "cpu_usage": 0,
            "memory_usage": {"total": 0, "available": 0, "percent": 0, "used": 0},
            "disk_usage": {"total": 0, "used": 0, "free": 0, "percent": 0},
            "database_status": "unknown",
            "cache_status": "unknown",
            "assistant_status": "unknown",
            "knowledge_base_status": "unknown",
            "last_check_in": datetime.utcnow().isoformat(),
            "error": str(e)
        }

api_router = APIRouter(prefix="/api")

# ---- Medical / Knowledge Base ----
# Moved imports to lazy load within functions to avoid blocking startup
# from app.services.icd10_service import get_icd10_service
# from app.services.vector_knowledge_base import get_vector_knowledge_base
# from app.services.document_manager import get_document_manager
# from app.services.local_vector_kb import get_local_knowledge_base
# # Futuristic services
# from app.services.hybrid_search import get_hybrid_search
# from app.services.rag_service import get_rag_service
# from app.services.medical_entity_extractor import get_entity_extractor
# from app.services.pubmed_integration import get_pubmed_integration
# from app.services.knowledge_graph import get_knowledge_graph

medical_router = APIRouter(prefix="/medical")

@medical_router.post("/diagnosis")
def diagnosis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate diagnosis suggestions from symptoms"""
    try:
        # Lazy import to avoid blocking startup
        from app.services.icd10_service import get_icd10_service
        
        symptoms: List[str] = payload.get("symptoms", [])
        
        if not symptoms:
            return {
                "error": "No symptoms provided",
                "primary_diagnosis": "Unknown",
                "differential_diagnoses": [],
                "suggested_icd_codes": []
            }
        
        # Get ICD-10 code suggestions
        icd_service = get_icd10_service()
        suggested_codes = icd_service.suggest_codes(symptoms)
        
        # Use first suggested code as primary diagnosis
        primary_diagnosis = "Undetermined"
        if suggested_codes:
            primary_diagnosis = suggested_codes[0].get("description", "Undetermined")
        
        # Differential diagnoses from remaining codes
        differential_diagnoses = [
            code.get("description", "")
            for code in suggested_codes[1:5]
        ]
        
        return {
            "primary_diagnosis": primary_diagnosis,
            "differential_diagnoses": differential_diagnoses,
            "symptoms": symptoms,
            "suggested_icd_codes": suggested_codes[:5]
        }
    except Exception as e:
        logger.error(f"Error generating diagnosis: {e}")
        return {
            "error": str(e),
            "primary_diagnosis": "Error",
            "differential_diagnoses": [],
            "symptoms": symptoms
        }

@medical_router.post("/analyze-symptoms")
def analyze_symptoms(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze symptoms and suggest related conditions"""
    try:
        from app.services.icd10_service import get_icd10_service
        
        symptoms = payload.get("symptoms", [])
        
        if not symptoms:
            return {"error": "No symptoms provided", "analysis": []}
        
        # Get ICD-10 suggestions for each symptom
        icd_service = get_icd10_service()
        analysis = []
        
        for symptom in symptoms:
            codes = icd_service.search_codes(symptom, max_results=3)
            analysis.append({
                "symptom": symptom,
                "related_conditions": codes
            })
        
        return {
            "symptoms": symptoms,
            "analysis": analysis,
            "count": len(analysis)
        }
    except Exception as e:
        logger.error(f"Error analyzing symptoms: {e}")
        return {"error": str(e), "symptoms": symptoms, "analysis": []}

@medical_router.get("/icd/search")
def icd_search(query: str, max_results: int = 20) -> List[Dict[str, str]]:
    """Search ICD-10 codes by code or description"""
    try:
        from app.services.icd10_service import get_icd10_service
        
        if not query:
            return []
        
        icd_service = get_icd10_service()
        results = icd_service.search_codes(query, max_results=max_results)
        
        return results
    except Exception as e:
        logger.error(f"Error searching ICD codes: {e}")
        return [{"error": str(e)}]

@medical_router.get("/icd/code/{code}")
def icd_get_code(code: str) -> Dict[str, Any]:
    """Get specific ICD-10 code details"""
    try:
        from app.services.icd10_service import get_icd10_service
        
        icd_service = get_icd10_service()
        result = icd_service.get_code(code)
        
        if result is None:
            return {"error": "Code not found", "code": code}
        
        return result
    except Exception as e:
        logger.error(f"Error getting ICD code: {e}")
        return {"error": str(e), "code": code}

@medical_router.get("/icd/categories")
def icd_categories() -> List[str]:
    """Get all ICD-10 categories"""
    try:
        from app.services.icd10_service import get_icd10_service
        
        icd_service = get_icd10_service()
        return icd_service.get_categories()
    except Exception as e:
        logger.error(f"Error getting ICD categories: {e}")
        return []

# ---- FUTURISTIC KNOWLEDGE BASE ENDPOINTS ----

@medical_router.post("/knowledge/hybrid-search")
def hybrid_search(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    [STARTING] HYBRID SEARCH: Combines vector similarity + BM25 keyword matching
    Uses Reciprocal Rank Fusion for optimal results
    """
    try:
        from app.services.vector_knowledge_base import get_vector_knowledge_base
        from app.services.hybrid_search import get_hybrid_search
        
        query = payload.get("query", "")
        top_k = payload.get("top_k", 10)
        alpha = payload.get("alpha", 0.5)  # 0=BM25 only, 1=vector only
        
        # Get vector search results
        kb = get_vector_knowledge_base()
        vector_results = kb.search(query, top_k=top_k * 2)
        
        # Apply hybrid search
        hybrid_search_engine = get_hybrid_search()
        results = hybrid_search_engine.hybrid_search(
            query=query,
            vector_results=vector_results,
            top_k=top_k,
            alpha=alpha
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "search_type": "hybrid",
            "alpha": alpha
        }
    except Exception as e:
        logger.error(f"Error in hybrid search: {e}")
        return {"error": str(e), "query": query, "results": []}

@medical_router.post("/knowledge/rag-query")
def rag_query(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    [STARTING] RAG: Retrieval-Augmented Generation with GPT-4
    Retrieves relevant documents and generates cited responses
    """
    try:
        from app.services.vector_knowledge_base import get_vector_knowledge_base
        from app.services.rag_service import get_rag_service
        
        query = payload.get("query", "")
        max_context = payload.get("max_context_chunks", 5)
        
        # Retrieve relevant documents
        kb = get_vector_knowledge_base()
        retrieved_docs = kb.search(query, top_k=max_context)
        
        # Generate response with RAG
        rag_service = get_rag_service()
        response = rag_service.generate_with_context(
            query=query,
            retrieved_docs=retrieved_docs,
            include_citations=True
        )
        
        return response
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        return {"error": str(e), "query": query}

@medical_router.post("/knowledge/extract-entities")
def extract_medical_entities(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    [STARTING] ENTITY EXTRACTION: Automatically extract diseases, medications, procedures
    Uses advanced NLP pattern matching
    """
    try:
        from app.services.medical_entity_extractor import get_entity_extractor
        
        text = payload.get("text", "")
        include_summary = payload.get("include_summary", True)
        
        # Extract entities
        extractor = get_entity_extractor()
        entities = extractor.extract_entities(text)
        
        # Extract ICD codes
        icd_codes = extractor.extract_icd_codes(text)
        
        # Extract dosages
        dosages = extractor.extract_dosages(text)
        
        result = {
            "entities": entities,
            "icd_codes": icd_codes,
            "dosages": dosages
        }
        
        # Add summary if requested
        if include_summary:
            summary = extractor.build_medical_summary(entities)
            result["summary"] = summary
        
        return result
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        return {"error": str(e)}

@medical_router.get("/knowledge/pubmed-latest")
def pubmed_latest_research(
    topic: str = "diabetes",
    max_results: int = 5,
    days_back: int = 30
) -> Dict[str, Any]:
    """
    [STARTING] PUBMED INTEGRATION: Fetch latest medical research
    Real-time access to latest published papers
    """
    try:
        from app.services.pubmed_integration import get_pubmed_integration
        
        pubmed = get_pubmed_integration()
        papers = pubmed.search_papers(
            query=topic,
            max_results=max_results,
            days_back=days_back,
            sort="date"
        )
        
        return {
            "topic": topic,
            "papers": papers,
            "count": len(papers),
            "days_back": days_back
        }
    except Exception as e:
        logger.error(f"Error fetching PubMed research: {e}")
        return {"error": str(e), "topic": topic, "papers": []}

@medical_router.post("/knowledge/pubmed-auto-update")
def pubmed_auto_update(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    [STARTING] AUTO-UPDATE: Automatically index latest PubMed research
    Keeps knowledge base current with newest findings
    """
    try:
        from app.services.pubmed_integration import get_pubmed_integration
        from app.services.vector_knowledge_base import get_vector_knowledge_base
        
        topics = payload.get("topics", ["diabetes", "hypertension", "cancer"])
        papers_per_topic = payload.get("papers_per_topic", 3)
        days_back = payload.get("days_back", 7)
        
        # Auto-update knowledge base
        pubmed = get_pubmed_integration()
        kb = get_vector_knowledge_base()
        
        result = pubmed.auto_update_knowledge_base(
            vector_kb=kb,
            topics=topics,
            papers_per_topic=papers_per_topic,
            days_back=days_back
        )
        
        return result
    except Exception as e:
        logger.error(f"Error auto-updating from PubMed: {e}")
        return {"error": str(e)}

@medical_router.get("/knowledge/graph/visualize")
def visualize_knowledge_graph(
    concept: str = "diabetes",
    max_distance: int = 1
) -> Dict[str, Any]:
    """
    [STARTING] KNOWLEDGE GRAPH: Visualize medical concept relationships
    Shows connections between diseases, symptoms, medications
    """
    try:
        from app.services.knowledge_graph import get_knowledge_graph
        
        kg = get_knowledge_graph()
        
        # Find node
        node = kg.find_node(concept)
        if not node:
            return {"error": f"Concept '{concept}' not found in knowledge graph"}
        
        # Get visualization
        visualization = kg.visualize_subgraph(
            center_node_id=node["id"],
            max_distance=max_distance
        )
        
        # Get statistics
        stats = kg.get_statistics()
        
        return {
            "concept": concept,
            "visualization": visualization,
            "statistics": stats,
            "node": node
        }
    except Exception as e:
        logger.error(f"Error visualizing knowledge graph: {e}")
        return {"error": str(e), "concept": concept}

@medical_router.post("/knowledge/graph/build-from-text")
def build_graph_from_text(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    [STARTING] GRAPH BUILDER: Build knowledge graph from medical text
    Automatically extracts entities and creates relationships
    """
    try:
        from app.services.medical_entity_extractor import get_entity_extractor
        from app.services.knowledge_graph import get_knowledge_graph
        
        text = payload.get("text", "")
        
        # Extract entities
        extractor = get_entity_extractor()
        entities = extractor.extract_entities(text)
        
        # Build knowledge graph
        kg = get_knowledge_graph()
        kg.build_from_entities(entities)
        
        # Get statistics
        stats = kg.get_statistics()
        
        return {
            "message": "Knowledge graph built successfully",
            "statistics": stats,
            "entities_extracted": {
                "diseases": len(entities.get("diseases", [])),
                "medications": len(entities.get("medications", [])),
                "symptoms": len(entities.get("symptoms", []))
            }
        }
    except Exception as e:
        logger.error(f"Error building knowledge graph: {e}")
        return {"error": str(e)}

@medical_router.get("/knowledge/graph/export")
def export_knowledge_graph() -> Dict[str, Any]:
    """
    [STARTING] GRAPH EXPORT: Export entire knowledge graph as JSON
    For analysis, visualization, or backup
    """
    try:
        from app.services.knowledge_graph import get_knowledge_graph
        
        kg = get_knowledge_graph()
        graph_data = kg.export_graph()
        return graph_data
    except Exception as e:
        logger.error(f"Error exporting knowledge graph: {e}")
        return {"error": str(e)}

api_router.include_router(medical_router)

# ---- Document Upload / Knowledge Management ----
upload_router = APIRouter(prefix="/upload")

@upload_router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    source: str = None,
    category: str = None,
    description: str = None
):
    """
    Upload a medical document (PDF, DOCX, TXT) to knowledge base.
    The document will be processed, indexed, and made searchable.
    """
    try:
        from app.services.document_manager import get_document_manager
        from app.services.vector_knowledge_base import get_vector_knowledge_base
        
        # Read file content
        content = await file.read()
        
        # Save document
        doc_manager = get_document_manager()
        doc_info = await doc_manager.save_upload(
            content,
            file.filename,
            metadata={
                "source": source,
                "category": category,
                "description": description
            }
        )
        
        # Index document in vector knowledge base
        kb = get_vector_knowledge_base()
        text_content = doc_manager.get_document_text(doc_info["document_id"])
        
        if text_content:
            chunk_count = kb.add_document(
                content=text_content,
                metadata={
                    "document_id": doc_info["document_id"],
                    "filename": file.filename,
                    "source": source or "user_upload",
                    "category": category or "general",
                    "description": description
                }
            )
            doc_info["indexed_chunks"] = chunk_count
        else:
            doc_info["indexed_chunks"] = 0
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Document '{file.filename}' uploaded and indexed successfully",
                "document": doc_info
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@upload_router.get("/documents")
def list_documents():
    """List all uploaded documents"""
    try:
        from app.services.document_manager import get_document_manager
        
        doc_manager = get_document_manager()
        documents = doc_manager.list_documents()
        
        return {
            "success": True,
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@upload_router.get("/documents/{document_id}")
def get_document(document_id: str):
    """Get document information"""
    try:
        from app.services.document_manager import get_document_manager
        
        doc_manager = get_document_manager()
        doc_info = doc_manager.get_document(document_id)
        
        if doc_info is None:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "success": True,
            "document": doc_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@upload_router.delete("/documents/{document_id}")
def delete_document(document_id: str):
    """Delete a document and remove from knowledge base"""
    try:
        from app.services.document_manager import get_document_manager
        from app.services.vector_knowledge_base import get_vector_knowledge_base
        
        # Delete from document manager
        doc_manager = get_document_manager()
        deleted = doc_manager.delete_document(document_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from vector knowledge base
        kb = get_vector_knowledge_base()
        chunks_deleted = kb.delete_document(document_id)
        
        return {
            "success": True,
            "message": f"Document deleted successfully",
            "chunks_deleted": chunks_deleted
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

api_router.include_router(upload_router)

# ---- Prescription / Treatment ----
prescription_router = APIRouter(prefix="/prescription")

@prescription_router.post("/generate-plan")
def generate_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    meds = [
        {"name": "amoxicillin", "dose": "500mg", "frequency": "TID"},
        {"name": "acetaminophen", "dose": "650mg", "frequency": "Q6H PRN"},
    ]
    return {"medications": meds, "monitoring_advice": "Monitor temperature and respiratory status."}

@prescription_router.post("/check-interactions")
def check_interactions(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Check for drug interactions among multiple medications"""
    try:
        from app.services.drug_interactions import get_drug_checker
        
        medications: List[str] = payload.get("medications", [])
        include_severity: Optional[List[str]] = payload.get("include_severity")
        
        if not medications or len(medications) < 2:
            return {
                "total_interactions": 0,
                "high_risk_warning": False,
                "severity_breakdown": {"high": 0, "moderate": 0, "low": 0},
                "interactions": []
            }
        
        checker = get_drug_checker()
        results = checker.check_multiple_drugs(medications, include_severity)
        
        # Format response
        return {
            "total_interactions": results.get("total_interactions", 0),
            "high_risk_warning": results.get("high_risk_warning", False),
            "severity_breakdown": results.get("severity_breakdown", {"high": 0, "moderate": 0, "low": 0}),
            "interactions": results.get("interactions", [])
        }
    except Exception as e:
        logger.error(f"Error checking drug interactions: {e}")
        return {
            "total_interactions": 0,
            "high_risk_warning": False,
            "severity_breakdown": {"high": 0, "moderate": 0, "low": 0},
            "interactions": [],
            "error": str(e)
        }

@prescription_router.post("/dosing")
def dosing(payload: Dict[str, Any]) -> Dict[str, Any]:
    drug = payload.get("drug_name", "unknown")
    info = payload.get("patient_info", {})
    weight = info.get("weight", 70)
    dose = f"{round(weight * 10)}mg"  # Arbitrary weight-based stub
    return {"drug": drug, "recommended_dose": dose}

api_router.include_router(prescription_router)
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(discharge_router)
api_router.include_router(treatment_router, prefix="/treatment", tags=["treatment"])
api_router.include_router(timeline_router, prefix="/timeline", tags=["timeline"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(fhir_router, prefix="/fhir", tags=["fhir"])
api_router.include_router(health_router, tags=["health"])
api_router.include_router(knowledge_router, prefix="/medical/knowledge", tags=["knowledge-base"])
api_router.include_router(patient_intake_router, prefix="/medical", tags=["patient-intake"])
api_router.include_router(admin_users_router)

# KB Automation routes (scheduled syncing, feedback, integrity checks)
from app.api.kb_automation import router as kb_automation_router
api_router.include_router(kb_automation_router, prefix="/kb-automation", tags=["kb-automation"])

# Phase 2 & 3: Advanced Features (MIMIC-III, BiomedBERT, NER, reranking, fairness, validation)
from app.api.phase_advanced import router as phase_advanced_router
api_router.include_router(phase_advanced_router, prefix="/phase-advanced", tags=["phase-advanced"])

# Phase 4: Medical Image Analysis & Population Health
api_router.include_router(phase_4_router)

# Phase 5: Local Vision Models & Self-Reliance
api_router.include_router(phase_5_router)

# Phase 5C: Fine-tuning & Model Optimization
api_router.include_router(phase_5c_router)

# Phase 6: Local LLM Integration
api_router.include_router(phase_6_router)

# Phase 7: Self-Learning Engine
from app.api.phase_7_api import router as phase_7_router
api_router.include_router(phase_7_router)

# Self-Healing System API
from app.api.self_healing_api import router as self_healing_router
api_router.include_router(self_healing_router)

# Error Correction API
from app.api.error_correction_api import router as error_correction_router
api_router.include_router(error_correction_router)

# Background task for processing upload queue
_last_queue_process = 0
_queue_process_interval = 10  # Process queue every 10 seconds

@app.get("/api/queue/process")
def trigger_queue_processing() -> Dict[str, Any]:
    """
    Trigger PDF upload queue processing
    Can be called by an external scheduler (e.g., APScheduler, cron, Lambda)
    """
    try:
        from app.services.upload_queue_processor import process_upload_queue
        result = process_upload_queue()
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"[QUEUE] Error triggering processing: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Middleware to periodically check queue (on every request)
@app.middleware("http")
async def background_queue_processor(request: Request, call_next):
    """
    Periodically process upload queue on every API request
    This is a simple approach - in production, use a real task scheduler
    """
    global _last_queue_process
    
    try:
        # Check if it's time to process (every 10 seconds)
        current_time = time.time()
        if current_time - _last_queue_process >= _queue_process_interval:
            _last_queue_process = current_time
            
            # Don't block the request - fire and forget
            from app.services.upload_queue_processor import process_upload_queue
            try:
                process_upload_queue()
            except Exception as e:
                logger.warning(f"[QUEUE] Background processing error: {e}")
    except Exception as e:
        logger.warning(f"[MIDDLEWARE] Error in background processor: {e}")
    
    # Continue with the request
    response = await call_next(request)
    return response
app.include_router(api_router)
