from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
import logging

from ..database.connection import get_db
from ..database.models import PatientIntake, TravelHistory, FamilyHistory, TreatmentPlan, Medication, FollowUp, MonitoringRecord

logger = logging.getLogger(__name__)
router = APIRouter()


# ========================= PYDANTIC MODELS =========================

class TimelineEvent(BaseModel):
    id: str
    event_type: str  # intake, travel, family_history, treatment_plan, medication, follow_up, monitoring
    date: datetime
    title: str
    description: str
    status: Optional[str] = None
    related_id: Optional[str] = None
    metadata: Optional[dict] = {}
    
    model_config = ConfigDict(from_attributes=True)


class PatientTimelineResponse(BaseModel):
    patient_intake_id: str
    patient_name: str
    total_events: int
    events: List[TimelineEvent]


# ========================= HELPER FUNCTIONS =========================

def format_date(dt) -> datetime:
    """Convert various date formats to datetime"""
    if isinstance(dt, datetime):
        return dt
    elif isinstance(dt, str):
        try:
            return datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return datetime.now()
    return datetime.now()


def create_event(event_id: str, event_type: str, date, title: str, 
                 description: str, status: str = None, related_id: str = None,
                 metadata: dict = None) -> dict:
    """Create a timeline event dictionary"""
    return {
        "id": event_id,
        "event_type": event_type,
        "date": format_date(date),
        "title": title,
        "description": description,
        "status": status,
        "related_id": related_id,
        "metadata": metadata or {}
    }


# ========================= API ENDPOINTS =========================

@router.get("/patient/{patient_intake_id}", response_model=PatientTimelineResponse)
async def get_patient_timeline(
    patient_intake_id: str,
    event_types: Optional[str] = None,  # Comma-separated: "intake,treatment_plan,medication"
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive medical history timeline for a patient.
    
    Aggregates events from multiple sources:
    - Patient intake creation
    - Travel history entries
    - Family history entries
    - Treatment plans
    - Medications prescribed
    - Follow-up appointments
    - Monitoring records
    
    Query Parameters:
    - event_types: Filter by event types (comma-separated)
    - start_date: Filter events after this date (ISO format)
    - end_date: Filter events before this date (ISO format)
    """
    try:
        # Get patient intake
        patient = db.query(PatientIntake).filter(
            PatientIntake.intake_id == patient_intake_id
        ).first()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        events = []
        
        # Parse filter parameters
        filter_types = set(event_types.split(',')) if event_types else None
        filter_start = datetime.fromisoformat(start_date) if start_date else None
        filter_end = datetime.fromisoformat(end_date) if end_date else None
        
        # 1. PATIENT INTAKE EVENT
        if not filter_types or 'intake' in filter_types:
            intake_date = format_date(patient.created_at)
            if (not filter_start or intake_date >= filter_start) and \
               (not filter_end or intake_date <= filter_end):
                events.append(create_event(
                    event_id=f"intake-{patient.intake_id}",
                    event_type="intake",
                    date=patient.created_at,
                    title="Patient Intake Created",
                    description=f"Patient {patient.name} (UHID: {patient.uhid}) registered in the system",
                    status="completed",
                    related_id=patient.intake_id,
                    metadata={
                        "age": patient.age,
                        "sex": patient.sex,
                        "uhid": patient.uhid,
                        "contact": patient.contact_number
                    }
                ))
        
        # 2. TRAVEL HISTORY EVENTS
        if not filter_types or 'travel' in filter_types:
            travel_records = db.query(TravelHistory).filter(
                TravelHistory.intake_id == patient_intake_id
            ).all()
            
            for travel in travel_records:
                travel_date = format_date(travel.travel_date)
                if (not filter_start or travel_date >= filter_start) and \
                   (not filter_end or travel_date <= filter_end):
                    events.append(create_event(
                        event_id=f"travel-{travel.id}",
                        event_type="travel",
                        date=travel.travel_date,
                        title=f"Travel to {travel.destination}",
                        description=f"Patient traveled to {travel.destination} ({travel.country}). Purpose: {travel.purpose}. Duration: {travel.duration_days} days",
                        status="completed",
                        related_id=str(travel.id),
                        metadata={
                            "destination": travel.destination,
                            "country": travel.country,
                            "purpose": travel.purpose,
                            "duration_days": travel.duration_days
                        }
                    ))
        
        # 3. FAMILY HISTORY EVENTS
        if not filter_types or 'family_history' in filter_types:
            family_records = db.query(FamilyHistory).filter(
                FamilyHistory.intake_id == patient_intake_id
            ).all()
            
            for family in family_records:
                # Use patient intake date for family history (since no specific date)
                family_date = format_date(patient.created_at)
                if (not filter_start or family_date >= filter_start) and \
                   (not filter_end or family_date <= filter_end):
                    events.append(create_event(
                        event_id=f"family-{family.id}",
                        event_type="family_history",
                        date=patient.created_at,
                        title=f"Family Medical History: {family.relation}",
                        description=f"{family.relation} - {family.condition}. Notes: {family.notes or 'N/A'}",
                        status="noted",
                        related_id=str(family.id),
                        metadata={
                            "relation": family.relation,
                            "condition": family.condition,
                            "notes": family.notes
                        }
                    ))
        
        # 4. TREATMENT PLAN EVENTS
        if not filter_types or 'treatment_plan' in filter_types:
            treatment_plans = db.query(TreatmentPlan).filter(
                TreatmentPlan.patient_intake_id == patient_intake_id
            ).all()
            
            for plan in treatment_plans:
                plan_date = format_date(plan.start_date or plan.created_at)
                if (not filter_start or plan_date >= filter_start) and \
                   (not filter_end or plan_date <= filter_end):
                    events.append(create_event(
                        event_id=f"treatment-{plan.plan_id}",
                        event_type="treatment_plan",
                        date=plan.start_date or plan.created_at,
                        title=f"Treatment Plan: {plan.primary_diagnosis}",
                        description=f"Treatment plan created for {plan.primary_diagnosis} (ICD: {plan.icd_code}). Goals: {plan.treatment_goals[:100] if plan.treatment_goals else 'N/A'}",
                        status=plan.status,
                        related_id=plan.plan_id,
                        metadata={
                            "diagnosis": plan.primary_diagnosis,
                            "icd_code": plan.icd_code,
                            "status": plan.status,
                            "medication_count": len(plan.medications),
                            "followup_count": len(plan.follow_ups)
                        }
                    ))
        
        # 5. MEDICATION EVENTS
        if not filter_types or 'medication' in filter_types:
            treatment_plans = db.query(TreatmentPlan).filter(
                TreatmentPlan.patient_intake_id == patient_intake_id
            ).all()
            
            for plan in treatment_plans:
                for med in plan.medications:
                    med_date = format_date(med.prescribed_date or med.start_date or plan.created_at)
                    if (not filter_start or med_date >= filter_start) and \
                       (not filter_end or med_date <= filter_end):
                        status = "active" if med.is_active else "discontinued"
                        events.append(create_event(
                            event_id=f"medication-{med.id}",
                            event_type="medication",
                            date=med.prescribed_date or med.start_date or plan.created_at,
                            title=f"Medication: {med.medication_name}",
                            description=f"{med.medication_name} ({med.generic_name or 'N/A'}) - {med.dosage}, {med.route}, {med.frequency}. Instructions: {med.instructions[:100] if med.instructions else 'N/A'}",
                            status=status,
                            related_id=str(med.id),
                            metadata={
                                "medication_name": med.medication_name,
                                "generic_name": med.generic_name,
                                "dosage": med.dosage,
                                "route": med.route,
                                "frequency": med.frequency,
                                "duration_days": med.duration_days,
                                "is_active": med.is_active,
                                "treatment_plan_id": plan.plan_id
                            }
                        ))
                    
                    # Add discontinuation event if applicable
                    if not med.is_active and med.discontinuation_date:
                        disc_date = format_date(med.discontinuation_date)
                        if (not filter_start or disc_date >= filter_start) and \
                           (not filter_end or disc_date <= filter_end):
                            events.append(create_event(
                                event_id=f"medication-disc-{med.id}",
                                event_type="medication",
                                date=med.discontinuation_date,
                                title=f"Medication Discontinued: {med.medication_name}",
                                description=f"{med.medication_name} discontinued. Reason: {med.discontinuation_reason or 'Not specified'}",
                                status="discontinued",
                                related_id=str(med.id),
                                metadata={
                                    "medication_name": med.medication_name,
                                    "reason": med.discontinuation_reason
                                }
                            ))
        
        # 6. FOLLOW-UP APPOINTMENT EVENTS
        if not filter_types or 'follow_up' in filter_types:
            treatment_plans = db.query(TreatmentPlan).filter(
                TreatmentPlan.patient_intake_id == patient_intake_id
            ).all()
            
            for plan in treatment_plans:
                for followup in plan.follow_ups:
                    followup_date = format_date(followup.scheduled_date)
                    if (not filter_start or followup_date >= filter_start) and \
                       (not filter_end or followup_date <= filter_end):
                        events.append(create_event(
                            event_id=f"followup-{followup.id}",
                            event_type="follow_up",
                            date=followup.scheduled_date,
                            title=f"Follow-up: {followup.appointment_type}",
                            description=f"{followup.appointment_type} at {followup.location or 'N/A'} with {followup.provider or 'N/A'}. Status: {followup.status}",
                            status=followup.status,
                            related_id=str(followup.id),
                            metadata={
                                "appointment_type": followup.appointment_type,
                                "location": followup.location,
                                "provider": followup.provider,
                                "status": followup.status,
                                "outcome": followup.outcome,
                                "treatment_plan_id": plan.plan_id
                            }
                        ))
        
        # 7. MONITORING RECORD EVENTS
        if not filter_types or 'monitoring' in filter_types:
            treatment_plans = db.query(TreatmentPlan).filter(
                TreatmentPlan.patient_intake_id == patient_intake_id
            ).all()
            
            for plan in treatment_plans:
                for record in plan.monitoring_records:
                    record_date = format_date(record.record_date)
                    if (not filter_start or record_date >= filter_start) and \
                       (not filter_end or record_date <= filter_end):
                        events.append(create_event(
                            event_id=f"monitoring-{record.id}",
                            event_type="monitoring",
                            date=record.record_date,
                            title=f"Monitoring: {record.monitoring_type}",
                            description=f"{record.monitoring_type} - Assessment: {record.assessment[:100] if record.assessment else 'N/A'}. Concerns: {record.concerns or 'None'}",
                            status="completed",
                            related_id=str(record.id),
                            metadata={
                                "monitoring_type": record.monitoring_type,
                                "measurements": record.measurements,
                                "concerns": record.concerns,
                                "action_taken": record.action_taken,
                                "recorded_by": record.recorded_by,
                                "treatment_plan_id": plan.plan_id
                            }
                        ))
        
        # Sort events by date (most recent first)
        events.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "patient_intake_id": patient_intake_id,
            "patient_name": patient.name,
            "total_events": len(events),
            "events": events
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating patient timeline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate timeline: {str(e)}")


@router.get("/event-types")
async def get_event_types():
    """Get available event types for filtering"""
    return {
        "event_types": [
            {"value": "intake", "label": "Patient Intake", "icon": "PersonAdd"},
            {"value": "travel", "label": "Travel History", "icon": "Flight"},
            {"value": "family_history", "label": "Family History", "icon": "FamilyRestroom"},
            {"value": "treatment_plan", "label": "Treatment Plan", "icon": "LocalHospital"},
            {"value": "medication", "label": "Medications", "icon": "Medication"},
            {"value": "follow_up", "label": "Follow-up Appointments", "icon": "EventNote"},
            {"value": "monitoring", "label": "Monitoring Records", "icon": "Monitoring"}
        ]
    }
