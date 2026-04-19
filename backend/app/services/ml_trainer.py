"""
ML Model Trainer Service

Trains logistic regression model on historical patient data to predict readmission risk.
Runs as a background job to continuously improve predictions.
"""

import logging
import pickle
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Global service instance
_ml_trainer = None


class MLTrainer:
    """Service for training ML models on historical data"""

    def __init__(self, model_save_path: str = "backend/data/models/readmission_model.pkl"):
        """Initialize trainer"""
        self.model_save_path = model_save_path
        self.feature_names = [
            'age',
            'bmi',
            'gender_male',
            'comorbidity_count',
            'medication_count',
            'diagnosis_complexity',
            'previous_readmissions',
            'has_diabetes',
            'has_hypertension',
            'has_heart_disease',
            'family_history_score'
        ]
        # Ensure directory exists
        Path(self.model_save_path).parent.mkdir(parents=True, exist_ok=True)

    def train_readmission_model(self, db: Session, min_samples: int = 100) -> Dict:
        """
        Train logistic regression model on historical data

        Args:
            db: Database session
            min_samples: Minimum samples required to train

        Returns:
            Training results dict
        """
        try:
            logger.info("[ML] Starting readmission model training...")

            # Extract training data
            X, y, sample_count = self._extract_training_data(db)

            if len(X) < min_samples:
                logger.warning(f"[ML] Insufficient data: {len(X)} samples (need {min_samples})")
                return {
                    "status": "insufficient_data",
                    "message": f"Need {min_samples} samples, have {len(X)}",
                    "samples": len(X)
                }

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Train model
            model = LogisticRegression(max_iter=10000, random_state=42, solver='lbfgs')
            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]

            metrics = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "precision": float(precision_score(y_test, y_pred, zero_division=0)),
                "recall": float(recall_score(y_test, y_pred, zero_division=0)),
                "auc_roc": float(roc_auc_score(y_test, y_pred_proba)) if len(np.unique(y_test)) > 1 else 0.0,
                "test_samples": len(X_test),
                "train_samples": len(X_train),
                "total_samples": len(X)
            }

            # Cross-validation
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
            metrics["cv_mean_auc"] = float(cv_scores.mean())
            metrics["cv_std_auc"] = float(cv_scores.std())

            # Save model
            self._save_model(model, metrics)

            logger.info(f"[ML] Model trained successfully. Accuracy: {metrics['accuracy']:.3f}, AUC: {metrics['auc_roc']:.3f}")

            return {
                "status": "success",
                "message": "Model trained successfully",
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"[ML] Training failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _extract_training_data(self, db: Session) -> Tuple[np.ndarray, np.ndarray, int]:
        """
        Extract features and labels from historical patient data

        Returns:
            Tuple of (X, y, sample_count)
        """
        from app.models import PatientIntake, TreatmentPlan

        # Query all treatment plans completed in last 6 months
        cutoff_date = datetime.utcnow() - timedelta(days=180)

        treatment_plans = db.query(TreatmentPlan).filter(
            TreatmentPlan.end_date > cutoff_date
        ).all()

        X = []
        y = []

        for plan in treatment_plans:
            try:
                # Get patient data
                patient = db.query(PatientIntake).filter(
                    PatientIntake.intake_id == plan.patient_intake_id
                ).first()

                if not patient:
                    continue

                # Extract features
                features = self._extract_patient_features(patient, plan, db)

                # Determine label (was there a readmission within 30 days?)
                label = self._check_readmission(patient, plan, db)

                X.append(features)
                y.append(1 if label else 0)

            except Exception as e:
                logger.debug(f"[ML] Skipping patient: {e}")
                continue

        return np.array(X), np.array(y), len(X)

    def _extract_patient_features(self, patient: 'PatientIntake', plan: 'TreatmentPlan', db: Session) -> List[float]:
        """Extract feature vector from patient and treatment plan"""
        features = {}

        # Demographics (normalize to 0-1)
        try:
            age = int(patient.age) if patient.age else 60
        except Exception:
            age = 60
        features['age'] = min(age / 100.0, 1.0)

        try:
            bmi = patient.bmi if patient.bmi else 25
        except Exception:
            bmi = 25
        features['bmi'] = min(bmi / 50.0, 1.0)

        gender = patient.gender if patient.gender else 'M'
        features['gender_male'] = 1.0 if gender.lower() in ['m', 'male'] else 0.0

        # Comorbidities
        from app.models import FamilyHistory
        family_history_records = db.query(FamilyHistory).filter(
            FamilyHistory.patient_intake_id == patient.id
        ).all()

        comorbidity_count = len(family_history_records)
        features['comorbidity_count'] = min(comorbidity_count / 5.0, 1.0)

        # Check for high-risk conditions
        conditions_str = " ".join([r.condition.lower() for r in family_history_records])
        features['has_diabetes'] = 1.0 if 'diabetes' in conditions_str else 0.0
        features['has_hypertension'] = 1.0 if 'hypertension' in conditions_str else 0.0
        features['has_heart_disease'] = 1.0 if ('heart' in conditions_str or 'cardiac' in conditions_str) else 0.0
        features['family_history_score'] = min(comorbidity_count / 10.0, 1.0)

        # Medications
        from app.models import Medication, TreatmentPlan
        medication_count = db.query(Medication).filter(
            Medication.treatment_plan_id == plan.id,
            Medication.is_active.is_(True)
        ).count()
        features['medication_count'] = min(medication_count / 10.0, 1.0)

        # Diagnosis complexity (count ICD codes in same pattern)
        icd_code = plan.icd_code if plan.icd_code else ""
        diagnosis_complexity = 1 if icd_code else 1
        features['diagnosis_complexity'] = min(diagnosis_complexity / 5.0, 1.0)

        # Previous readmissions
        previous_plans = db.query(TreatmentPlan).filter(
            TreatmentPlan.patient_intake_id == plan.patient_intake_id,
            TreatmentPlan.id != plan.id,
            TreatmentPlan.start_date < plan.start_date
        ).count()
        features['previous_readmissions'] = min(previous_plans / 3.0, 1.0)

        # Return feature vector in order
        return [features.get(name, 0.0) for name in self.feature_names]

    def _check_readmission(self, patient: 'PatientIntake', plan: 'TreatmentPlan', db: Session) -> bool:
        """Check if patient was readmitted within 30 days"""
        from app.models import TreatmentPlan as TP

        # Look for another treatment plan starting within 30 days of discharge
        discharge_date = plan.end_date if plan.end_date else datetime.utcnow()
        thirty_days_later = discharge_date + timedelta(days=30)

        readmission = db.query(TP).filter(
            TP.patient_intake_id == plan.patient_intake_id,
            TP.id != plan.id,
            TP.start_date >= discharge_date,
            TP.start_date <= thirty_days_later
        ).first()

        return readmission is not None

    def _save_model(self, model, metrics: Dict):
        """Save trained model to disk"""
        try:
            data = {
                "model": model,
                "feature_names": self.feature_names,
                "metadata": {
                    "model_type": "Logistic Regression",
                    "trained_at": datetime.utcnow().isoformat(),
                    "last_trained": datetime.utcnow().isoformat(),
                    **metrics
                }
            }

            with open(self.model_save_path, 'wb') as f:
                pickle.dump(data, f)

            logger.info(f"[ML] Model saved to {self.model_save_path}")
        except Exception as e:
            logger.error(f"[ML] Failed to save model: {e}")


def get_ml_trainer() -> MLTrainer:
    """Factory function to get singleton service instance"""
    global _ml_trainer
    if _ml_trainer is None:
        _ml_trainer = MLTrainer()
    return _ml_trainer


if __name__ == "__main__":
    # Simulated test without database
    print("[TEST] ML Trainer Service")
    print("=" * 50)
    print("Run with: python -m app.services.ml_trainer")
    print("Connect to database to test training")
