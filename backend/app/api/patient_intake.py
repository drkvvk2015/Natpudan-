"""
Patient Intake API - Simplified complaint handling with structured chronological history
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models import PatientIntake, TravelHistory, FamilyHistory
from app.api.auth_new import get_current_user
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["patient-intake"])

# ==================== Pydantic Models ====================

class ChiefComplaint(BaseModel):
    """Chief complaint with chronological details"""
    complaint: str = Field(..., description="Primary complaint (e.g., Fever, Cough, Headache)")
    onset: str = Field(..., description="When it started (e.g., 3 days ago, last week)")
    duration: str = Field(..., description="How long (e.g., 3 days, 1 week)")
    severity: str = Field(..., description="Severity (Mild/Moderate/Severe)")
    character: Optional[str] = Field(None, description="Nature of complaint (e.g., throbbing, sharp)")
    location: Optional[str] = Field(None, description="Location if applicable")
    radiation: Optional[str] = Field(None, description="Radiation to other areas")
    relieving_factors: List[str] = Field(default_factory=list, description="What makes it better")
    aggravating_factors: List[str] = Field(default_factory=list, description="What makes it worse")
    associated_symptoms: List[str] = Field(default_factory=list, description="Other related symptoms")
    progression: str = Field("Stable", description="Getting better/worse/stable")
    timing: Optional[str] = Field(None, description="When does it occur (e.g., morning, after meals)")
    quality: Optional[str] = Field(None, description="Quality of symptom")


class AssociatedSymptom(BaseModel):
    """Associated symptoms with timeline"""
    symptom: str
    onset: str
    severity: str  # Mild/Moderate/Severe
    notes: Optional[str] = None


class TravelHistoryInput(BaseModel):
    """Travel history"""
    destination: str
    departure_date: str
    return_date: str
    duration: str
    purpose: str
    activities: List[str] = Field(default_factory=list)


class FamilyHistoryInput(BaseModel):
    """Family medical history"""
    relationship: str
    condition: str
    age_of_onset: Optional[int] = None
    current_status: str
    notes: Optional[str] = None


class PatientIntakeRequest(BaseModel):
    """Complete patient intake request"""
    # Demographics
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., pattern="^(Male|Female|Other)$")
    blood_type: Optional[str] = Field(None, pattern="^(A\\+|A-|B\\+|B-|AB\\+|AB-|O\\+|O-)$")
    
    # Chief complaints (multiple possible)
    chief_complaints: List[ChiefComplaint] = Field(default_factory=list)
    
    # Present history organized chronologically
    associated_symptoms: List[AssociatedSymptom] = Field(default_factory=list)
    
    # Past history
    past_medical_history: List[str] = Field(default_factory=list)
    past_surgical_history: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    
    # Social history
    smoking: Optional[str] = None
    alcohol: Optional[str] = None
    occupation: Optional[str] = None
    
    # Travel and family history
    travel_history: List[TravelHistoryInput] = Field(default_factory=list)
    family_history: List[FamilyHistoryInput] = Field(default_factory=list)


class PatientIntakeResponse(BaseModel):
    """Patient intake response"""
    intake_id: int
    name: str
    age: int
    gender: str
    blood_type: Optional[str]
    chief_complaints: List[Dict[str, Any]]
    associated_symptoms: List[Dict[str, Any]]
    past_medical_history: List[str]
    past_surgical_history: List[str]
    current_medications: List[str]
    allergies: List[str]
    smoking: Optional[str]
    alcohol: Optional[str]
    occupation: Optional[str]
    travel_history: List[Dict[str, Any]]
    family_history: List[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== Common Complaints Options ====================

COMMON_COMPLAINTS = [
    # Respiratory
    "Cough", "Shortness of breath", "Chest pain", "Wheezing",
    
    # General/Constitutional
    "Fever", "Chills", "Fatigue", "Weight loss", "Weight gain",
    "Night sweats", "Weakness", "Malaise",
    
    # Head/Neurological
    "Headache", "Dizziness", "Vertigo", "Confusion", "Memory problems",
    "Seizures", "Loss of consciousness",
    
    # GI
    "Nausea", "Vomiting", "Diarrhea", "Constipation", "Abdominal pain",
    "Heartburn", "Loss of appetite", "Blood in stool",
    
    # Cardiovascular
    "Palpitations", "Leg swelling", "Chest pressure",
    
    # Musculoskeletal
    "Joint pain", "Muscle pain", "Back pain", "Neck pain", "Stiffness",
    
    # Skin
    "Rash", "Itching", "Skin lesions", "Bruising",
    
    # ENT
    "Sore throat", "Ear pain", "Runny nose", "Nasal congestion",
    "Hearing loss", "Tinnitus",
    
    # Genitourinary
    "Painful urination", "Frequent urination", "Blood in urine",
    "Difficulty urinating",
    
    # Other
    "Vision changes", "Anxiety", "Depression", "Insomnia", "Pain"
]

RELIEVING_FACTORS = [
    "Rest", "Medication", "Cold compress", "Heat application",
    "Position change", "Deep breathing", "Massage", "Stretching",
    "Eating", "Drinking water", "Sleep", "Distraction",
    "Fresh air", "Lying down", "Sitting up", "Movement"
]

AGGRAVATING_FACTORS = [
    "Physical activity", "Stress", "Eating", "Lying down",
    "Standing", "Walking", "Coughing", "Deep breathing",
    "Cold weather", "Hot weather", "Night time", "Morning",
    "Bending", "Lifting", "Noise", "Light", "Touch"
]

SEVERITY_OPTIONS = ["Mild", "Moderate", "Severe"]

PROGRESSION_OPTIONS = ["Getting better", "Getting worse", "Stable", "Fluctuating"]

ONSET_OPTIONS = [
    "Today", "Yesterday", "2 days ago", "3 days ago", "1 week ago",
    "2 weeks ago", "1 month ago", "2 months ago", "3 months ago",
    "6 months ago", "1 year ago", "More than 1 year ago"
]

TIMING_OPTIONS = [
    "Constant", "Intermittent", "Morning", "Evening", "Night",
    "After meals", "Before meals", "During activity", "At rest",
    "Specific time of day"
]

CHARACTER_OPTIONS = {
    "Pain": ["Sharp", "Dull", "Aching", "Burning", "Throbbing", "Stabbing", "Cramping"],
    "Cough": ["Dry", "Productive", "Barking", "Hacking"],
    "Headache": ["Throbbing", "Pressure", "Sharp", "Dull"],
    "Fever": ["High grade", "Low grade", "Intermittent", "Continuous"]
}


@router.get("/complaints/options")
async def get_complaint_options():
    """Get all complaint options for UI dropdowns"""
    return {
        "common_complaints": sorted(COMMON_COMPLAINTS),
        "relieving_factors": sorted(RELIEVING_FACTORS),
        "aggravating_factors": sorted(AGGRAVATING_FACTORS),
        "severity_options": SEVERITY_OPTIONS,
        "progression_options": PROGRESSION_OPTIONS,
        "onset_options": ONSET_OPTIONS,
        "timing_options": TIMING_OPTIONS,
        "character_options": CHARACTER_OPTIONS
    }


# ==================== CRUD Endpoints ====================

@router.post("/patient-intake", response_model=PatientIntakeResponse)
async def create_patient_intake(
    data: PatientIntakeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new patient intake with simplified complaint handling"""
    try:
        # Create patient intake record
        patient = PatientIntake(
            name=data.name,
            age=data.age,
            gender=data.gender,
            blood_type=data.blood_type,
            chief_complaints=[complaint.dict() for complaint in data.chief_complaints],
            associated_symptoms=[symptom.dict() for symptom in data.associated_symptoms],
            past_medical_history=data.past_medical_history,
            past_surgical_history=data.past_surgical_history,
            current_medications=data.current_medications,
            allergies=data.allergies,
            smoking=data.smoking,
            alcohol=data.alcohol,
            occupation=data.occupation,
            created_by=current_user.id,
        )
        
        db.add(patient)
        db.flush()  # Get the patient ID
        
        # Add travel history
        for travel in data.travel_history:
            travel_record = TravelHistory(
                patient_intake_id=patient.id,
                destination=travel.destination,
                departure_date=travel.departure_date,
                return_date=travel.return_date,
                duration=travel.duration,
                purpose=travel.purpose,
                activities=travel.activities,
            )
            db.add(travel_record)
        
        # Add family history
        for family in data.family_history:
            family_record = FamilyHistory(
                patient_intake_id=patient.id,
                family_relationship=family.relationship,
                condition=family.condition,
                age_of_onset=str(family.age_of_onset) if family.age_of_onset else None,
                status=family.current_status,
                notes=family.notes,
            )
            db.add(family_record)
        
        db.commit()
        db.refresh(patient)
        
        logger.info(f"Created patient intake {patient.intake_id} for {patient.name}")
        
        return PatientIntakeResponse(
            intake_id=patient.intake_id,
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            blood_type=patient.blood_type,
            chief_complaints=patient.chief_complaints or [],
            associated_symptoms=patient.associated_symptoms or [],
            past_medical_history=patient.past_medical_history or [],
            past_surgical_history=patient.past_surgical_history or [],
            current_medications=patient.current_medications or [],
            allergies=patient.allergies or [],
            smoking=patient.smoking,
            alcohol=patient.alcohol,
            occupation=patient.occupation,
            travel_history=[],  # Will be fetched separately if needed
            family_history=[],  # Will be fetched separately if needed
            created_at=patient.created_at,
            updated_at=patient.updated_at,
        )
        
    except Exception as e:
        logger.error(f"Error creating patient intake: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create patient intake: {str(e)}"
        )


@router.get("/patient-intake/{intake_id}", response_model=PatientIntakeResponse)
async def get_patient_intake(
    intake_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get patient intake by ID"""
    try:
        patient = db.query(PatientIntake).filter(
            PatientIntake.intake_id == intake_id
        ).first()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient intake not found")
        
        # Get related records
        travel_history = db.query(TravelHistory).filter(
            TravelHistory.patient_intake_id == patient.id
        ).all()
        
        family_history = db.query(FamilyHistory).filter(
            FamilyHistory.patient_intake_id == patient.id
        ).all()
        
        return PatientIntakeResponse(
            intake_id=patient.intake_id,
            name=patient.name,
            age=patient.age,
            gender=patient.gender,
            blood_type=patient.blood_type,
            chief_complaints=patient.chief_complaints or [],
            associated_symptoms=patient.associated_symptoms or [],
            past_medical_history=patient.past_medical_history or [],
            past_surgical_history=patient.past_surgical_history or [],
            current_medications=patient.current_medications or [],
            allergies=patient.allergies or [],
            smoking=patient.smoking,
            alcohol=patient.alcohol,
            occupation=patient.occupation,
            travel_history=[
                {
                    "destination": t.destination,
                    "departure_date": t.departure_date,
                    "return_date": t.return_date,
                    "duration": t.duration,
                    "purpose": t.purpose,
                    "activities": t.activities or []
                }
                for t in travel_history
            ],
            family_history=[
                {
                    "relationship": f.family_relationship,
                    "condition": f.condition,
                    "age_of_onset": int(f.age_of_onset) if f.age_of_onset and f.age_of_onset.isdigit() else None,
                    "current_status": f.status,
                    "notes": f.notes
                }
                for f in family_history
            ],
            created_at=patient.created_at,
            updated_at=patient.updated_at,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient intake: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get patient intake: {str(e)}"
        )


@router.put("/patient-intake/{intake_id}", response_model=PatientIntakeResponse)
async def update_patient_intake(
    intake_id: int,
    data: PatientIntakeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update existing patient intake"""
    try:
        patient = db.query(PatientIntake).filter(
            PatientIntake.intake_id == intake_id
        ).first()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient intake not found")
        
        # Update patient fields
        patient.name = data.name
        patient.age = data.age
        patient.gender = data.gender
        patient.blood_type = data.blood_type
        patient.chief_complaints = [complaint.dict() for complaint in data.chief_complaints]
        patient.associated_symptoms = [symptom.dict() for symptom in data.associated_symptoms]
        patient.past_medical_history = data.past_medical_history
        patient.past_surgical_history = data.past_surgical_history
        patient.current_medications = data.current_medications
        patient.allergies = data.allergies
        patient.smoking = data.smoking
        patient.alcohol = data.alcohol
        patient.occupation = data.occupation
        patient.updated_at = datetime.utcnow()
        
        # Delete existing travel/family history and recreate
        db.query(TravelHistory).filter(TravelHistory.patient_intake_id == patient.id).delete()
        db.query(FamilyHistory).filter(FamilyHistory.patient_intake_id == patient.id).delete()
        
        # Add updated travel history
        for travel in data.travel_history:
            travel_record = TravelHistory(
                patient_intake_id=patient.id,
                destination=travel.destination,
                departure_date=travel.departure_date,
                return_date=travel.return_date,
                duration=travel.duration,
                purpose=travel.purpose,
                activities=travel.activities,
            )
            db.add(travel_record)
        
        # Add updated family history
        for family in data.family_history:
            family_record = FamilyHistory(
                patient_intake_id=patient.id,
                family_relationship=family.relationship,
                condition=family.condition,
                age_of_onset=str(family.age_of_onset) if family.age_of_onset else None,
                status=family.current_status,
                notes=family.notes,
            )
            db.add(family_record)
        
        db.commit()
        db.refresh(patient)
        
        logger.info(f"Updated patient intake {intake_id}")
        
        return await get_patient_intake(intake_id, db, current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient intake: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update patient intake: {str(e)}"
        )


@router.get("/patient-intake")
async def list_patient_intakes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all patient intakes"""
    try:
        patients = db.query(PatientIntake).offset(skip).limit(limit).all()
        
        return {
            "total": db.query(PatientIntake).count(),
            "patients": [
                {
                    "intake_id": p.intake_id,
                    "name": p.name,
                    "age": p.age,
                    "gender": p.gender,
                    "blood_type": p.blood_type,
                    "chief_complaints": p.chief_complaints or [],
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in patients
            ]
        }
    except Exception as e:
        logger.error(f"Error listing patient intakes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list patient intakes: {str(e)}"
        )
