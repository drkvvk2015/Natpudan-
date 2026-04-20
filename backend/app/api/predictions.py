"""
Predictions API Router

Exposes ML prediction endpoints for readmission risk, drug interactions, etc.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.database import SessionLocal
from app.services.readmission_predictor import get_readmission_predictor
from app.services.alert_generator import get_alert_generator
from app.services.ml_trainer import get_ml_trainer
from app.models import PatientIntake, TreatmentPlan, Alert

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predictions", tags=["predictions"])


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/readmission-risk")
def predict_readmission_risk(
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict:
    """
    Predict 30-day readmission risk for a patient

    Args:
        payload: {patient_intake_id: int, treatment_plan_id: optional int}

    Returns:
        {
            risk_score, risk_level, confidence,
            feature_importance, top_risk_factors, recommended_interventions
        }
    """
    try:
        patient_intake_id = payload.get("patient_intake_id")
        treatment_plan_id = payload.get("treatment_plan_id")

        if not patient_intake_id:
            raise HTTPException(status_code=400, detail="patient_intake_id required")

        # Get patient data
        patient = db.query(PatientIntake).filter(
            PatientIntake.id == patient_intake_id
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Build patient data dict
        patient_data = {
            "age": patient.age,
            "bmi": patient.bmi,
            "gender": patient.gender or "M",
            "family_history": [],
            "medication_count": 0,
            "diagnosis_complexity": 1,
            "previous_readmissions": 0
        }

        # Get family history
        try:
            from app.models import FamilyHistory
            family_records = db.query(FamilyHistory).filter(
                FamilyHistory.patient_intake_id == patient_intake_id
            ).all()
            patient_data["family_history"] = [r.condition for r in family_records]
        except Exception:
            pass  # nosec B110

        # Get current/last treatment plan
        if not treatment_plan_id:
            from app.models import TreatmentPlan
            plan = db.query(TreatmentPlan).filter(
                TreatmentPlan.patient_intake_id == patient.intake_id
            ).order_by(TreatmentPlan.start_date.desc()).first()
            treatment_plan_id = plan.id if plan else None

        if treatment_plan_id:
            try:
                from app.models import Medication, TreatmentPlan
                plan = db.query(TreatmentPlan).filter(
                    TreatmentPlan.id == treatment_plan_id
                ).first()

                if plan:
                    # Count active medications
                    meds = db.query(Medication).filter(
                        Medication.treatment_plan_id == treatment_plan_id,
                        Medication.is_active.is_(True)
                    ).all()
                    patient_data["medication_count"] = len(meds)

                    # Count previous plans
                    prev_plans = db.query(TreatmentPlan).filter(
                        TreatmentPlan.patient_intake_id == patient.intake_id,
                        TreatmentPlan.id < treatment_plan_id
                    ).count()
                    patient_data["previous_readmissions"] = max(0, prev_plans - 1)
            except Exception:
                pass  # nosec B110

        # Predict
        predictor = get_readmission_predictor()
        prediction = predictor.predict_risk(patient_data)

        # Generate alert if high risk
        if treatment_plan_id and prediction.get("risk_score", 0) >= 0.5:
            try:
                alert_gen = get_alert_generator()
                alert_result = alert_gen.generate_readmission_alert(
                    db=db,
                    patient_intake_id=patient_intake_id,
                    treatment_plan_id=treatment_plan_id,
                    risk_score=prediction["risk_score"],
                    risk_factors=prediction.get("top_risk_factors", []),
                    recommended_actions=prediction.get("recommended_interventions", []),
                    severity="critical" if prediction["risk_score"] >= 0.7 else "high"
                )
                prediction["alert"] = alert_result
            except Exception as e:
                logger.warning(f"[PREDICTIONS] Failed to generate alert: {e}")

        return {
            "success": True,
            "patient_id": patient_intake_id,
            **prediction
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[PREDICTIONS] Error predicting readmission: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/readmission-risk/{patient_intake_id}")
def get_readmission_risk(
    patient_intake_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Quick endpoint to predict readmission for a patient by ID

    Args:
        patient_intake_id: Patient ID

    Returns:
        Prediction result
    """
    return predict_readmission_risk(
        {"patient_intake_id": patient_intake_id},
        db
    )


@router.get("/model-stats")
def get_model_stats() -> Dict:
    """
    Get readmission model statistics and metadata

    Returns:
        Model info: type, status, features, metrics, etc.
    """
    try:
        predictor = get_readmission_predictor()
        return {
            "success": True,
            "model": predictor.get_model_stats()
        }
    except Exception as e:
        logger.error(f"[PREDICTIONS] Error getting model stats: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/train-model")
def train_model(db: Session = Depends(get_db)) -> Dict:
    """
    Trigger model retraining on historical data

    Returns:
        Training results: status, metrics, timestamp
    """
    try:
        trainer = get_ml_trainer()
        result = trainer.train_readmission_model(db)

        if result.get("status") == "success":
            logger.info("[PREDICTIONS] Model training completed successfully")
            logger.info(f"  Accuracy: {result['metrics']['accuracy']:.3f}")
            logger.info(f"  AUC-ROC: {result['metrics']['auc_roc']:.3f}")
            return {"success": True, **result}
        else:
            return {"success": False, **result}

    except Exception as e:
        logger.error(f"[PREDICTIONS] Error training model: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/alerts/high-risk-patients")
def get_high_risk_patients(
    limit: int = 10,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get list of high-risk patients with pending alerts

    Args:
        limit: Max patients to return

    Returns:
        List of high-risk patients with alert info
    """
    try:
        alert_gen = get_alert_generator()
        patients = alert_gen.get_high_risk_patients(db, limit)

        return {
            "success": True,
            "high_risk_patients": patients,
            "count": len(patients)
        }
    except Exception as e:
        logger.error(f"[PREDICTIONS] Error getting high-risk patients: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/alerts/patient/{patient_intake_id}")
def get_patient_alerts(
    patient_intake_id: int,
    include_acknowledged: bool = False,
    limit: int = 20,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get alerts for a specific patient

    Args:
        patient_intake_id: Patient ID
        include_acknowledged: Include acknowledged alerts
        limit: Max alerts

    Returns:
        List of alerts
    """
    try:
        alert_gen = get_alert_generator()
        alerts = alert_gen.get_alerts_for_patient(
            db,
            patient_intake_id,
            include_acknowledged,
            limit
        )

        return {
            "success": True,
            "patient_id": patient_intake_id,
            "alerts": alerts,
            "count": len(alerts)
        }
    except Exception as e:
        logger.error(f"[PREDICTIONS] Error getting patient alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict:
    """
    Acknowledge/dismiss an alert

    Args:
        alert_id: Alert ID
        payload: {user_id: int, notes: optional str}

    Returns:
        Updated alert
    """
    try:
        user_id = payload.get("user_id")
        notes = payload.get("notes", "")

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id required")

        alert_gen = get_alert_generator()
        result = alert_gen.acknowledge_alert(db, alert_id, user_id, notes)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {
            "success": True,
            **result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[PREDICTIONS] Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/alerts/recent")
def get_recent_alerts(
    limit: int = 20,
    include_acknowledged: bool = False,
    db: Session = Depends(get_db)
) -> Dict:
    """Return recent alerts for dashboard-style widgets."""
    try:
        query = db.query(Alert).order_by(Alert.created_at.desc())
        if not include_acknowledged:
            query = query.filter(Alert.is_acknowledged == False)
        alerts = query.limit(limit).all()
        return {
            "success": True,
            "alerts": [
                {
                    "id": alert.id,
                    "patient_intake_id": alert.patient_intake_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "description": alert.description,
                    "recommended_action": alert.recommended_action,
                    "is_acknowledged": alert.is_acknowledged,
                    "created_at": alert.created_at.isoformat() if alert.created_at else None,
                }
                for alert in alerts
            ],
            "count": len(alerts)
        }
    except Exception as e:
        logger.error(f"[PREDICTIONS] Error getting recent alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
