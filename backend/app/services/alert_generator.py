"""
Alert Generator Service

Generates clinical alerts based on prediction results, drug interactions, lab abnormalities, etc.
Stores alerts in database and triggers notifications.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json

logger = logging.getLogger(__name__)

# Global service instance
_alert_generator = None


class AlertGenerator:
    """Service for generating and managing clinical alerts"""

    def __init__(self):
        """Initialize alert generator"""
        pass

    def generate_readmission_alert(
        self,
        db: Session,
        patient_intake_id: int,
        treatment_plan_id: int,
        risk_score: float,
        risk_factors: List[str],
        recommended_actions: List[str],
        severity: str = "high"
    ) -> Dict:
        """
        Generate readmission risk alert

        Args:
            db: Database session
            patient_intake_id: Patient ID
            treatment_plan_id: Treatment plan ID
            risk_score: Risk probability (0-1)
            risk_factors: List of risk factors
            recommended_actions: List of recommended actions
            severity: Alert severity

        Returns:
            Created alert dict
        """
        from app.models import Alert

        try:
            # Determine severity from risk score if not specified
            if risk_score >= 0.7:
                severity = "critical"
            elif risk_score >= 0.5:
                severity = "high"
            elif risk_score >= 0.3:
                severity = "medium"
            else:
                severity = "low"

            # Format alert description
            description = f"Patient at {risk_score*100:.1f}% risk of readmission within 30 days. "
            description += f"Key factors: {', '.join(risk_factors[:3])}"

            # Format risk factors
            risk_factors_json = [
                {"factor": factor, "importance": 0.9 - (i * 0.1), "priority": i + 1}
                for i, factor in enumerate(risk_factors[:5])
            ]

            # Create alert
            alert = Alert(
                patient_intake_id=patient_intake_id,
                treatment_plan_id=treatment_plan_id,
                alert_type="readmission_risk",
                severity=severity,
                title=f"High Readmission Risk - {severity.upper()}",
                description=description,
                recommended_action="\n".join(recommended_actions),
                risk_score=f"{risk_score:.3f}",
                risk_factors=risk_factors_json,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30)
            )

            db.add(alert)
            db.commit()
            db.refresh(alert)

            logger.info(f"[ALERT] Created readmission alert for patient {patient_intake_id}, severity={severity}")

            return {
                "alert_id": alert.id,
                "type": alert.alert_type,
                "severity": alert.severity,
                "risk_score": alert.risk_score,
                "created_at": alert.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"[ALERT] Error generating readmission alert: {e}")
            db.rollback()
            return {"error": str(e)}

    def generate_drug_interaction_alert(
        self,
        db: Session,
        patient_intake_id: int,
        treatment_plan_id: int,
        medications: List[str],
        interaction_details: Dict,
        severity: str = "high"
    ) -> Dict:
        """
        Generate drug interaction alert

        Args:
            db: Database session
            patient_intake_id: Patient ID
            treatment_plan_id: Treatment plan ID
            medications: List of interacting medications
            interaction_details: Details about interaction
            severity: Alert severity

        Returns:
            Created alert dict
        """
        from app.models import Alert

        try:
            description = f"Drug interaction detected: {' + '.join(medications)}"
            description += f"\nEffect: {interaction_details.get('effect', 'Unknown')}"

            alert = Alert(
                patient_intake_id=patient_intake_id,
                treatment_plan_id=treatment_plan_id,
                alert_type="drug_interaction",
                severity=severity,
                title=f"Drug Interaction - {severity.upper()}",
                description=description,
                recommended_action=interaction_details.get('recommendation', ''),
                risk_factors=[{"factor": med} for med in medications],
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=90)
            )

            db.add(alert)
            db.commit()
            db.refresh(alert)

            logger.info(f"[ALERT] Created drug interaction alert for patient {patient_intake_id}")

            return {
                "alert_id": alert.id,
                "type": alert.alert_type,
                "severity": alert.severity,
                "medications": medications,
                "created_at": alert.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"[ALERT] Error generating drug interaction alert: {e}")
            db.rollback()
            return {"error": str(e)}

    def generate_lab_abnormality_alert(
        self,
        db: Session,
        patient_intake_id: int,
        test_name: str,
        value: float,
        reference_range: str,
        severity: str = "medium"
    ) -> Dict:
        """
        Generate lab abnormality alert

        Args:
            db: Database session
            patient_intake_id: Patient ID
            test_name: Lab test name
            value: Test value
            reference_range: Normal range
            severity: Alert severity

        Returns:
            Created alert dict
        """
        from app.models import Alert

        try:
            description = f"Lab abnormality: {test_name} = {value} (normal: {reference_range})"

            alert = Alert(
                patient_intake_id=patient_intake_id,
                alert_type="lab_abnormality",
                severity=severity,
                title=f"Lab Abnormality: {test_name}",
                description=description,
                recommended_action="Review lab result and recommend follow-up testing if indicated",
                risk_factors=[{"factor": test_name, "value": value}],
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30)
            )

            db.add(alert)
            db.commit()
            db.refresh(alert)

            logger.info(f"[ALERT] Created lab abnormality alert for patient {patient_intake_id}: {test_name}")

            return {
                "alert_id": alert.id,
                "type": alert.alert_type,
                "severity": alert.severity,
                "test": test_name,
                "created_at": alert.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"[ALERT] Error generating lab abnormality alert: {e}")
            db.rollback()
            return {"error": str(e)}

    def get_alerts_for_patient(
        self,
        db: Session,
        patient_intake_id: int,
        include_acknowledged: bool = False,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get alerts for a patient

        Args:
            db: Database session
            patient_intake_id: Patient ID
            include_acknowledged: Include acknowledged alerts
            limit: Max results

        Returns:
            List of alert dicts
        """
        from app.models import Alert

        try:
            query = db.query(Alert).filter(
                Alert.patient_intake_id == patient_intake_id
            )

            if not include_acknowledged:
                query = query.filter(Alert.is_acknowledged == False)

            alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()

            return [
                {
                    "id": alert.id,
                    "type": alert.alert_type,
                    "severity": alert.severity,
                    "title": alert.title,
                    "description": alert.description,
                    "risk_score": alert.risk_score,
                    "is_acknowledged": alert.is_acknowledged,
                    "created_at": alert.created_at.isoformat(),
                    "expires_at": alert.expires_at.isoformat() if alert.expires_at else None
                }
                for alert in alerts
            ]

        except Exception as e:
            logger.error(f"[ALERT] Error retrieving alerts: {e}")
            return []

    def acknowledge_alert(
        self,
        db: Session,
        alert_id: int,
        user_id: int,
        notes: str = ""
    ) -> Dict:
        """
        Acknowledge an alert (mark as read)

        Args:
            db: Database session
            alert_id: Alert ID
            user_id: Acknowledging user ID
            notes: Acknowledgment notes

        Returns:
            Updated alert dict
        """
        from app.models import Alert

        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()

            if not alert:
                return {"error": "Alert not found"}

            alert.is_acknowledged = True
            alert.acknowledged_by_id = user_id
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledgment_notes = notes

            db.commit()
            db.refresh(alert)

            logger.info(f"[ALERT] Alert {alert_id} acknowledged by user {user_id}")

            return {
                "alert_id": alert.id,
                "acknowledged": True,
                "acknowledged_at": alert.acknowledged_at.isoformat()
            }

        except Exception as e:
            logger.error(f"[ALERT] Error acknowledging alert: {e}")
            db.rollback()
            return {"error": str(e)}

    def get_high_risk_patients(
        self,
        db: Session,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get list of high-risk patients with pending alerts

        Args:
            db: Database session
            limit: Max results

        Returns:
            List of patient dicts with alert counts
        """
        from app.models import Alert, PatientIntake

        try:
            # Get patients with unacknowledged critical/high severity alerts
            high_risk = db.query(
                PatientIntake.id,
                PatientIntake.name,
                PatientIntake.intake_id,
                Alert.severity
            ).join(
                Alert, Alert.patient_intake_id == PatientIntake.id
            ).filter(
                Alert.is_acknowledged == False,
                Alert.severity.in_(['critical', 'high'])
            ).order_by(Alert.created_at.desc()).limit(limit).all()

            patients = {}
            for row in high_risk:
                patient_id = row[0]
                if patient_id not in patients:
                    patients[patient_id] = {
                        "patient_id": row[0],
                        "name": row[1],
                        "intake_id": row[2],
                        "alert_count": 0,
                        "highest_severity": None
                    }

                patients[patient_id]["alert_count"] += 1
                if not patients[patient_id]["highest_severity"] or row[3] == "critical":
                    patients[patient_id]["highest_severity"] = row[3]

            return list(patients.values())[:limit]

        except Exception as e:
            logger.error(f"[ALERT] Error retrieving high-risk patients: {e}")
            return []


def get_alert_generator() -> AlertGenerator:
    """Factory function to get singleton service instance"""
    global _alert_generator
    if _alert_generator is None:
        _alert_generator = AlertGenerator()
    return _alert_generator
