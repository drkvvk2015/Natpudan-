"""
Treatment Plan API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

# ==================== Request/Response Models ====================

class MedicationCreate(BaseModel):
    medication_name: str
    generic_name: Optional[str] = None
    dosage: str
    route: str = "oral"
    frequency: str = "once_daily"
    duration_days: Optional[int] = None
    instructions: Optional[str] = None
    precautions: Optional[str] = None
    side_effects: Optional[str] = None
    refills_remaining: int = 0


class MedicationResponse(BaseModel):
    id: int
    medication_name: str
    generic_name: Optional[str]
    dosage: str
    route: str
    frequency: str
    duration_days: Optional[int]
    instructions: Optional[str]
    precautions: Optional[str]
    side_effects: Optional[str]
    prescribed_date: datetime
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    refills_remaining: int
    is_active: bool
    discontinuation_reason: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


class FollowUpCreate(BaseModel):
    scheduled_date: datetime
    appointment_type: Optional[str] = None
    location: Optional[str] = None
    provider: Optional[str] = None
    pre_appointment_instructions: Optional[str] = None


class FollowUpResponse(BaseModel):
    id: int
    scheduled_date: datetime
    appointment_type: Optional[str]
    location: Optional[str]
    provider: Optional[str]
    status: str
    completed_date: Optional[datetime]
    pre_appointment_instructions: Optional[str]
    post_appointment_notes: Optional[str]
    outcome: Optional[str]
    reminder_sent: bool
    
    model_config = ConfigDict(from_attributes=True)


class MonitoringRecordCreate(BaseModel):
    monitoring_type: str
    measurements: Optional[str] = None  # JSON string
    assessment: Optional[str] = None
    concerns: Optional[str] = None
    action_taken: Optional[str] = None
    recorded_by: Optional[str] = None


class MonitoringRecordResponse(BaseModel):
    id: int
    record_date: datetime
    monitoring_type: str
    measurements: Optional[str]
    assessment: Optional[str]
    concerns: Optional[str]
    action_taken: Optional[str]
    recorded_by: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


class TreatmentPlanCreate(BaseModel):
    patient_intake_id: str
    diagnosis_id: Optional[str] = None
    primary_diagnosis: str
    icd_code: Optional[str] = None
    treatment_goals: Optional[str] = None
    clinical_notes: Optional[str] = None
    created_by: Optional[str] = None
    medications: List[MedicationCreate] = []
    follow_ups: List[FollowUpCreate] = []


class TreatmentPlanUpdate(BaseModel):
    status: Optional[str] = None
    treatment_goals: Optional[str] = None
    clinical_notes: Optional[str] = None
    end_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None


class TreatmentPlanResponse(BaseModel):
    id: int
    plan_id: str
    patient_intake_id: str
    diagnosis_id: Optional[str]
    primary_diagnosis: str
    icd_code: Optional[str]
    treatment_goals: Optional[str]
    clinical_notes: Optional[str]
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    last_review_date: Optional[datetime]
    next_review_date: Optional[datetime]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    medications: List[MedicationResponse]
    follow_ups: List[FollowUpResponse]
    monitoring_records: List[MonitoringRecordResponse]
    
    model_config = ConfigDict(from_attributes=True)


# ==================== API Endpoints ====================

from ..database.connection import SessionLocal
from ..database.models import TreatmentPlan, Medication, FollowUp, PatientIntake, MonitoringRecord

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/treatment-plans", response_model=TreatmentPlanResponse)
async def create_treatment_plan(plan: TreatmentPlanCreate, db: Session = Depends(get_db)):
    """Create a new treatment plan"""
    try:

        
        # Verify patient exists
        patient = db.query(PatientIntake).filter(PatientIntake.intake_id == plan.patient_intake_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Generate plan ID
        plan_id = f"TP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        
        # Create treatment plan
        db_plan = TreatmentPlan(
            plan_id=plan_id,
            patient_intake_id=plan.patient_intake_id,
            diagnosis_id=plan.diagnosis_id,
            primary_diagnosis=plan.primary_diagnosis,
            icd_code=plan.icd_code,
            treatment_goals=plan.treatment_goals,
            clinical_notes=plan.clinical_notes,
            created_by=plan.created_by,
            status="active"
        )
        
        db.add(db_plan)
        db.flush()  # Get the ID
        
        # Add medications
        for med_data in plan.medications:
            medication = Medication(
                treatment_plan_id=db_plan.id,
                **med_data.model_dump()
            )
            db.add(medication)
        
        # Add follow-ups
        for followup_data in plan.follow_ups:
            followup = FollowUp(
                treatment_plan_id=db_plan.id,
                **followup_data.model_dump()
            )
            db.add(followup)
        
        db.commit()
        db.refresh(db_plan)
        
        return db_plan
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating treatment plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create treatment plan: {str(e)}")


@router.get("/treatment-plans/patient/{patient_intake_id}", response_model=List[TreatmentPlanResponse])
async def get_patient_treatment_plans(patient_intake_id: str, db: Session = Depends(get_db)):
    """Get all treatment plans for a patient"""
    try:
        
        plans = db.query(TreatmentPlan).filter(
            TreatmentPlan.patient_intake_id == patient_intake_id
        ).order_by(TreatmentPlan.created_at.desc()).all()
        
        return plans
        
    except Exception as e:
        logger.error(f"Error fetching treatment plans: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch treatment plans: {str(e)}")


@router.get("/treatment-plans/{plan_id}", response_model=TreatmentPlanResponse)
async def get_treatment_plan(plan_id: str, db: Session = Depends(get_db)):
    """Get a specific treatment plan"""
    try:
        
        plan = db.query(TreatmentPlan).filter(TreatmentPlan.plan_id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Treatment plan not found")
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching treatment plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch treatment plan: {str(e)}")


@router.put("/treatment-plans/{plan_id}", response_model=TreatmentPlanResponse)
async def update_treatment_plan(plan_id: str, plan_update: TreatmentPlanUpdate, db: Session = Depends(get_db)):
    """Update a treatment plan"""
    try:
        
        plan = db.query(TreatmentPlan).filter(TreatmentPlan.plan_id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Treatment plan not found")
        
        # Update fields
        update_data = plan_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plan, field, value)
        
        plan.last_review_date = datetime.utcnow()
        
        db.commit()
        db.refresh(plan)
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating treatment plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update treatment plan: {str(e)}")


@router.post("/treatment-plans/{plan_id}/medications", response_model=MedicationResponse)
async def add_medication(plan_id: str, medication: MedicationCreate, db: Session = Depends(get_db)):
    """Add a medication to a treatment plan"""
    try:
        
        plan = db.query(TreatmentPlan).filter(TreatmentPlan.plan_id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Treatment plan not found")
        
        db_medication = Medication(
            treatment_plan_id=plan.id,
            **medication.model_dump()
        )
        
        db.add(db_medication)
        db.commit()
        db.refresh(db_medication)
        
        return db_medication
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding medication: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add medication: {str(e)}")


@router.put("/medications/{medication_id}")
async def update_medication(medication_id: int, is_active: bool, discontinuation_reason: Optional[str] = None, db: Session = Depends(get_db)):
    """Update medication status (discontinue/reactivate)"""
    try:
        
        medication = db.query(Medication).filter(Medication.id == medication_id).first()
        if not medication:
            raise HTTPException(status_code=404, detail="Medication not found")
        
        medication.is_active = is_active
        if not is_active:
            medication.discontinuation_reason = discontinuation_reason
            medication.discontinuation_date = datetime.utcnow()
        
        db.commit()
        db.refresh(medication)
        
        return {"message": "Medication updated successfully", "medication": medication}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating medication: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update medication: {str(e)}")


@router.post("/treatment-plans/{plan_id}/follow-ups", response_model=FollowUpResponse)
async def add_follow_up(plan_id: str, followup: FollowUpCreate, db: Session = Depends(get_db)):
    """Add a follow-up appointment"""
    try:
        
        plan = db.query(TreatmentPlan).filter(TreatmentPlan.plan_id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Treatment plan not found")
        
        db_followup = FollowUp(
            treatment_plan_id=plan.id,
            **followup.model_dump()
        )
        
        db.add(db_followup)
        db.commit()
        db.refresh(db_followup)
        
        return db_followup
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding follow-up: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add follow-up: {str(e)}")


@router.put("/follow-ups/{followup_id}")
async def update_follow_up(
    followup_id: int, 
    status: Optional[str] = None, 
    post_appointment_notes: Optional[str] = None, 
    outcome: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update follow-up status and notes"""
    try:
        
        followup = db.query(FollowUp).filter(FollowUp.id == followup_id).first()
        if not followup:
            raise HTTPException(status_code=404, detail="Follow-up not found")
        
        if status:
            followup.status = status
            if status == "completed":
                followup.completed_date = datetime.utcnow()
        
        if post_appointment_notes:
            followup.post_appointment_notes = post_appointment_notes
        
        if outcome:
            followup.outcome = outcome
        
        db.commit()
        db.refresh(followup)
        
        return {"message": "Follow-up updated successfully", "followup": followup}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating follow-up: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update follow-up: {str(e)}")


@router.post("/treatment-plans/{plan_id}/monitoring", response_model=MonitoringRecordResponse)
async def add_monitoring_record(plan_id: str, record: MonitoringRecordCreate, db: Session = Depends(get_db)):
    """Add a monitoring record to a treatment plan"""
    try:
        
        plan = db.query(TreatmentPlan).filter(TreatmentPlan.plan_id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Treatment plan not found")
        
        db_record = MonitoringRecord(
            treatment_plan_id=plan.id,
            **record.model_dump()
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        return db_record
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding monitoring record: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add monitoring record: {str(e)}")


@router.get("/treatment-plans", response_model=List[Dict[str, Any]])
async def list_all_treatment_plans(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all treatment plans with optional filters"""
    try:
        
        query = db.query(TreatmentPlan)
        
        if status:
            query = query.filter(TreatmentPlan.status == status)
        
        plans = query.order_by(TreatmentPlan.created_at.desc()).offset(skip).limit(limit).all()
        
        # Enhance with patient data
        result = []
        for plan in plans:
            patient = db.query(PatientIntake).filter(PatientIntake.intake_id == plan.patient_intake_id).first()
            result.append({
                "plan_id": plan.plan_id,
                "patient_name": patient.name if patient else "Unknown",
                "patient_intake_id": plan.patient_intake_id,
                "primary_diagnosis": plan.primary_diagnosis,
                "status": plan.status,
                "start_date": plan.start_date,
                "medications_count": len(plan.medications),
                "follow_ups_count": len(plan.follow_ups),
                "created_at": plan.created_at
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing treatment plans: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list treatment plans: {str(e)}")
