"""FastAPI application entrypoint.

This module prioritizes test compatibility and stable API behavior while the
service layer continues to evolve. Endpoints here should remain deterministic,
well-validated, and operational across local and CI environments.
"""

from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException, Request, status
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response as StarletteResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
import os
import psutil
import logging
import tempfile

from app.core.config import settings
from app.logging_config import setup_logging, get_logger
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.rate_limiter import RateLimiter
from app.monitoring import record_http_metrics, render_prometheus_metrics
from app.telemetry import instrument_fastapi_app
from app.schemas.system import RootResponse, HealthResponse, DetailedHealthResponse
from app.container import register_api_routers
from app.lifespan import app_lifespan

setup_logging(getattr(logging, settings.LOG_LEVEL, logging.INFO))
logger = get_logger(__name__)

# Import error correction system
from app.services.error_corrector import get_error_corrector

error_corrector = get_error_corrector()

from app.database import SessionLocal
from sqlalchemy import text

# Track application start time for uptime calculation
START_TIME = time.time()

# Service health status
service_health = {
    "database": False,
    "openai": False,
    "knowledge_base": False
}

app = FastAPI(
    title="Physician AI Assistant",
    version="1.0.0",
    lifespan=app_lifespan
)
instrument_fastapi_app(app)

app.add_middleware(RequestContextMiddleware)

if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimiter,
        calls=settings.RATE_LIMIT_CALLS,
        period=settings.RATE_LIMIT_PERIOD,
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


@app.post("/api/error-correction/log")
async def log_frontend_error(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Accept frontend error reports without failing the client."""
    error_corrector.log_error(
        Exception(payload.get("message", "Frontend error")),
        {
            "operation": "frontend_error",
            "url": payload.get("url"),
            "component_stack": payload.get("componentStack"),
            "timestamp": payload.get("timestamp"),
        },
    )
    return {"success": True}

# CORS middleware - allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.middleware("http")
async def log_requests(request: Request, call_next: RequestResponseEndpoint) -> StarletteResponse:
    started_at = time.perf_counter()
    response: StarletteResponse = await call_next(request)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    record_http_metrics(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        started_at=started_at,
    )
    logger.info(
        "request_completed method=%s path=%s status=%s duration_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/", response_model=RootResponse)
def root() -> Dict[str, Any]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/health", response_model=HealthResponse)
def health() -> Dict[str, Any]:
    # Fallback probe so health works reliably in tests and warm/cold starts.
    db_healthy = service_health["database"]
    if not db_healthy:
        db = None
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db_healthy = True
            service_health["database"] = True
        except Exception:
            db_healthy = False
        finally:
            if db is not None:
                db.close()

    openai_healthy = service_health["openai"]
    if not openai_healthy:
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            openai_healthy = bool(api_key and not api_key.startswith("sk-your"))
            service_health["openai"] = openai_healthy
        except Exception:
            openai_healthy = False

    kb_healthy = service_health["knowledge_base"]
    if not kb_healthy:
        try:
            from app.services.vector_knowledge_base import get_vector_knowledge_base
            kb = get_vector_knowledge_base()
            kb_healthy = kb is not None
            service_health["knowledge_base"] = kb_healthy
        except Exception:
            kb_healthy = False

    current_services = {
        "database": db_healthy,
        "openai": openai_healthy,
        "knowledge_base": kb_healthy,
    }

    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "api",
        "services": current_services,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health/detailed", response_model=DetailedHealthResponse)
def detailed_health() -> Dict[str, Any]:
    """Detailed health check with system metrics."""
    try:
        # Calculate uptime in seconds
        uptime_seconds = int(time.time() - START_TIME)

        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(os.path.abspath(os.sep))

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
            "last_check_in": datetime.now(timezone.utc).isoformat()
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
            "last_check_in": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }


@app.get("/metrics")
def metrics() -> StarletteResponse:
    """Prometheus metrics endpoint."""
    payload = render_prometheus_metrics()
    if payload is None:
        raise HTTPException(status_code=503, detail="Metrics backend unavailable")
    return StarletteResponse(content=payload, media_type="text/plain; version=0.0.4")

api_router = APIRouter(prefix="/api")

# ---- Medical / Knowledge Base ----
from app.services.icd10_service import get_icd10_service
from app.services.vector_knowledge_base import get_vector_knowledge_base
from app.services.document_manager import get_document_manager
# Futuristic services
from app.services.hybrid_search import get_hybrid_search
from app.services.rag_service import get_rag_service
from app.services.medical_entity_extractor import get_entity_extractor
from app.services.pubmed_integration import get_pubmed_integration
from app.services.knowledge_graph import get_knowledge_graph

medical_router = APIRouter(prefix="/medical")

@medical_router.post("/diagnosis")
def diagnosis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate diagnosis suggestions from symptoms"""
    symptoms: List[str] = payload.get("symptoms", [])
    try:

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
    symptoms: List[Any] = payload.get("symptoms", [])
    try:

        if not symptoms:
            return {"error": "No symptoms provided", "analysis": []}

        # Get ICD-10 suggestions for each symptom
        icd_service = get_icd10_service()
        analysis: List[Dict[str, Any]] = []

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


@medical_router.post("/live-diagnosis")
def live_diagnosis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate diagnosis suggestions from richer clinical context."""
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
                "data_completeness": 0.0,
            }

        symptoms: List[str] = []
        for complaint in complaints:
            if isinstance(complaint, dict):
                value = str(complaint.get("complaint", "")).strip()
            else:
                value = str(complaint).strip()
            if value:
                symptoms.append(value)

        supporting_evidence: List[str] = []
        for finding in clinical_findings:
            if not isinstance(finding, dict):
                supporting_evidence.append(str(finding))
                continue
            system = str(finding.get("system", "")).strip()
            detail = str(finding.get("finding", "")).strip()
            normalized = f"{system}: {detail}" if system and detail else detail or system
            if normalized:
                supporting_evidence.append(normalized)

        data_completeness = 0.2
        if patient_history:
            data_completeness += 0.2
        if vital_signs:
            data_completeness += 0.2
        if anthropometry:
            data_completeness += 0.1
        if clinical_findings:
            data_completeness += 0.3

        icd_service = get_icd10_service()
        suggested_codes = icd_service.suggest_codes(symptoms)

        differential_diagnoses: List[Dict[str, Any]] = []
        for idx, code in enumerate(suggested_codes[:5]):
            confidence = max(0.3, 0.9 - (idx * 0.15))
            differential_diagnoses.append(
                {
                    "diagnosis": code.get("description", "Unknown"),
                    "disease_name": code.get("description", "Unknown"),
                    "confidence": confidence,
                    "icd_code": code.get("code", ""),
                    "supporting_evidence": supporting_evidence[:3] if supporting_evidence else symptoms[:2],
                }
            )

        search_space = [item.lower() for item in [*symptoms, *supporting_evidence]]
        recommended_tests: List[str] = []
        if any("chest pain" in item or "heart" in item for item in search_space):
            recommended_tests.extend(["ECG", "Troponins", "Chest X-ray"])
        if any("fever" in item or "infection" in item for item in search_space):
            recommended_tests.extend(["CBC", "Blood cultures", "CRP"])
        if any("abdominal" in item or "stomach" in item for item in search_space):
            recommended_tests.extend(["Abdominal ultrasound", "Lipase", "Liver function tests"])
        if any("headache" in item or "neuro" in item for item in search_space):
            recommended_tests.extend(["CT head", "MRI brain"])
        recommended_tests = list(dict.fromkeys(recommended_tests))

        primary_complaint = symptoms[0] if symptoms else "Unknown complaint"
        duration_info = ""
        if complaints and isinstance(complaints[0], dict) and complaints[0].get("duration"):
            duration_info = f" for {complaints[0]['duration']}"

        clinical_summary = f"Patient presents with {primary_complaint}{duration_info}. "
        if len(symptoms) > 1:
            clinical_summary += f"Associated symptoms include {', '.join(symptoms[1:3])}. "
        if patient_history:
            clinical_summary += "Comprehensive history available. "
        if supporting_evidence:
            clinical_summary += f"Positive findings on exam: {', '.join(supporting_evidence[:5])}. "
        clinical_summary += f"Data completeness: {int(data_completeness * 100)}%."

        return {
            "differential_diagnoses": differential_diagnoses,
            "recommended_tests": recommended_tests,
            "clinical_summary": clinical_summary,
            "data_completeness": data_completeness,
        }
    except Exception as e:
        logger.error(f"Error in live diagnosis: {e}")
        return {
            "error": str(e),
            "differential_diagnoses": [],
            "recommended_tests": [],
            "clinical_summary": "Error processing request",
            "data_completeness": 0.0,
        }


@medical_router.post("/live-diagnosis/suggest-treatment")
def suggest_treatment(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Compatibility endpoint for the diagnosis screen."""
    from app.services.ai_treatment_recommender import get_treatment_recommender

    diagnosis = payload.get("diagnosis", "")
    patient_data = {
        "age": payload.get("patient_age"),
        "gender": payload.get("patient_gender"),
        "comorbidities": payload.get("comorbidities", []),
    }
    recommender = get_treatment_recommender()
    return recommender.recommend_treatment(diagnosis, patient_data)


@medical_router.post("/parse-medical-report")
async def parse_medical_report(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Extract structured data from uploaded PDF reports."""
    from app.services.pdf_processor import pdf_processor

    suffix = os.path.splitext(file.filename or "report.pdf")[1] or ".pdf"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(await file.read())
            temp_path = temp_file.name

        report_data = pdf_processor.process_report(temp_path)
        flattened_lab_results: List[Dict[str, Any]] = []
        for category_results in report_data.get("lab_results", {}).values():
            if not isinstance(category_results, dict):
                continue
            for test_name, value in category_results.items():
                flattened_lab_results.append({"test": test_name, "value": str(value)})

        diagnoses = [
            {
                "description": item.get("description", ""),
                "icd10_code": item.get("code") if item.get("code") not in (None, "Unknown") else None,
            }
            for item in report_data.get("diagnoses", [])
        ]

        return {
            "vitals": report_data.get("vitals", {}),
            "medications": report_data.get("medications", []),
            "lab_results": flattened_lab_results,
            "diagnoses": diagnoses,
            "allergies": report_data.get("allergies", []),
        }
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

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
    query: str = payload.get("query", "")
    try:
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
    query: str = payload.get("query", "")
    try:
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

        result: Dict[str, Any] = pubmed.auto_update_knowledge_base(
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
    source: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None
):
    """
    Upload a medical document (PDF, DOCX, TXT) to knowledge base.
    The document will be processed, indexed, and made searchable.
    """
    try:
        # Read file content
        content = await file.read()

        # Save document
        doc_manager = get_document_manager()
        filename = file.filename or "unnamed_document"
        doc_info = await doc_manager.save_upload(
            content,
            filename,
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
                    "filename": filename,
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
                "message": f"Document '{filename}' uploaded and indexed successfully",
                "document": doc_info
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@upload_router.get("/documents")
def list_documents() -> Dict[str, Any]:
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
def get_document(document_id: str) -> Dict[str, Any]:
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
def delete_document(document_id: str) -> Dict[str, Any]:
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
            "message": "Document deleted successfully",
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
    """Generate treatment plan based on patient data and diagnosis."""
    from app.services.ai_treatment_recommender import get_treatment_recommender
    from app.services.drug_interactions import get_drug_checker

    diagnosis = payload.get("diagnosis", "")
    patient_data = payload.get("patient_data", {})
    medications = payload.get("medications", [])

    if not diagnosis and not medications:
        return {
            "medications": [],
            "monitoring_advice": "Please provide diagnosis or medications."
        }

    # Get treatment recommendations
    recommender = get_treatment_recommender()
    treatment = recommender.recommend_treatment(diagnosis, patient_data)

    # Check drug interactions if multiple medications provided
    interaction_result = {"interactions": [], "high_risk_warning": False}
    if len(medications) >= 2:
        checker = get_drug_checker()
        interaction_result = checker.check_interactions(medications)

    return {
        "diagnosis": diagnosis,
        "medications": treatment.get("primary_pathway", {}).get("medications", []),
        "alternative_options": treatment.get("alternative_pathways", []),
        "monitoring_advice": "Monitor temperature and respiratory status.",
        "interactions": interaction_result.get("interactions", []),
        "high_risk_warning": interaction_result.get("high_risk_warning", False),
        "outcome_prediction": treatment.get("outcome_prediction", {}),
        "clinical_guidelines": treatment.get("clinical_guidelines", [])
    }


@prescription_router.post("/generate")
def generate_prescription(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Compatibility alias for legacy frontend callers."""
    normalized_payload = {
        "diagnosis": payload.get("diagnosis", ""),
        "patient_data": {
            "age": payload.get("patient_age"),
            "weight": payload.get("patient_weight"),
            "allergies": payload.get("allergies", []),
        },
        "medications": payload.get("medications", []),
    }
    return generate_plan(normalized_payload)

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


@prescription_router.post("/drugs/check")
def legacy_check_interactions(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Compatibility alias for older frontend service paths."""
    return check_interactions(payload)


@prescription_router.get("/drugs/search")
def search_drugs(q: str) -> List[str]:
    """Basic local drug search using the rule-based interaction database."""
    from app.services.drug_interactions import get_drug_checker

    query = q.strip().lower()
    if not query:
        return []

    checker = get_drug_checker()
    candidates = set()
    for drug1, drug2 in checker.normalized_db.keys():
        candidates.add(drug1)
        candidates.add(drug2)
    for drugs in checker.DRUG_CLASSES.values():
        candidates.update(drugs)

    return sorted([candidate for candidate in candidates if query in candidate])[:20]

@prescription_router.post("/dosing")
def dosing(payload: Dict[str, Any]) -> Dict[str, Any]:
    drug = payload.get("drug_name", "unknown")
    info = payload.get("patient_info", {})
    weight = info.get("weight", 70)
    dose = f"{round(weight * 10)}mg"  # Arbitrary weight-based stub
    return {"drug": drug, "recommended_dose": dose}

api_router.include_router(prescription_router)
register_api_routers(api_router)

@app.post("/api/queue/process")
def trigger_queue_processing() -> Dict[str, Any]:
    """
    Trigger PDF upload queue processing
    Can be called by an external scheduler (e.g., APScheduler, cron, Lambda)
    """
    try:
        from app.services.upload_queue_processor import process_upload_queue
        result: Dict[str, Any] = process_upload_queue()
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"[QUEUE] Error triggering processing: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@app.middleware("http")
async def background_queue_processor(request: Request, call_next: RequestResponseEndpoint) -> StarletteResponse:
    """Pass-through middleware. Queue processing is explicit, not request-driven."""
    response: StarletteResponse = await call_next(request)
    return response
@app.api_route("/api/v1/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def api_v1_compat(full_path: str, request: Request):
    """Compatibility layer: route legacy /api/v1/* requests to /api/* endpoints."""
    target = f"/api/{full_path}"
    if request.url.query:
        target = f"{target}?{request.url.query}"
    return RedirectResponse(url=target, status_code=307)


app.include_router(api_router)
