from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from typing import Dict, List, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

from app.database import get_db
from app.database.models import PatientIntake, TravelHistory, FamilyHistory, TreatmentPlan, Medication, FollowUp, TreatmentStatus

logger = logging.getLogger(__name__)
router = APIRouter()


# ========================= PYDANTIC MODELS =========================

class DemographicsData(BaseModel):
    total_patients: int
    age_distribution: Dict[str, int]
    gender_distribution: Dict[str, int]
    blood_type_distribution: Dict[str, int]
    average_age: float
    
class DiseaseTrendsData(BaseModel):
    total_diagnoses: int
    top_diagnoses: List[Dict[str, Any]]
    diagnoses_by_month: List[Dict[str, Any]]
    icd_code_distribution: List[Dict[str, Any]]
    
class TreatmentOutcomesData(BaseModel):
    total_treatment_plans: int
    active_treatments: int
    completed_treatments: int
    discontinued_treatments: int
    on_hold_treatments: int
    treatment_status_distribution: Dict[str, int]
    average_treatment_duration: float
    medication_statistics: Dict[str, Any]
    follow_up_statistics: Dict[str, Any]
    
class PerformanceMetricsData(BaseModel):
    patient_intake_rate: Dict[str, Any]
    risk_assessment_summary: Dict[str, int]
    travel_history_summary: Dict[str, Any]
    family_history_summary: Dict[str, Any]
    
class AnalyticsDashboardResponse(BaseModel):
    demographics: DemographicsData
    disease_trends: DiseaseTrendsData
    treatment_outcomes: TreatmentOutcomesData
    performance_metrics: PerformanceMetricsData
    generated_at: datetime


# ========================= HELPER FUNCTIONS =========================

def get_age_group(age: int) -> str:
    """Categorize age into groups"""
    if age < 18:
        return "0-17"
    elif age < 30:
        return "18-29"
    elif age < 40:
        return "30-39"
    elif age < 50:
        return "40-49"
    elif age < 60:
        return "50-59"
    elif age < 70:
        return "60-69"
    else:
        return "70+"


# ========================= ANALYTICS ENDPOINTS =========================

@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(db: Session = Depends(get_db)):
    """
    Get comprehensive analytics dashboard data.
    
    Includes:
    - Patient demographics (age, gender, blood type)
    - Disease trends (top diagnoses, monthly trends)
    - Treatment outcomes (status, duration, medications)
    - Performance metrics (intake rate, risk levels)
    """
    try:
        # ===================== DEMOGRAPHICS =====================
        
        # Total patients
        total_patients = db.query(PatientIntake).count()
        
        # Age distribution
        patients = db.query(PatientIntake).all()
        age_groups = {"0-17": 0, "18-29": 0, "30-39": 0, "40-49": 0, 
                      "50-59": 0, "60-69": 0, "70+": 0}
        total_age = 0
        age_count = 0
        
        for patient in patients:
            try:
                age = int(patient.age)
                age_groups[get_age_group(age)] += 1
                total_age += age
                age_count += 1
            except (ValueError, TypeError):
                pass
        
        average_age = round(total_age / age_count, 1) if age_count > 0 else 0.0
        
        # Gender distribution
        gender_dist = db.query(
            PatientIntake.sex,
            func.count(PatientIntake.id).label('count')
        ).group_by(PatientIntake.sex).all()
        
        gender_distribution = {g.sex: g.count for g in gender_dist if g.sex}
        
        # Blood type distribution
        blood_type_dist = db.query(
            PatientIntake.blood_group,
            func.count(PatientIntake.id).label('count')
        ).group_by(PatientIntake.blood_group).all()
        
        blood_type_distribution = {bt.blood_group: bt.count for bt in blood_type_dist if bt.blood_group}
        
        demographics = DemographicsData(
            total_patients=total_patients,
            age_distribution=age_groups,
            gender_distribution=gender_distribution,
            blood_type_distribution=blood_type_distribution,
            average_age=average_age
        )
        
        # ===================== DISEASE TRENDS =====================
        
        # Get all treatment plans with diagnoses
        treatment_plans = db.query(TreatmentPlan).all()
        total_diagnoses = len(treatment_plans)
        
        # Top diagnoses
        diagnosis_counts: Dict[str, int] = {}
        icd_counts: Dict[str, Dict[str, Any]] = {}
        
        for plan in treatment_plans:
            if plan.primary_diagnosis:
                diagnosis = plan.primary_diagnosis.strip()
                diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1
                
                if plan.icd_code:
                    icd_key = f"{plan.icd_code} - {diagnosis}"
                    if icd_key not in icd_counts:
                        icd_counts[icd_key] = {
                            "icd_code": plan.icd_code,
                            "diagnosis": diagnosis,
                            "count": 0
                        }
                    icd_counts[icd_key]["count"] += 1
        
        # Sort and get top 10 diagnoses
        top_diagnoses = [
            {"diagnosis": k, "count": v, "percentage": round(v / total_diagnoses * 100, 1) if total_diagnoses > 0 else 0}
            for k, v in sorted(diagnosis_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # ICD code distribution (top 10)
        icd_distribution = sorted(
            list(icd_counts.values()),
            key=lambda x: x["count"],
            reverse=True
        )[:10]
        
        # Diagnoses by month (last 12 months)
        diagnoses_by_month = []
        current_date = datetime.now()
        
        for i in range(11, -1, -1):
            month_date = current_date - timedelta(days=i*30)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            count = db.query(TreatmentPlan).filter(
                TreatmentPlan.created_at >= month_start,
                TreatmentPlan.created_at <= month_end
            ).count()
            
            diagnoses_by_month.append({
                "month": month_start.strftime("%b %Y"),
                "count": count
            })
        
        disease_trends = DiseaseTrendsData(
            total_diagnoses=total_diagnoses,
            top_diagnoses=top_diagnoses,
            diagnoses_by_month=diagnoses_by_month,
            icd_code_distribution=icd_distribution
        )
        
        # ===================== TREATMENT OUTCOMES =====================
        
        total_treatment_plans = db.query(TreatmentPlan).count()
        
        # Status distribution
        status_counts = db.query(
            TreatmentPlan.status,
            func.count(TreatmentPlan.id).label('count')
        ).group_by(TreatmentPlan.status).all()
        
        status_distribution = {s.status: s.count for s in status_counts if s.status}
        
        active_treatments = status_distribution.get(TreatmentStatus.ACTIVE, 0)
        completed_treatments = status_distribution.get(TreatmentStatus.COMPLETED, 0)
        discontinued_treatments = status_distribution.get(TreatmentStatus.DISCONTINUED, 0)
        on_hold_treatments = status_distribution.get(TreatmentStatus.ON_HOLD, 0)
        
        # Average treatment duration (for completed treatments)
        completed_plans = db.query(TreatmentPlan).filter(
            TreatmentPlan.status == TreatmentStatus.COMPLETED,
            TreatmentPlan.start_date.isnot(None),
            TreatmentPlan.end_date.isnot(None)
        ).all()
        
        total_duration = 0
        duration_count = 0
        
        for plan in completed_plans:
            if plan.start_date and plan.end_date:
                duration = (plan.end_date - plan.start_date).days
                if duration > 0:
                    total_duration += duration
                    duration_count += 1
        
        average_duration = round(total_duration / duration_count, 1) if duration_count > 0 else 0.0
        
        # Medication statistics
        total_medications = db.query(Medication).count()
        active_medications = db.query(Medication).filter(Medication.is_active == True).count()
        discontinued_medications = db.query(Medication).filter(Medication.is_active == False).count()
        
        medication_statistics = {
            "total": total_medications,
            "active": active_medications,
            "discontinued": discontinued_medications,
            "discontinuation_rate": round(discontinued_medications / total_medications * 100, 1) if total_medications > 0 else 0.0
        }
        
        # Follow-up statistics
        total_followups = db.query(FollowUp).count()
        
        followup_status_counts = db.query(
            FollowUp.status,
            func.count(FollowUp.id).label('count')
        ).group_by(FollowUp.status).all()
        
        followup_status_dist = {s.status: s.count for s in followup_status_counts if s.status}
        
        follow_up_statistics = {
            "total": total_followups,
            "scheduled": followup_status_dist.get("scheduled", 0),
            "completed": followup_status_dist.get("completed", 0),
            "missed": followup_status_dist.get("missed", 0),
            "cancelled": followup_status_dist.get("cancelled", 0),
            "completion_rate": round(
                followup_status_dist.get("completed", 0) / total_followups * 100, 1
            ) if total_followups > 0 else 0.0
        }
        
        treatment_outcomes = TreatmentOutcomesData(
            total_treatment_plans=total_treatment_plans,
            active_treatments=active_treatments,
            completed_treatments=completed_treatments,
            discontinued_treatments=discontinued_treatments,
            on_hold_treatments=on_hold_treatments,
            treatment_status_distribution=status_distribution,
            average_treatment_duration=average_duration,
            medication_statistics=medication_statistics,
            follow_up_statistics=follow_up_statistics
        )
        
        # ===================== PERFORMANCE METRICS =====================
        
        # Patient intake rate (last 12 months)
        intake_by_month = []
        
        for i in range(11, -1, -1):
            month_date = current_date - timedelta(days=i*30)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            count = db.query(PatientIntake).filter(
                PatientIntake.created_at >= month_start,
                PatientIntake.created_at <= month_end
            ).count()
            
            intake_by_month.append({
                "month": month_start.strftime("%b %Y"),
                "count": count
            })
        
        # Calculate average monthly intake
        total_intakes = sum(m["count"] for m in intake_by_month)
        average_monthly_intake = round(total_intakes / 12, 1) if total_intakes > 0 else 0.0
        
        patient_intake_rate = {
            "monthly_data": intake_by_month,
            "average_monthly": average_monthly_intake,
            "total_last_year": total_intakes
        }
        
        # Risk assessment summary (would need risk calculation API)
        # For now, provide placeholder based on age
        risk_summary = {
            "high": sum(1 for p in patients if int(p.age) > 60 if p.age and p.age.isdigit()),
            "medium": sum(1 for p in patients if 40 <= int(p.age) <= 60 if p.age and p.age.isdigit()),
            "low": sum(1 for p in patients if int(p.age) < 40 if p.age and p.age.isdigit())
        }
        
        # Travel history summary
        total_travel_records = db.query(TravelHistory).count()
        unique_countries = db.query(TravelHistory.country).distinct().count()
        
        # Top destinations
        top_destinations = db.query(
            TravelHistory.destination,
            TravelHistory.country,
            func.count(TravelHistory.id).label('count')
        ).group_by(TravelHistory.destination, TravelHistory.country).order_by(
            func.count(TravelHistory.id).desc()
        ).limit(5).all()
        
        travel_summary = {
            "total_records": total_travel_records,
            "unique_countries": unique_countries,
            "top_destinations": [
                {"destination": d.destination, "country": d.country, "count": d.count}
                for d in top_destinations
            ]
        }
        
        # Family history summary
        total_family_records = db.query(FamilyHistory).count()
        
        family_conditions = db.query(
            FamilyHistory.condition,
            func.count(FamilyHistory.id).label('count')
        ).group_by(FamilyHistory.condition).order_by(
            func.count(FamilyHistory.id).desc()
        ).limit(5).all()
        
        family_summary = {
            "total_records": total_family_records,
            "common_conditions": [
                {"condition": c.condition, "count": c.count}
                for c in family_conditions
            ]
        }
        
        performance_metrics = PerformanceMetricsData(
            patient_intake_rate=patient_intake_rate,
            risk_assessment_summary=risk_summary,
            travel_history_summary=travel_summary,
            family_history_summary=family_summary
        )
        
        # ===================== FINAL RESPONSE =====================
        
        return AnalyticsDashboardResponse(
            demographics=demographics,
            disease_trends=disease_trends,
            treatment_outcomes=treatment_outcomes,
            performance_metrics=performance_metrics,
            generated_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error generating analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")


@router.get("/demographics")
async def get_demographics(db: Session = Depends(get_db)):
    """Get patient demographics data only"""
    try:
        dashboard = await get_analytics_dashboard(db)
        return dashboard.demographics
    except Exception as e:
        logger.error(f"Error fetching demographics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/disease-trends")
async def get_disease_trends(db: Session = Depends(get_db)):
    """Get disease trends data only"""
    try:
        dashboard = await get_analytics_dashboard(db)
        return dashboard.disease_trends
    except Exception as e:
        logger.error(f"Error fetching disease trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/treatment-outcomes")
async def get_treatment_outcomes(db: Session = Depends(get_db)):
    """Get treatment outcomes data only"""
    try:
        dashboard = await get_analytics_dashboard(db)
        return dashboard.treatment_outcomes
    except Exception as e:
        logger.error(f"Error fetching treatment outcomes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-metrics")
async def get_performance_metrics(db: Session = Depends(get_db)):
    """Get performance metrics data only"""
    try:
        dashboard = await get_analytics_dashboard(db)
        return dashboard.performance_metrics
    except Exception as e:
        logger.error(f"Error fetching performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
