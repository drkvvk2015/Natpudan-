"""Discharge Summary API endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.api.auth_new import get_current_user
from app.models import User
from app.crud import (
    create_discharge_summary,
    get_discharge_summary,
    get_user_discharge_summaries,
    update_discharge_summary,
    delete_discharge_summary,
)
from app.utils.ai_service import generate_discharge_summary

router = APIRouter(prefix="/discharge-summary", tags=["discharge-summary"])


class DischargeSummaryRequest(BaseModel):
    patient_name: str
    patient_age: Optional[str] = None
    patient_gender: Optional[str] = None
    mrn: Optional[str] = None
    admission_date: Optional[str] = None
    discharge_date: Optional[str] = None
    chief_complaint: Optional[str] = None
    history_present_illness: Optional[str] = None
    past_medical_history: Optional[str] = None
    physical_examination: Optional[str] = None
    diagnosis: Optional[str] = None
    hospital_course: Optional[str] = None
    procedures_performed: Optional[str] = None
    medications: Optional[str] = None
    discharge_medications: Optional[str] = None
    follow_up_instructions: Optional[str] = None
    diet_restrictions: Optional[str] = None
    activity_restrictions: Optional[str] = None


class DischargeSummaryResponse(BaseModel):
    id: int
    patient_name: str
    mrn: Optional[str]
    admission_date: Optional[str]
    discharge_date: Optional[str]
    created_at: str
    updated_at: str


class DischargeSummaryDetail(DischargeSummaryRequest):
    id: int
    ai_summary: Optional[str]
    created_at: str
    updated_at: str


class AIGenerateRequest(BaseModel):
    patient_data: dict


@router.post("/", response_model=DischargeSummaryResponse)
async def create_summary(
    request: DischargeSummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new discharge summary."""
    summary = create_discharge_summary(
        db=db,
        created_by_id=current_user.id,
        patient_data=request.dict(),
    )
    
    return DischargeSummaryResponse(
        id=summary.id,
        patient_name=summary.patient_name,
        mrn=summary.mrn,
        admission_date=summary.admission_date,
        discharge_date=summary.discharge_date,
        created_at=summary.created_at.isoformat(),
        updated_at=summary.updated_at.isoformat(),
    )


@router.get("/", response_model=List[DischargeSummaryResponse])
async def list_summaries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all discharge summaries created by current user."""
    summaries = get_user_discharge_summaries(db, current_user.id)
    
    return [
        DischargeSummaryResponse(
            id=summary.id,
            patient_name=summary.patient_name,
            mrn=summary.mrn,
            admission_date=summary.admission_date,
            discharge_date=summary.discharge_date,
            created_at=summary.created_at.isoformat(),
            updated_at=summary.updated_at.isoformat(),
        )
        for summary in summaries
    ]


@router.get("/{summary_id}", response_model=DischargeSummaryDetail)
async def get_summary(
    summary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific discharge summary."""
    summary = get_discharge_summary(db, summary_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discharge summary not found"
        )
    
    # Verify ownership (you might want to allow doctors to view all summaries)
    if summary.created_by_id != current_user.id and current_user.role.value not in ["doctor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this summary"
        )
    
    return DischargeSummaryDetail(
        id=summary.id,
        patient_name=summary.patient_name,
        patient_age=summary.patient_age,
        patient_gender=summary.patient_gender,
        mrn=summary.mrn,
        admission_date=summary.admission_date,
        discharge_date=summary.discharge_date,
        chief_complaint=summary.chief_complaint,
        history_present_illness=summary.history_present_illness,
        past_medical_history=summary.past_medical_history,
        physical_examination=summary.physical_examination,
        diagnosis=summary.diagnosis,
        hospital_course=summary.hospital_course,
        procedures_performed=summary.procedures_performed,
        medications=summary.medications,
        discharge_medications=summary.discharge_medications,
        follow_up_instructions=summary.follow_up_instructions,
        diet_restrictions=summary.diet_restrictions,
        activity_restrictions=summary.activity_restrictions,
        ai_summary=summary.ai_summary,
        created_at=summary.created_at.isoformat(),
        updated_at=summary.updated_at.isoformat(),
    )


@router.put("/{summary_id}", response_model=DischargeSummaryResponse)
async def update_summary(
    summary_id: int,
    request: DischargeSummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a discharge summary."""
    summary = get_discharge_summary(db, summary_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discharge summary not found"
        )
    
    if summary.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this summary"
        )
    
    updated_summary = update_discharge_summary(
        db=db,
        summary_id=summary_id,
        patient_data=request.dict(),
    )
    
    return DischargeSummaryResponse(
        id=updated_summary.id,
        patient_name=updated_summary.patient_name,
        mrn=updated_summary.mrn,
        admission_date=updated_summary.admission_date,
        discharge_date=updated_summary.discharge_date,
        created_at=updated_summary.created_at.isoformat(),
        updated_at=updated_summary.updated_at.isoformat(),
    )


@router.delete("/{summary_id}")
async def delete_summary(
    summary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a discharge summary."""
    summary = get_discharge_summary(db, summary_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discharge summary not found"
        )
    
    if summary.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this summary"
        )
    
    delete_discharge_summary(db, summary_id)
    return {"message": "Discharge summary deleted successfully"}


@router.post("/ai-generate")
async def ai_generate(
    request: AIGenerateRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate AI discharge summary from patient data."""
    try:
        ai_summary = await generate_discharge_summary(request.patient_data)
        return {"ai_summary": ai_summary}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI summary: {str(e)}"
        )
