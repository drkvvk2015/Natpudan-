"""
Phase 4 API Endpoints - Medical Image Analysis & Population Health

This module implements all Phase 4 endpoints:
- Medical image analysis (Claude Vision)
- Report generation
- Patient outcome tracking
- Risk scoring
- Population health analytics
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import base64
import logging

from ..database import get_db
from ..models.phase_4_models import (
    MedicalImage, MedicalReport, PatientOutcome, RiskScore,
    ProgressionPrediction, CohortAnalytics
)
from ..services.phase_4_services import get_medical_image_analyzer, get_image_cache_manager
from ..services.phase_4_services.medical_image_analyzer import ImageType, ImageSeverity
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Create router with Phase 4 prefix (will be included in api_router without prefix)
router = APIRouter(prefix="/phase-4", tags=["Phase 4"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ImageAnalysisRequest(BaseModel):
    """Request for analyzing a medical image"""
    clinical_context: Optional[str] = None
    patient_id: Optional[int] = None


class ImageAnalysisResponse(BaseModel):
    """Response from image analysis"""
    image_id: int
    image_type: str
    findings: List[str]
    severity: str
    confidence: float
    differential_diagnoses: List[str]
    recommendations: List[str]
    ai_analysis_date: datetime


class BatchAnalysisRequest(BaseModel):
    """Request for batch image analysis"""
    image_ids: List[int]
    clinical_context: Optional[str] = None


class VerificationRequest(BaseModel):
    """Radiologist verification of AI findings"""
    verified_findings: List[str]
    verification_notes: Optional[str] = None
    verified_by: int  # Doctor user ID


class ReportGenerationRequest(BaseModel):
    """Request to generate a medical report"""
    patient_id: int
    report_type: str  # discharge, progress, treatment, follow-up
    image_ids: Optional[List[int]] = None
    include_citations: bool = True


class OutcomeRecordRequest(BaseModel):
    """Record patient outcome"""
    patient_id: int
    visit_date: datetime
    outcome_status: str
    vital_signs: Optional[Dict[str, Any]] = None
    lab_results: Optional[Dict[str, Any]] = None
    clinical_notes: Optional[str] = None


class RiskScoreResponse(BaseModel):
    """Risk score computation result"""
    patient_id: int
    hospitalization_risk: float
    readmission_risk: float
    complication_risk: float
    mortality_risk: float
    risk_factors: List[str]
    computed_at: datetime


# ============================================================================
# MEDICAL IMAGE ANALYSIS ENDPOINTS
# ============================================================================

@router.post("/image/analyze", response_model=ImageAnalysisResponse)
async def analyze_medical_image(
    image: UploadFile = File(...),
    image_type: str = "xray",
    clinical_context: Optional[str] = None,
    patient_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze a medical image using Claude Vision API
    
    Supports: X-ray, ECG, ultrasound, pathology, MRI, CT
    """
    try:
        # Read image data
        image_data = await image.read()
        
        # Convert image type string to enum
        try:
            img_type = ImageType[image_type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type: {image_type}. Must be one of: xray, ecg, ultrasound, pathology, mri, ct"
            )
        
        # Check cache first
        cache_manager = get_image_cache_manager()
        image_hash = cache_manager.compute_image_hash(image_data)
        
        cached_analysis = cache_manager.get_cached_analysis(image_hash)
        if cached_analysis:
            logger.info(f"Cache hit for image {image_hash[:16]}")
            return cached_analysis
        
        # Analyze with Claude Vision
        analyzer = get_medical_image_analyzer()
        analysis_result = await analyzer.analyze_image(
            image_data=image_data,
            image_type=img_type,
            patient_context={"clinical_context": clinical_context} if clinical_context else None
        )
        
        # Save to database
        db_image = MedicalImage(
            patient_id=patient_id,
            image_type=image_type,
            image_hash=image_hash,
            image_data=image_data,
            ai_findings=analysis_result.get("findings", []),
            ai_confidence=analysis_result.get("confidence", 0.0),
            ai_severity=analysis_result.get("severity", "UNKNOWN"),
            differential_diagnoses=analysis_result.get("differential_diagnoses", []),
            recommendations=analysis_result.get("recommendations", []),
            clinical_significance=analysis_result.get("clinical_significance"),
            ai_analysis_date=datetime.utcnow()
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        # Cache the result
        cache_manager.cache_analysis(image_hash, analysis_result)
        
        logger.info(f"Image analysis complete: ID={db_image.id}, severity={db_image.ai_severity}")
        
        return ImageAnalysisResponse(
            image_id=db_image.id,
            image_type=db_image.image_type,
            findings=db_image.ai_findings,
            severity=db_image.ai_severity,
            confidence=db_image.ai_confidence,
            differential_diagnoses=db_image.differential_diagnoses,
            recommendations=db_image.recommendations,
            ai_analysis_date=db_image.ai_analysis_date
        )
        
    except Exception as e:
        logger.error(f"Image analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/image/batch-analyze")
async def batch_analyze_images(
    request: BatchAnalysisRequest,
    db: Session = Depends(get_db)
):
    """Batch analyze multiple medical images"""
    try:
        results = []
        analyzer = get_medical_image_analyzer()
        
        for image_id in request.image_ids:
            # Fetch image from database
            db_image = db.query(MedicalImage).filter(MedicalImage.id == image_id).first()
            if not db_image:
                results.append({"image_id": image_id, "error": "Image not found"})
                continue
            
            # Check if already analyzed
            if db_image.ai_findings:
                results.append({
                    "image_id": image_id,
                    "status": "already_analyzed",
                    "findings": db_image.ai_findings
                })
                continue
            
            # Analyze
            analysis = await analyzer.analyze_image(
                image_data=db_image.image_data,
                image_type=ImageType[db_image.image_type.upper()],
                patient_context={"clinical_context": request.clinical_context} if request.clinical_context else None
            )
            
            # Update database
            db_image.ai_findings = analysis.get("findings", [])
            db_image.ai_confidence = analysis.get("confidence", 0.0)
            db_image.ai_severity = analysis.get("severity", "UNKNOWN")
            db_image.ai_analysis_date = datetime.utcnow()
            
            results.append({
                "image_id": image_id,
                "status": "analyzed",
                "findings": db_image.ai_findings,
                "severity": db_image.ai_severity
            })
        
        db.commit()
        
        return {
            "total_images": len(request.image_ids),
            "analyzed": len([r for r in results if r.get("status") == "analyzed"]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image/{image_id}")
def get_image_analysis(image_id: int, db: Session = Depends(get_db)):
    """Retrieve analysis results for a specific image"""
    db_image = db.query(MedicalImage).filter(MedicalImage.id == image_id).first()
    
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return {
        "image_id": db_image.id,
        "patient_id": db_image.patient_id,
        "image_type": db_image.image_type,
        "findings": db_image.ai_findings,
        "severity": db_image.ai_severity,
        "confidence": db_image.ai_confidence,
        "differential_diagnoses": db_image.differential_diagnoses,
        "recommendations": db_image.recommendations,
        "verification_status": db_image.verification_status,
        "verified_by": db_image.verified_by,
        "verification_notes": db_image.verification_notes,
        "ai_analysis_date": db_image.ai_analysis_date,
        "verification_date": db_image.verification_date
    }


@router.post("/image/{image_id}/verify")
def verify_image_analysis(
    image_id: int,
    verification: VerificationRequest,
    db: Session = Depends(get_db)
):
    """Radiologist verification of AI findings"""
    db_image = db.query(MedicalImage).filter(MedicalImage.id == image_id).first()
    
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Update with verified findings
    db_image.verified_findings = verification.verified_findings
    db_image.verification_notes = verification.verification_notes
    db_image.verified_by = verification.verified_by
    db_image.verification_status = "VERIFIED"
    db_image.verification_date = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Image {image_id} verified by user {verification.verified_by}")
    
    return {
        "status": "success",
        "message": "Image analysis verified",
        "image_id": image_id,
        "verification_date": db_image.verification_date
    }


# ============================================================================
# REPORT GENERATION ENDPOINTS (Placeholder for Sprint 2)
# ============================================================================

@router.post("/report/generate")
def generate_medical_report(
    request: ReportGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate a medical report (Sprint 2 implementation)"""
    # TODO: Implement in Sprint 2
    return {
        "status": "pending",
        "message": "Report generation will be implemented in Sprint 2",
        "report_type": request.report_type
    }


# ============================================================================
# PATIENT OUTCOME & RISK SCORING ENDPOINTS (Placeholder for Sprint 3)
# ============================================================================

@router.post("/patient/{patient_id}/outcomes/record")
def record_patient_outcome(
    patient_id: int,
    outcome: OutcomeRecordRequest,
    db: Session = Depends(get_db)
):
    """Record patient outcome data"""
    db_outcome = PatientOutcome(
        patient_id=patient_id,
        visit_date=outcome.visit_date,
        outcome_status=outcome.outcome_status,
        vital_signs=outcome.vital_signs,
        lab_results=outcome.lab_results,
        clinical_notes=outcome.clinical_notes,
        recorded_at=datetime.utcnow()
    )
    
    db.add(db_outcome)
    db.commit()
    db.refresh(db_outcome)
    
    logger.info(f"Outcome recorded for patient {patient_id}")
    
    return {
        "status": "success",
        "outcome_id": db_outcome.id,
        "patient_id": patient_id
    }


@router.get("/patient/{patient_id}/risk-score", response_model=RiskScoreResponse)
def get_patient_risk_score(patient_id: int, db: Session = Depends(get_db)):
    """Get risk scores for a patient (Sprint 3 implementation)"""
    # TODO: Implement ML-based risk scoring in Sprint 3
    # For now, return placeholder
    return RiskScoreResponse(
        patient_id=patient_id,
        hospitalization_risk=0.0,
        readmission_risk=0.0,
        complication_risk=0.0,
        mortality_risk=0.0,
        risk_factors=["To be implemented in Sprint 3"],
        computed_at=datetime.utcnow()
    )


# ============================================================================
# POPULATION HEALTH ANALYTICS ENDPOINTS (Placeholder for Sprint 4)
# ============================================================================

@router.get("/analytics/disease-prevalence")
def get_disease_prevalence(
    disease_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get disease prevalence statistics (Sprint 4 implementation)"""
    # TODO: Implement in Sprint 4
    return {
        "status": "pending",
        "message": "Disease prevalence analytics will be implemented in Sprint 4"
    }


@router.get("/analytics/health-equity")
def get_health_equity_metrics(
    metric_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get health equity disparity metrics (Sprint 4 implementation)"""
    # TODO: Implement in Sprint 4
    return {
        "status": "pending",
        "message": "Health equity metrics will be implemented in Sprint 4"
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
def phase_4_health_check():
    """Phase 4 service health check"""
    try:
        analyzer = get_medical_image_analyzer()
        cache_manager = get_image_cache_manager()
        
        cache_stats = cache_manager.get_cache_statistics()
        
        return {
            "status": "healthy",
            "phase": "Phase 4",
            "services": {
                "medical_image_analyzer": "active",
                "image_cache": "active"
            },
            "cache_statistics": cache_stats,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }
