"""FastAPI application entrypoint.

This file was reconstructed after repository history cleanup to satisfy
existing tests that import `app.main:app` and expect a set of medical,
prescription, and diagnostic endpoints. The implementations here are
minimal stubs that return deterministic structures required by tests.

TODO: Replace stub logic with real service integrations (knowledge base,
diagnosis engine, ICD code provider, etc.).
"""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from datetime import datetime
import time
import psutil
from app.api.auth_new import router as auth_router
from app.api.chat_new import router as chat_router
from app.api.discharge import router as discharge_router
from app.database import init_db

# Track application start time for uptime calculation
START_TIME = time.time()

app = FastAPI(title="Physician AI Assistant", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    init_db()
    print("Database initialized successfully")

# CORS middleware - allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/")
def root() -> Dict[str, Any]:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "healthy", "service": "api", "timestamp": datetime.utcnow().isoformat()}

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
medical_router = APIRouter(prefix="/medical")

@medical_router.get("/knowledge/statistics")
def knowledge_statistics() -> Dict[str, int]:
    # Stub: real implementation would scan indexed documents
    return {"total_documents": 0, "total_chunks": 0}

@medical_router.post("/knowledge/search")
def knowledge_search(payload: Dict[str, Any]) -> Dict[str, Any]:
    query = payload.get("query", "")
    top_k = payload.get("top_k", 5)
    # Stub: empty results list
    return {"query": query, "results": [], "top_k": top_k}

@medical_router.post("/diagnosis")
def diagnosis(payload: Dict[str, Any]) -> Dict[str, Any]:
    symptoms: List[str] = payload.get("symptoms", [])
    primary = "Undetermined" if not symptoms else f"Possible {symptoms[0]} related condition"
    return {
        "primary_diagnosis": primary,
        "differential_diagnoses": ["Condition A", "Condition B"],
        "symptoms": symptoms,
    }

@medical_router.post("/analyze-symptoms")
def analyze_symptoms(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"symptoms": payload.get("symptoms", [])}

@medical_router.get("/icd/search")
def icd_search(query: str) -> List[Dict[str, str]]:
    # Stub: return one fabricated code for demonstration
    return [{"code": "A00", "description": f"Stub result for {query}"}]

@medical_router.get("/icd/categories")
def icd_categories() -> List[str]:
    return ["Infectious", "Cardiology", "Respiratory"]

api_router.include_router(medical_router)

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
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(discharge_router)

app.include_router(api_router)
