from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import logging
import json

from app.database import get_db
from app.models import PatientIntake, TravelHistory, FamilyHistory, TreatmentPlan, Medication, FollowUp

logger = logging.getLogger(__name__)
router = APIRouter()


# ========================= FHIR RESOURCE MODELS =========================

class FHIRIdentifier(BaseModel):
    system: str
    value: str


class FHIRCodeableConcept(BaseModel):
    coding: List[Dict[str, Any]]
    text: Optional[str] = None


class FHIRReference(BaseModel):
    reference: str
    display: Optional[str] = None


class FHIRPatient(BaseModel):
    resourceType: str = "Patient"
    id: str
    identifier: List[FHIRIdentifier]
    active: bool
    name: List[Dict[str, Any]]
    telecom: List[Dict[str, Any]]
    gender: Optional[str]
    birthDate: Optional[str]
    address: Optional[List[Dict[str, Any]]]
    
    
class FHIRCondition(BaseModel):
    resourceType: str = "Condition"
    id: str
    subject: FHIRReference
    code: FHIRCodeableConcept
    clinicalStatus: FHIRCodeableConcept
    verificationStatus: FHIRCodeableConcept
    recordedDate: str
    

class FHIRMedicationRequest(BaseModel):
    resourceType: str = "MedicationRequest"
    id: str
    status: str
    intent: str = "order"
    medicationCodeableConcept: FHIRCodeableConcept
    subject: FHIRReference
    authoredOn: str
    dosageInstruction: List[Dict[str, Any]]


class FHIRAppointment(BaseModel):
    resourceType: str = "Appointment"
    id: str
    status: str
    description: Optional[str]
    start: str
    end: Optional[str]
    participant: List[Dict[str, Any]]


class FHIRBundle(BaseModel):
    resourceType: str = "Bundle"
    type: str
    total: int
    entry: List[Dict[str, Any]]


# ========================= HELPER FUNCTIONS =========================

def convert_patient_to_fhir(patient: PatientIntake) -> Dict[str, Any]:
    """Convert PatientIntake to FHIR Patient resource"""
    
    # Gender mapping
    gender_map = {
        "Male": "male",
        "Female": "female",
        "male": "male",
        "female": "female",
        "M": "male",
        "F": "female"
    }
    
    fhir_patient = {
        "resourceType": "Patient",
        "id": patient.intake_id,
        "identifier": [
            {
                "system": "http://hospital.example.org/patients",
                "value": patient.uhid
            }
        ],
        "active": True,
        "name": [
            {
                "use": "official",
                "text": patient.name,
                "family": patient.name.split()[-1] if patient.name else "",
                "given": patient.name.split()[:-1] if patient.name else []
            }
        ],
        "telecom": [
            {
                "system": "phone",
                "value": patient.contact_number,
                "use": "mobile"
            }
        ],
        "gender": gender_map.get(patient.sex, "unknown"),
        "address": [
            {
                "use": "home",
                "text": patient.address or "",
                "city": patient.city or "",
                "state": patient.state or "",
                "country": patient.country or ""
            }
        ]
    }
    
    # Add birth date if age is available
    if patient.age and patient.age.isdigit():
        current_year = datetime.now().year
        birth_year = current_year - int(patient.age)
        fhir_patient["birthDate"] = f"{birth_year}-01-01"
    
    return fhir_patient


def convert_treatment_to_fhir_condition(plan: TreatmentPlan) -> Dict[str, Any]:
    """Convert TreatmentPlan to FHIR Condition resource"""
    
    # Clinical status mapping
    status_map = {
        "active": "active",
        "completed": "resolved",
        "discontinued": "inactive",
        "on_hold": "inactive"
    }
    
    fhir_condition = {
        "resourceType": "Condition",
        "id": plan.plan_id,
        "subject": {
            "reference": f"Patient/{plan.patient_intake_id}",
            "display": plan.patient.name if plan.patient else "Unknown"
        },
        "code": {
            "coding": [
                {
                    "system": "http://hl7.org/fhir/sid/icd-10",
                    "code": plan.icd_code or "Unknown",
                    "display": plan.primary_diagnosis
                }
            ],
            "text": plan.primary_diagnosis
        },
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": status_map.get(plan.status, "unknown")
                }
            ]
        },
        "verificationStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": "confirmed"
                }
            ]
        },
        "recordedDate": plan.created_at.isoformat() if plan.created_at else datetime.now().isoformat()
    }
    
    return fhir_condition


def convert_medication_to_fhir(medication: Medication, patient_ref: str) -> Dict[str, Any]:
    """Convert Medication to FHIR MedicationRequest resource"""
    
    status_map = {
        True: "active",
        False: "stopped"
    }
    
    fhir_medication = {
        "resourceType": "MedicationRequest",
        "id": f"med-{medication.id}",
        "status": status_map.get(medication.is_active, "unknown"),
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "display": medication.medication_name
                }
            ],
            "text": medication.medication_name
        },
        "subject": {
            "reference": patient_ref
        },
        "authoredOn": medication.prescribed_date.isoformat() if medication.prescribed_date else datetime.now().isoformat(),
        "dosageInstruction": [
            {
                "text": f"{medication.dosage}, {medication.route}, {medication.frequency}",
                "timing": {
                    "repeat": {
                        "frequency": 1,
                        "period": 1,
                        "periodUnit": "d"
                    }
                },
                "route": {
                    "text": medication.route
                },
                "doseAndRate": [
                    {
                        "doseQuantity": {
                            "value": medication.dosage,
                            "unit": "dose"
                        }
                    }
                ]
            }
        ]
    }
    
    if medication.instructions:
        fhir_medication["note"] = [{"text": medication.instructions}]
    
    return fhir_medication


def convert_followup_to_fhir(followup: FollowUp, patient_ref: str) -> Dict[str, Any]:
    """Convert FollowUp to FHIR Appointment resource"""
    
    status_map = {
        "scheduled": "booked",
        "completed": "fulfilled",
        "missed": "noshow",
        "cancelled": "cancelled",
        "rescheduled": "booked"
    }
    
    fhir_appointment = {
        "resourceType": "Appointment",
        "id": f"appt-{followup.id}",
        "status": status_map.get(followup.status, "proposed"),
        "description": followup.appointment_type,
        "start": followup.scheduled_date.isoformat() if followup.scheduled_date else datetime.now().isoformat(),
        "participant": [
            {
                "actor": {
                    "reference": patient_ref
                },
                "required": "required",
                "status": "accepted"
            }
        ]
    }
    
    if followup.location:
        fhir_appointment["appointmentType"] = {
            "text": followup.location
        }
    
    if followup.provider:
        fhir_appointment["participant"].append({
            "actor": {
                "display": followup.provider
            },
            "required": "required",
            "status": "accepted"
        })
    
    return fhir_appointment


# ========================= FHIR API ENDPOINTS =========================

@router.get("/Patient/{patient_id}")
async def get_fhir_patient(patient_id: str, db: Session = Depends(get_db)):
    """
    Get FHIR Patient resource by ID
    
    Compliant with FHIR R4 Patient resource specification
    """
    try:
        # Fetch patient by intake_id or uhid
        patient = db.query(PatientIntake).filter(
            (PatientIntake.intake_id == patient_id) | (PatientIntake.uhid == patient_id)
        ).first()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        fhir_patient = convert_patient_to_fhir(patient)
        return fhir_patient
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching FHIR patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve patient resource")


@router.get("/Patient")
async def search_fhir_patients(
    name: Optional[str] = None,
    identifier: Optional[str] = None,
    _count: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search FHIR Patient resources
    
    Supports search parameters: name, identifier
    """
    try:
        query = db.query(PatientIntake)
        
        if name:
            query = query.filter(PatientIntake.name.ilike(f"%{name}%"))
        
        if identifier:
            query = query.filter(
                (PatientIntake.uhid == identifier) | 
                (PatientIntake.intake_id == identifier)
            )
        
        patients = query.limit(_count).all()
        
        # Create FHIR Bundle
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(patients),
            "entry": [
                {
                    "resource": convert_patient_to_fhir(patient),
                    "fullUrl": f"http://example.org/fhir/Patient/{patient.intake_id}"
                }
                for patient in patients
            ]
        }
        
        return bundle
        
    except Exception as e:
        logger.error(f"Error searching FHIR patients: {e}")
        raise HTTPException(status_code=500, detail="Failed to search patients")


@router.get("/Condition/{condition_id}")
async def get_fhir_condition(condition_id: str, db: Session = Depends(get_db)):
    """Get FHIR Condition resource by ID"""
    try:
        plan = db.query(TreatmentPlan).filter(TreatmentPlan.plan_id == condition_id).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Condition not found")
        
        fhir_condition = convert_treatment_to_fhir_condition(plan)
        return fhir_condition
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching FHIR condition: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve condition resource")


@router.get("/Condition")
async def search_fhir_conditions(
    patient: Optional[str] = None,
    _count: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search FHIR Condition resources"""
    try:
        query = db.query(TreatmentPlan)
        
        if patient:
            query = query.filter(TreatmentPlan.patient_intake_id == patient)
        
        plans = query.limit(_count).all()
        
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(plans),
            "entry": [
                {
                    "resource": convert_treatment_to_fhir_condition(plan),
                    "fullUrl": f"http://example.org/fhir/Condition/{plan.plan_id}"
                }
                for plan in plans
            ]
        }
        
        return bundle
        
    except Exception as e:
        logger.error(f"Error searching FHIR conditions: {e}")
        raise HTTPException(status_code=500, detail="Failed to search conditions")


@router.get("/MedicationRequest")
async def search_fhir_medications(
    patient: Optional[str] = None,
    status: Optional[str] = None,
    _count: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search FHIR MedicationRequest resources"""
    try:
        query = db.query(Medication).join(TreatmentPlan)
        
        if patient:
            query = query.filter(TreatmentPlan.patient_intake_id == patient)
        
        if status:
            is_active = status == "active"
            query = query.filter(Medication.is_active == is_active)
        
        medications = query.limit(_count).all()
        
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(medications),
            "entry": [
                {
                    "resource": convert_medication_to_fhir(
                        med, 
                        f"Patient/{med.treatment_plan.patient_intake_id}"
                    ),
                    "fullUrl": f"http://example.org/fhir/MedicationRequest/med-{med.id}"
                }
                for med in medications
            ]
        }
        
        return bundle
        
    except Exception as e:
        logger.error(f"Error searching FHIR medications: {e}")
        raise HTTPException(status_code=500, detail="Failed to search medications")


@router.get("/Appointment")
async def search_fhir_appointments(
    patient: Optional[str] = None,
    status: Optional[str] = None,
    _count: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search FHIR Appointment resources"""
    try:
        query = db.query(FollowUp).join(TreatmentPlan)
        
        if patient:
            query = query.filter(TreatmentPlan.patient_intake_id == patient)
        
        if status:
            query = query.filter(FollowUp.status == status)
        
        followups = query.limit(_count).all()
        
        bundle = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(followups),
            "entry": [
                {
                    "resource": convert_followup_to_fhir(
                        followup,
                        f"Patient/{followup.treatment_plan.patient_intake_id}"
                    ),
                    "fullUrl": f"http://example.org/fhir/Appointment/appt-{followup.id}"
                }
                for followup in followups
            ]
        }
        
        return bundle
        
    except Exception as e:
        logger.error(f"Error searching FHIR appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to search appointments")


@router.get("/metadata")
async def get_capability_statement():
    """
    Get FHIR CapabilityStatement (server metadata)
    
    Describes the FHIR server capabilities and supported resources
    """
    return {
        "resourceType": "CapabilityStatement",
        "status": "active",
        "date": datetime.now().isoformat(),
        "kind": "instance",
        "fhirVersion": "4.0.1",
        "format": ["json"],
        "rest": [
            {
                "mode": "server",
                "resource": [
                    {
                        "type": "Patient",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"}
                        ],
                        "searchParam": [
                            {"name": "name", "type": "string"},
                            {"name": "identifier", "type": "token"}
                        ]
                    },
                    {
                        "type": "Condition",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"}
                        ],
                        "searchParam": [
                            {"name": "patient", "type": "reference"}
                        ]
                    },
                    {
                        "type": "MedicationRequest",
                        "interaction": [
                            {"code": "search-type"}
                        ],
                        "searchParam": [
                            {"name": "patient", "type": "reference"},
                            {"name": "status", "type": "token"}
                        ]
                    },
                    {
                        "type": "Appointment",
                        "interaction": [
                            {"code": "search-type"}
                        ],
                        "searchParam": [
                            {"name": "patient", "type": "reference"},
                            {"name": "status", "type": "token"}
                        ]
                    }
                ]
            }
        ]
    }


@router.get("/$export")
async def bulk_export(
    _type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    FHIR Bulk Data Export (simplified)
    
    Returns all resources or specific resource types
    """
    try:
        resources = []
        
        # Export patients if requested or all
        if not _type or _type == "Patient":
            patients = db.query(PatientIntake).all()
            resources.extend([convert_patient_to_fhir(p) for p in patients])
        
        # Export conditions if requested or all
        if not _type or _type == "Condition":
            plans = db.query(TreatmentPlan).all()
            resources.extend([convert_treatment_to_fhir_condition(p) for p in plans])
        
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "total": len(resources),
            "entry": [
                {"resource": resource}
                for resource in resources
            ]
        }
        
        return bundle
        
    except Exception as e:
        logger.error(f"Error in bulk export: {e}")
        raise HTTPException(status_code=500, detail="Failed to export data")
