"""
Phase 7 API: Self-Learning Engine

API endpoints for the self-learning system:
- Data collection management
- Training job scheduling
- Model deployment
- Performance monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from ..database import get_db
from ..database.models import (
    ValidatedCase,
    ValidationStatus,
    ModelPerformance,
    TrainingJob,
    TrainingJobStatus,
    ModelType,
    User
)
from ..services.phase_7_services.data_collector import DataCollector

# No /api prefix here - it's already in main.py's api_router
router = APIRouter(prefix="/phase-7", tags=["Phase 7 - Self-Learning"])
logger = logging.getLogger(__name__)


# ========================================
# PYDANTIC MODELS
# ========================================

class CollectionStatsResponse(BaseModel):
    """Collection statistics response"""
    total_cases: int
    validated_cases: int
    pending_cases: int
    anonymized_cases: int
    used_in_training: int
    average_quality_score: float
    collection_rate: float


class CaseCollectionRequest(BaseModel):
    """Request to collect cases"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)
    min_confidence: int = Field(80, ge=0, le=100)


class ValidatedCaseResponse(BaseModel):
    """Validated case response"""
    id: int
    case_id: str
    diagnosis: str
    diagnosis_confidence: Optional[int]
    validation_status: str
    data_quality_score: Optional[int]
    is_anonymized: bool
    used_in_training: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TrainingJobResponse(BaseModel):
    """Training job response"""
    id: int
    job_id: str
    model_type: str
    model_version: str
    status: str
    progress_percentage: int
    dataset_size: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    final_accuracy: Optional[int]
    
    class Config:
        from_attributes = True


class ModelPerformanceResponse(BaseModel):
    """Model performance response"""
    id: int
    model_version: str
    model_type: str
    accuracy: Optional[int]
    precision: Optional[int]
    recall: Optional[int]
    f1_score: Optional[int]
    is_active: bool
    deployed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ========================================
# HEALTH CHECK
# ========================================

@router.get("/health")
async def phase_7_health():
    """Health check for Phase 7 services"""
    return {
        "status": "operational",
        "phase": "7 - Self-Learning Engine",
        "features": [
            "Data collection from validated cases",
            "HIPAA anonymization",
            "Quality filtering and scoring",
            "Training job management (ready)",
            "Model performance tracking",
            "A/B testing framework (ready)",
            "Auto-deployment system (ready)"
        ],
        "message": "Phase 7 foundation ready - Day 1 complete!",
        "version": "1.0.0"
    }


# ========================================
# DATA COLLECTION ENDPOINTS
# ========================================

@router.get("/cases/statistics", response_model=CollectionStatsResponse)
async def get_collection_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about collected cases
    
    Returns:
        - Total cases collected
        - Validated vs pending
        - Anonymization status
        - Quality scores
        - Training usage
    """
    try:
        collector = DataCollector(db)
        stats = collector.get_collection_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting collection statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cases/collect")
async def collect_cases(
    request: CaseCollectionRequest,
    db: Session = Depends(get_db)
):
    """
    Manually trigger case collection from treatment plans
    
    Collects completed treatment plans and creates ValidatedCase entries.
    """
    try:
        collector = DataCollector(db, min_confidence=request.min_confidence)
        
        # Collect from treatment plans
        collected = collector.collect_from_treatment_plans(
            min_treatment_duration_days=7,
            limit=request.limit
        )
        
        return {
            "status": "success",
            "collected_count": collected,
            "message": f"Collected {collected} new cases from treatment plans"
        }
    except Exception as e:
        logger.error(f"Error collecting cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cases", response_model=List[ValidatedCaseResponse])
async def list_cases(
    status: Optional[str] = Query(None, description="Filter by validation status"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List collected cases
    
    Query parameters:
        - status: Filter by validation status (pending, validated, rejected)
        - limit: Maximum number of cases to return
        - offset: Pagination offset
    """
    try:
        query = db.query(ValidatedCase)
        
        if status:
            query = query.filter(ValidatedCase.validation_status == status)
        
        query = query.order_by(ValidatedCase.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        cases = query.all()
        return cases
    except Exception as e:
        logger.error(f"Error listing cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cases/{case_id}", response_model=ValidatedCaseResponse)
async def get_case(case_id: str, db: Session = Depends(get_db)):
    """Get details of a specific case"""
    try:
        case = db.query(ValidatedCase).filter(
            ValidatedCase.case_id == case_id
        ).first()
        
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        return case
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting case: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cases/{case_id}/anonymize")
async def anonymize_case(case_id: str, db: Session = Depends(get_db)):
    """
    Anonymize a case for HIPAA compliance
    
    Removes all personally identifiable information:
    - Names, dates of birth
    - Addresses, phone numbers
    - Email addresses
    - Medical record numbers
    """
    try:
        collector = DataCollector(db)
        
        case = db.query(ValidatedCase).filter(
            ValidatedCase.case_id == case_id
        ).first()
        
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        anonymized_case = collector.anonymize_case(case)
        
        return {
            "status": "success",
            "case_id": case_id,
            "is_anonymized": anonymized_case.is_anonymized,
            "anonymization_date": anonymized_case.anonymization_date,
            "message": "Case anonymized successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error anonymizing case: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cases/{case_id}/validate")
async def validate_case(
    case_id: str,
    validation_status: ValidationStatus,
    validation_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Validate a case (approve/reject for training)
    
    Body parameters:
        - validation_status: validated, rejected, needs_review
        - validation_notes: Optional notes about validation decision
    """
    try:
        case = db.query(ValidatedCase).filter(
            ValidatedCase.case_id == case_id
        ).first()
        
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        case.validation_status = validation_status.value
        case.validated_at = datetime.utcnow()
        case.validation_notes = validation_notes
        
        db.commit()
        
        return {
            "status": "success",
            "case_id": case_id,
            "validation_status": validation_status.value,
            "message": f"Case marked as {validation_status.value}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating case: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# TRAINING JOB ENDPOINTS (FOUNDATION)
# ========================================

@router.get("/training/jobs", response_model=List[TrainingJobResponse])
async def list_training_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    List training jobs
    
    Query parameters:
        - status: Filter by job status (queued, running, completed, failed)
        - limit: Maximum number of jobs to return
    """
    try:
        query = db.query(TrainingJob)
        
        if status:
            query = query.filter(TrainingJob.status == status)
        
        query = query.order_by(TrainingJob.created_at.desc()).limit(limit)
        jobs = query.all()
        
        return jobs
    except Exception as e:
        logger.error(f"Error listing training jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training/jobs/{job_id}", response_model=TrainingJobResponse)
async def get_training_job(job_id: str, db: Session = Depends(get_db)):
    """Get details of a specific training job"""
    try:
        job = db.query(TrainingJob).filter(
            TrainingJob.job_id == job_id
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Training job not found")
        
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting training job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# MODEL PERFORMANCE ENDPOINTS
# ========================================

@router.get("/models/performance", response_model=List[ModelPerformanceResponse])
async def list_model_performance(
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List model performance metrics
    
    Query parameters:
        - model_type: Filter by model type (medsam, llm, diagnosis)
        - is_active: Filter by deployment status
        - limit: Maximum number of records to return
    """
    try:
        query = db.query(ModelPerformance)
        
        if model_type:
            query = query.filter(ModelPerformance.model_type == model_type)
        if is_active is not None:
            query = query.filter(ModelPerformance.is_active == is_active)
        
        query = query.order_by(ModelPerformance.created_at.desc()).limit(limit)
        performances = query.all()
        
        return performances
    except Exception as e:
        logger.error(f"Error listing model performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/current")
async def get_current_model(
    model_type: str = Query("diagnosis", description="Model type"),
    db: Session = Depends(get_db)
):
    """Get currently active model version"""
    try:
        current_model = db.query(ModelPerformance).filter(
            ModelPerformance.model_type == model_type,
            ModelPerformance.is_active == True
        ).first()
        
        if not current_model:
            return {
                "status": "no_active_model",
                "model_type": model_type,
                "message": "No active model deployed yet"
            }
        
        return {
            "status": "active",
            "model_version": current_model.model_version,
            "model_type": current_model.model_type,
            "accuracy": current_model.accuracy,
            "deployed_at": current_model.deployed_at,
            "performance_metrics": {
                "accuracy": current_model.accuracy,
                "precision": current_model.precision,
                "recall": current_model.recall,
                "f1_score": current_model.f1_score
            }
        }
    except Exception as e:
        logger.error(f"Error getting current model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# DASHBOARD ENDPOINTS
# ========================================

@router.get("/dashboard/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    Get overview dashboard data
    
    Returns:
        - Collection statistics
        - Recent training jobs
        - Model performance
        - System health
    """
    try:
        collector = DataCollector(db)
        collection_stats = collector.get_collection_statistics()
        
        # Recent training jobs
        recent_jobs = db.query(TrainingJob).order_by(
            TrainingJob.created_at.desc()
        ).limit(5).all()
        
        # Active models
        active_models = db.query(ModelPerformance).filter(
            ModelPerformance.is_active == True
        ).all()
        
        return {
            "collection": collection_stats,
            "recent_jobs": [
                {
                    "job_id": job.job_id,
                    "status": job.status,
                    "progress": job.progress_percentage,
                    "model_type": job.model_type
                }
                for job in recent_jobs
            ],
            "active_models": [
                {
                    "model_version": model.model_version,
                    "model_type": model.model_type,
                    "accuracy": model.accuracy,
                    "deployed_at": model.deployed_at
                }
                for model in active_models
            ],
            "system_health": "operational"
        }
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# UTILITIES
# ========================================

@router.get("/roadmap")
async def get_phase_7_roadmap():
    """Get Phase 7 implementation roadmap"""
    return {
        "phase": "7 - Self-Learning Engine",
        "current_status": "Week 1 - Day 1 Complete (Foundation)",
        "completed_features": [
            "✅ Database schema (ValidatedCase, ModelPerformance, TrainingJob)",
            "✅ Data collector service with HIPAA anonymization",
            "✅ Case collection from treatment plans",
            "✅ Quality scoring and filtering",
            "✅ API endpoints for data management",
            "✅ Collection statistics and monitoring"
        ],
        "next_steps": [
            "📋 Week 1 (Days 2-7): Dataset export, background scheduler, comprehensive testing",
            "📋 Week 2: Automated training pipeline integration",
            "📋 Week 3: A/B testing and auto-deployment",
            "📋 Week 4: Dashboard UI and production hardening"
        ],
        "timeline": "4 weeks to full self-learning system",
        "benefits": [
            "Zero manual work - fully automated learning",
            "Learns from YOUR patient population",
            "$0/month cost - 100% local",
            "Complete privacy - on-premise learning",
            "Proprietary AI unique to your clinic"
        ]
    }
