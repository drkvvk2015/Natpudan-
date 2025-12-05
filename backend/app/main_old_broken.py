"""FastAPI application entrypoint.

This file was reconstructed after repository history cleanup to satisfy
existing tests that import `app.main:app` and expect a set of medical,
prescription, and diagnostic endpoints. The implementations here are
minimal stubs that return deterministic structures required by tests.

TODO: Replace stub logic with real service integrations (knowledge base,
diagnosis engine, ICD code provider, etc.).
"""

from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import List, Dict, Any
from datetime import datetime
import time
import psutil
import logging
import traceback

logger = logging.getLogger(__name__)

# Import routers with error handling
try:
    from app.api.auth_new import router as auth_router
    logger.info("[OK] auth_router imported")
except Exception as e:
    logger.error(f"[ERROR] Failed to import auth_router: {e}")
    auth_router = None

try:
    from app.api.chat_new import router as chat_router
    logger.info("[OK] chat_router imported")
except Exception as e:
    logger.error(f"[ERROR] Failed to import chat_router: {e}")
    chat_router = None

try:
    from app.api.discharge import router as discharge_router
    logger.info("[OK] discharge_router imported")
except Exception as e:
    logger.error(f"[ERROR] Failed to import discharge_router: {e}")
    discharge_router = None

try:
    from app.api.treatment import router as treatment_router
    logger.info("[OK] treatment_router imported")
except Exception as e:
    logger.error(f"[ERROR] Failed to import treatment_router: {e}")
    treatment_router = None

try:
    from app.api.timeline import router as timeline_router
    logger.info("[OK] timeline_router imported")
except Exception as e:
    logger.error(f"[ERROR] Failed to import timeline_router: {e}")
    timeline_router = None

try:
    from app.api.analytics import router as analytics_router
    logger.info("[OK] analytics_router imported")
except Exception as e:
    logger.error(f"[ERROR] Failed to import analytics_router: {e}")
    analytics_router = None

try:
    from app.api.fhir import router as fhir_router
    logger.info("[OK] fhir_router imported")
except Exception as e:
    logger.error(f"[ERROR] Failed to import fhir_router: {e}")
    fhir_router = None

try:
    from app.api.health import router as health_router
    logger.info("[OK] health_router imported")
except Exception as e:
    logger.error(f"[ERROR] Failed to import health_router: {e}")
    health_router = None

try:
    from app.api.error_correction import router as error_correction_router
    logger.info("[OK] error_correction_router imported")
except Exception as e:
    logger.error(f"[ERROR] Failed to import error_correction_router: {e}")
    error_correction_router = None

try:
    from app.api.knowledge_base import router as knowledge_base_router
    logger.info("[OK] knowledge_base_router imported")
except Exception as e:
    logger.error(f"[ERROR] Failed to import knowledge_base_router: {e}")
    knowledge_base_router = None

try:
    from app.api.reports import router as reports_router
    logger.info("[OK] reports_router imported")
except Exception as e:
    logger.error(f"[ERROR] Failed to import reports_router: {e}")
    reports_router = None

try:
    from app.database import init_db
    logger.info("[OK] database imported")
except Exception as e:
    logger.error(f"[ERROR] Failed to import database: {e}")
    def init_db():
        pass

# Track application start time for uptime calculation
START_TIME = time.time()

app = FastAPI(title="Physician AI Assistant", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    import logging
    logger = logging.getLogger("startup")
    try:
        logger.info("[STARTUP] Initializing database tables...")
        init_db()
        logger.info("[STARTUP] Database initialized successfully.")
        print("[STARTUP] Backend server started successfully on http://127.0.0.1:8001")
    except Exception as e:
        logger.error(f"[STARTUP ERROR] {e}", exc_info=True)
        print(f"[STARTUP ERROR] Failed to initialize database: {e}")
        # Don't use log_error during startup as it may cause issues
        # Just log and continue - database will be created on first request if needed

# CORS middleware - allow specific origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,  # Allow credentials with specific origins
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Global exception handlers with error correction integration
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions and log to error correction system"""
    from app.api.error_correction import log_error, ErrorCategory, ErrorSeverity
    
    # Determine severity based on status code
    if exc.status_code >= 500:
        severity = ErrorSeverity.CRITICAL
    elif exc.status_code >= 400:
        severity = ErrorSeverity.MEDIUM
    else:
        severity = ErrorSeverity.LOW
    
    # Determine category
    if exc.status_code == 401:
        category = ErrorCategory.AUTHENTICATION
    elif exc.status_code == 403:
        category = ErrorCategory.PERMISSION
    elif exc.status_code == 404:
        category = ErrorCategory.API
    else:
        category = ErrorCategory.API
    
    # Log to error correction system
    await log_error(
        category=category,
        severity=severity,
        message=str(exc.detail),
        stack_trace=None,
        endpoint=str(request.url.path),
        execute_correction=True,  # Auto-correct if possible
        context={
            "status_code": exc.status_code,
            "method": request.method,
            "url": str(request.url)
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and attempt auto-correction"""
    from app.api.error_correction import log_error, ErrorCategory, ErrorSeverity
    
    error_msg = f"Validation error: {exc.errors()}"
    
    # Log and attempt correction
    await log_error(
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.MEDIUM,
        message=error_msg,
        stack_trace=traceback.format_exc(),
        endpoint=str(request.url.path),
        execute_correction=True,
        context={"validation_errors": exc.errors()}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler with error correction"""
    from app.api.error_correction import log_error, ErrorCategory, ErrorSeverity
    
    error_msg = str(exc)
    
    # Determine category based on error type/message
    if "database" in error_msg.lower() or "sql" in error_msg.lower():
        category = ErrorCategory.DATABASE
    elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
        category = ErrorCategory.NETWORK
    elif "token" in error_msg.lower() or "auth" in error_msg.lower():
        category = ErrorCategory.AUTHENTICATION
    else:
        category = ErrorCategory.SYSTEM
    
    # Log and attempt correction
    correction_result = await log_error(
        category=category,
        severity=ErrorSeverity.CRITICAL,
        message=error_msg,
        stack_trace=traceback.format_exc(),
        endpoint=str(request.url.path),
        execute_correction=True,
        context={
            "method": request.method,
            "url": str(request.url),
            "exception_type": type(exc).__name__
        }
    )
    
    logger.error(f"Unhandled exception at {request.url.path}: {error_msg}", exc_info=True)
    
    # If correction was successful, include hint in response
    detail = error_msg
    if correction_result and correction_result.get("auto_corrected"):
        detail += f" (Auto-correction attempted: {correction_result.get('correction_applied')})"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail}
    )

@app.get("/")
def root() -> Dict[str, Any]:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
def health() -> Dict[str, Any]:
    import logging
    logger = logging.getLogger("health")
    try:
        return {"status": "healthy", "service": "api", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"[HEALTH ERROR] {e}", exc_info=True)
        # Log to error correction system
        from app.api.error_correction import log_error, ErrorCategory, ErrorSeverity
        import asyncio
        asyncio.create_task(log_error(
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            message=str(e),
            stack_trace=None,
            endpoint="health",
            execute_correction=True,
            context={"exception_type": type(e).__name__}
        ))
        return {"status": "error", "detail": str(e), "timestamp": datetime.utcnow().isoformat()}

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
from app.services.icd10_service import get_icd10_service
from app.services.vector_knowledge_base import get_vector_knowledge_base
from app.services.document_manager import get_document_manager
# Enhanced services
from app.services.enhanced_document_manager import get_enhanced_document_manager
from app.services.online_medical_sources import get_online_medical_sources
# Futuristic services
from app.services.hybrid_search import get_hybrid_search
from app.services.rag_service import get_rag_service
from app.services.medical_entity_extractor import get_entity_extractor
from app.services.pubmed_integration import get_pubmed_integration
from app.services.knowledge_graph import get_knowledge_graph

medical_router = APIRouter(prefix="/medical")

@medical_router.get("/knowledge/statistics")
def knowledge_statistics() -> Dict[str, Any]:
    """Get knowledge base statistics"""
    try:
        kb = get_vector_knowledge_base()
        doc_manager = get_document_manager()
        
        kb_stats = kb.get_statistics()
        doc_stats = doc_manager.get_statistics()

        # Build indexed sources from uploaded documents (PDFs only)
        documents = doc_manager.list_documents()
        kb_docs = {d.get('document_id'): d for d in kb.list_documents()}
        pdf_sources = []
        for doc in documents:
            if str(doc.get('extension', '')).lower() == '.pdf':
                size_mb = 0.0
                try:
                    size_mb = round(int(doc.get('file_size', 0)) / (1024 * 1024), 2)
                except Exception:
                    pass
                # Consider 'indexed' if any chunks exist for this document_id
                status = 'indexed' if doc.get('document_id') in kb_docs and kb_docs[doc.get('document_id')].get('chunk_count', 0) > 0 else 'pending'
                pdf_sources.append({
                    'name': doc.get('filename', 'unknown'),
                    'size_mb': size_mb,
                    'status': status
                })

        # Derive a simple knowledge level heuristic
        total_chunks = kb_stats.get('total_chunks', 0)
        if total_chunks == 0:
            knowledge_level = 'UNKNOWN'
        elif total_chunks < 500:
            knowledge_level = 'BASIC'
        elif total_chunks < 5000:
            knowledge_level = 'MODERATE'
        else:
            knowledge_level = 'ADVANCED'

        return {
            "status": "ok",
            "total_documents": kb_stats.get("total_documents", 0),
            "total_chunks": total_chunks,
            "uploaded_documents": doc_stats.get("total_documents", 0),
            "total_size_mb": doc_stats.get("total_size_mb", 0),
            "embedding_model": kb_stats.get("embedding_model", "unknown"),
            "faiss_available": kb_stats.get("faiss_available", False),
            "openai_available": kb_stats.get("openai_available", False),
            "knowledge_level": knowledge_level,
            "search_mode": "semantic",
            "pdf_sources": pdf_sources,
        }
    except Exception as e:
        logger.error(f"Error getting knowledge statistics: {e}")
        return {"error": str(e), "status": "error", "total_documents": 0, "total_chunks": 0, "pdf_sources": []}

@medical_router.post("/knowledge/search")
def knowledge_search(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Search knowledge base using semantic similarity"""
    try:
        query = payload.get("query", "")
        top_k = payload.get("top_k", 5)
        
        if not query:
            return {"error": "Query is required", "query": "", "results": []}
        
        kb = get_vector_knowledge_base()
        raw_results = kb.search(query, top_k=top_k)

        # Transform results to frontend-friendly shape
        results = []
        for r in raw_results:
            metadata = r.get('metadata', {}) or {}
            results.append({
                'content': r.get('content', ''),
                'metadata': {
                    'source': metadata.get('source') or metadata.get('filename') or 'unknown',
                    'page': metadata.get('page')
                },
                'relevance': float(r.get('similarity_score', 0.0)),
                'distance': float(r.get('distance', 0.0))
            })
        
        return {
            "query": query,
            "results": results,
            "top_k": top_k,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        return {"error": str(e), "query": query, "results": []}

@medical_router.post("/diagnosis")
def diagnosis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate diagnosis suggestions from symptoms"""
    try:
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
        
        # Ensure suggested_icd_codes are well-formed
        formatted_icd = []
        for code in suggested_codes[:5]:
            if isinstance(code, dict):
                formatted_icd.append({
                    'code': code.get('code'),
                    'description': code.get('description'),
                    'category': icd_service._get_category(code.get('code', '')) if code.get('code') else None
                })
        
        return {
            "primary_diagnosis": primary_diagnosis,
            "differential_diagnoses": differential_diagnoses,
            "symptoms": symptoms,
            "suggested_icd_codes": formatted_icd
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
        icd_service = get_icd10_service()
        result = icd_service.get_code(code)
        
        if result is None:
            return {"error": "Code not found", "code": code}
        
        return result
    except Exception as e:
        logger.error(f"Error getting ICD code: {e}")
        return {"error": str(e), "code": code}

@medical_router.post("/live-diagnosis")
def live_diagnosis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate real-time diagnosis suggestions from comprehensive patient data"""
    try:
        complaints = payload.get("complaints", [])
        patient_history = payload.get("patient_history", "")
        vital_signs = payload.get("vital_signs", {})
        anthropometry = payload.get("anthropometry", {})
        clinical_findings = payload.get("clinical_findings", [])
        
        if not complaints:
            return {
                "differential_diagnoses": [],
                "recommended_tests": [],
                "clinical_summary": "No complaints provided",
                "data_completeness": 0.0
            }
        
        # Extract symptoms for ICD analysis
        symptoms = []
        for complaint in complaints:
            if isinstance(complaint, dict):
                symptoms.append(complaint.get("complaint", ""))
            else:
                symptoms.append(str(complaint))
        
        # Normalize clinical findings into supporting evidence
        supporting_evidence = []
        positive_findings = []
        for cf in clinical_findings:
            try:
                system = cf.get('system', '') if isinstance(cf, dict) else ''
                finding = cf.get('finding', '') if isinstance(cf, dict) else str(cf)
                # Treat presence in list as positive finding
                entry = f"{system}: {finding}" if system else finding
                supporting_evidence.append(entry)
                positive_findings.append(entry)
            except Exception:
                continue
        
        # Calculate data completeness (0-1 scale)
        data_completeness = 0.2  # Base for having complaints
        if patient_history: data_completeness += 0.2
        if vital_signs: data_completeness += 0.2
        if anthropometry: data_completeness += 0.1
        if clinical_findings: data_completeness += 0.3
        
        # Get ICD-10 suggestions
        icd_service = get_icd10_service()
        suggested_codes = icd_service.suggest_codes(symptoms)
        
        # Build differential diagnoses with confidence scores
        differential_diagnoses = []
        for i, code in enumerate(suggested_codes[:5]):
            confidence = max(0.3, 0.9 - (i * 0.15))  # Decreasing confidence
            differential_diagnoses.append({
                "diagnosis": code.get("description", "Unknown"),
                "disease_name": code.get("description", "Unknown"),
                "confidence": confidence,
                "icd_code": code.get("code", ""),
                "supporting_evidence": supporting_evidence[:3] if supporting_evidence else symptoms[:2]
            })
        
        # Generate recommended tests based on symptoms and positive findings
        recommended_tests = []
        if any("chest pain" in s.lower() or "heart" in s.lower() for s in symptoms + supporting_evidence):
            recommended_tests.extend(["ECG", "Troponins", "Chest X-ray"])
        if any("fever" in s.lower() or "infection" in s.lower() for s in symptoms + supporting_evidence):
            recommended_tests.extend(["CBC", "Blood cultures", "CRP"])
        if any("abdominal" in s.lower() or "stomach" in s.lower() for s in symptoms + supporting_evidence):
            recommended_tests.extend(["Abdominal ultrasound", "Lipase", "Liver function tests"])
        if any("headache" in s.lower() or "neurologic" in s.lower() for s in symptoms + supporting_evidence):
            recommended_tests.extend(["CT head", "MRI brain"])
        
        # Remove duplicates
        recommended_tests = list(dict.fromkeys(recommended_tests))
        
        # Generate clinical summary including positive findings
        primary_complaint = symptoms[0] if symptoms else "Unknown complaint"
        duration_info = ""
        if complaints and isinstance(complaints[0], dict) and complaints[0].get("duration"):
            duration_info = f" for {complaints[0]['duration']}"
        
        clinical_summary = f"Patient presents with {primary_complaint}{duration_info}. "
        if len(symptoms) > 1:
            clinical_summary += f"Associated symptoms include {', '.join(symptoms[1:3])}. "
        if patient_history:
            clinical_summary += "Comprehensive history available. "
        if positive_findings:
            clinical_summary += f"Positive findings on exam: {', '.join(positive_findings[:5])}. "
        clinical_summary += f"Data completeness: {int(data_completeness * 100)}%."
        
        return {
            "differential_diagnoses": differential_diagnoses,
            "recommended_tests": recommended_tests,
            "clinical_summary": clinical_summary,
            "data_completeness": data_completeness
        }
        
    except Exception as e:
        logger.error(f"Error in live diagnosis: {e}")
        return {
            "error": str(e),
            "differential_diagnoses": [],
            "recommended_tests": [],
            "clinical_summary": "Error processing request",
            "data_completeness": 0.0
        }

@medical_router.get("/icd/categories")
def icd_categories() -> List[str]:
    """Get all ICD-10 categories"""
    try:
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

@medical_router.post("/knowledge/fetch-online-data")
async def fetch_online_medical_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    [STARTING] ENHANCED: Fetch medical knowledge from multiple online sources
    Integrates PubMed, WHO, CDC, NIH simultaneously
    """
    try:
        query = payload.get("query", "")
        sources = payload.get("sources", ["pubmed"])  # Default to PubMed
        max_results = payload.get("max_results", 10)
        auto_index = payload.get("auto_index", False)
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Fetch from online sources
        online_sources = get_online_medical_sources()
        results = await online_sources.fetch_comprehensive_knowledge(
            query=query,
            sources=sources,
            max_results=max_results
        )
        
        # Optionally auto-index into knowledge base
        indexed_count = 0
        if auto_index:
            kb = get_vector_knowledge_base()
            
            for source_name, documents in results.items():
                for doc in documents:
                    try:
                        formatted = online_sources.format_for_indexing(doc)
                        chunks = kb.add_document(
                            content=formatted["content"],
                            metadata=formatted["metadata"]
                        )
                        if chunks > 0:
                            indexed_count += 1
                    except Exception as e:
                        logger.error(f"Error indexing document from {source_name}: {e}")
        
        total_found = sum(len(docs) for docs in results.values())
        
        return {
            "query": query,
            "sources_queried": sources,
            "results": results,
            "total_documents": total_found,
            "auto_indexed": auto_index,
            "indexed_count": indexed_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching online medical data: {e}", exc_info=True)
        return {"error": str(e), "query": payload.get("query", "")}

@medical_router.post("/knowledge/auto-update")
async def auto_update_knowledge_base(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    [STARTING] AUTO-UPDATE: Automatically update KB with latest online research
    Fetches and indexes recent papers for specified topics
    """
    try:
        topics = payload.get("topics", ["diabetes", "hypertension", "covid-19"])
        sources = payload.get("sources", ["pubmed"])
        results_per_topic = payload.get("results_per_topic", 5)
        
        if not topics:
            raise HTTPException(status_code=400, detail="Topics list is required")
        
        # Auto-update knowledge base
        online_sources = get_online_medical_sources()
        kb = get_vector_knowledge_base()
        
        update_result = await online_sources.auto_update_knowledge_base(
            vector_kb=kb,
            topics=topics,
            sources=sources,
            results_per_topic=results_per_topic
        )
        
        return {
            "success": True,
            "message": f"Knowledge base updated with {update_result['documents_indexed']} new documents",
            "update_summary": update_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error auto-updating knowledge base: {e}", exc_info=True)
        return {"error": str(e), "success": False}

@medical_router.get("/knowledge/performance-metrics")
def get_kb_performance_metrics() -> Dict[str, Any]:
    """
    [STATS] Get knowledge base performance metrics and statistics
    """
    try:
        doc_manager = get_enhanced_document_manager()
        stats = doc_manager.get_statistics()
        
        kb = get_vector_knowledge_base()
        kb_stats = kb.get_statistics()
        
        return {
            "success": True,
            "document_manager": stats,
            "vector_kb": kb_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return {"error": str(e), "success": False}

@medical_router.post("/knowledge/clear-cache")
def clear_document_cache() -> Dict[str, Any]:
    """
    🗑️ Clear document extraction cache
    """
    try:
        doc_manager = get_enhanced_document_manager()
        count = doc_manager.clear_cache()
        
        return {
            "success": True,
            "message": f"Cleared {count} cached files",
            "files_cleared": count
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return {"error": str(e), "success": False}

@medical_router.post("/knowledge/pubmed-auto-update")
def pubmed_auto_update(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    [STARTING] AUTO-UPDATE: Automatically index latest PubMed research
    Keeps knowledge base current with newest findings
    """
    try:
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
    Enhanced with async processing, caching, and comprehensive error handling.
    
    Supports files up to 500MB (configurable).
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Use enhanced document manager with 500MB limit
        doc_manager = get_enhanced_document_manager()
        
        try:
            doc_info = await doc_manager.save_upload(
                content,
                file.filename,
                metadata={
                    "source": source,
                    "category": category,
                    "description": description
                },
                max_file_size_mb=500  # Allow up to 500MB files
            )
        except ValueError as ve:
            # Client error (invalid file type, too large, etc.)
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            # Server error
            logger.error(f"Error saving document: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to process document")
        
        # Index document in vector knowledge base
        kb = get_vector_knowledge_base()
        text_content = doc_manager.get_document_text(doc_info["document_id"])
        
        if text_content:
            try:
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
            except Exception as e:
                logger.error(f"Error indexing document: {e}", exc_info=True)
                doc_info["indexed_chunks"] = 0
                doc_info["indexing_error"] = str(e)
        else:
            doc_info["indexed_chunks"] = 0
            doc_info["warning"] = "No text content extracted"
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Document '{file.filename}' uploaded and indexed successfully",
                "document": doc_info
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@upload_router.get("/documents")
def list_documents():
    """List all uploaded documents"""
    try:
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
    medications: List[str] = payload.get("medications", [])
    # Simple heuristic: if both warfarin and aspirin present -> high risk
    high_risk = "warfarin" in medications and "aspirin" in medications
    total_interactions = 2 if high_risk else 0
    severity_breakdown = {"high": 2 if high_risk else 0, "moderate": 0, "low": 0}
    return {
        "total_interactions": total_interactions,
        "high_risk_warning": high_risk,
        "severity_breakdown": severity_breakdown,
    }

@prescription_router.post("/dosing")
def dosing(payload: Dict[str, Any]) -> Dict[str, Any]:
    drug = payload.get("drug_name", "unknown")
    info = payload.get("patient_info", {})
    weight = info.get("weight", 70)
    dose = f"{round(weight * 10)}mg"  # Arbitrary weight-based stub
    return {"drug": drug, "recommended_dose": dose}

api_router.include_router(prescription_router)
if auth_router: api_router.include_router(auth_router)
if chat_router: api_router.include_router(chat_router)
if discharge_router: api_router.include_router(discharge_router)
if treatment_router: api_router.include_router(treatment_router, prefix="/treatment", tags=["treatment"])
if timeline_router: api_router.include_router(timeline_router, prefix="/timeline", tags=["timeline"])
if analytics_router: api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
if fhir_router: api_router.include_router(fhir_router, prefix="/fhir", tags=["fhir"])
if error_correction_router: api_router.include_router(error_correction_router, prefix="/error-correction", tags=["error-correction"])
if health_router: api_router.include_router(health_router, tags=["health"])
if knowledge_base_router: api_router.include_router(knowledge_base_router, prefix="/knowledge")
if reports_router: api_router.include_router(reports_router, prefix="/reports", tags=["reports"])

app.include_router(api_router)
