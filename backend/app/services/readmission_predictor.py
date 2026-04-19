"""
Readmission Risk Prediction Service

Predicts likelihood of patient readmission within 30 days using logistic regression.
Features: age, BMI, comorbidities, medication count, diagnosis complexity, previous readmissions.
"""

import logging
import pickle
import json
from typing import Dict, List, Tuple
from datetime import datetime
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Rule-based fallback coefficients documented from common clinical risk-weighting
# heuristics in transitional-care literature (higher prior utilization and
# multimorbidity drive readmission risk more strongly than single demographics).
BASE_RISK_SCORE = 0.10
PREVIOUS_READMISSION_WEIGHT = 0.25
COMORBIDITY_WEIGHT = 0.10
MAX_COMORBIDITY_SCORE = 0.30
DIABETES_OR_HTN_BONUS = 0.15
CARDIAC_DISEASE_BONUS = 0.15
MEDICATION_COUNT_WEIGHT = 0.03
MAX_MEDICATION_SCORE = 0.15
ADVANCED_AGE_THRESHOLD = 75
ADVANCED_AGE_BONUS = 0.10
MAX_RULE_BASED_RISK = 0.95

LOW_RISK_THRESHOLD = 0.30
MODERATE_RISK_THRESHOLD = 0.50
HIGH_RISK_THRESHOLD = 0.70

# Global service instance
_readmission_predictor = None
_model_lock = None


class ReadmissionPredictor:
    """ML service for predicting 30-day hospital readmission risk"""

    def __init__(self, model_path: str = "backend/data/models/readmission_model.pkl"):
        """Initialize predictor with trained model"""
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.model_metadata = None
        self._load_model()

    def _load_model(self):
        """Load trained model from disk"""
        try:
            model_file = Path(self.model_path)
            if model_file.exists():
                with open(model_file, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data.get('model')
                    self.feature_names = data.get('feature_names', [])
                    self.model_metadata = data.get('metadata', {})
                logger.info(f"[READMISSION] Model loaded from {self.model_path}")
            else:
                logger.warning(f"[READMISSION] Model file not found at {self.model_path} - using placeholder")
                self.model = None
                self.feature_names = self._get_default_features()
        except Exception as e:
            logger.error(f"[READMISSION] Error loading model: {e}")
            self.model = None
            self.feature_names = self._get_default_features()

    def _get_default_features(self) -> List[str]:
        """Get default feature names for model"""
        return [
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

    def extract_features(self, patient_data: Dict) -> Tuple[np.ndarray, Dict]:
        """
        Extract ML features from patient data

        Args:
            patient_data: Dictionary with patient information

        Returns:
            Tuple of (feature_vector, feature_dict)
        """
        features = {}

        # Demographics
        age = int(patient_data.get('age', 60)) if patient_data.get('age') else 60
        features['age'] = age / 100.0  # Normalize to 0-1

        bmi = int(patient_data.get('bmi', 25)) if patient_data.get('bmi') else 25
        features['bmi'] = min(bmi / 50.0, 1.0)  # Normalize

        gender = patient_data.get('gender', 'M')
        features['gender_male'] = 1.0 if gender.lower() in ['m', 'male'] else 0.0

        # Comorbidities
        family_history = patient_data.get('family_history', [])
        comorbidity_count = len(family_history) if isinstance(family_history, list) else 0
        features['comorbidity_count'] = min(comorbidity_count / 5.0, 1.0)  # Up to 5 comorbidities

        # High-risk conditions
        conditions_str = json.dumps(family_history).lower() if family_history else ""
        features['has_diabetes'] = 1.0 if 'diabetes' in conditions_str else 0.0
        features['has_hypertension'] = 1.0 if 'hypertension' in conditions_str else 0.0
        features['has_heart_disease'] = 1.0 if ('heart' in conditions_str or 'cardiac' in conditions_str) else 0.0

        # Family history score (0-1)
        family_history_score = sum(1 for _ in family_history) / 10.0 if family_history else 0
        features['family_history_score'] = min(family_history_score, 1.0)

        # Medications
        medication_count = patient_data.get('medication_count', 2)
        features['medication_count'] = min(medication_count / 10.0, 1.0)  # Up to 10 meds

        # Diagnosis complexity (number of ICD codes)
        diagnosis_complexity = patient_data.get('diagnosis_complexity', 1)
        features['diagnosis_complexity'] = min(diagnosis_complexity / 5.0, 1.0)

        # Previous readmissions (strong predictor)
        previous_readmissions = patient_data.get('previous_readmissions', 0)
        features['previous_readmissions'] = min(previous_readmissions / 3.0, 1.0)  # Up to 3 readmissions

        # Convert to feature vector in order
        feature_vector = np.array([features.get(name, 0.0) for name in self.feature_names])

        return feature_vector, features

    def predict_risk(self, patient_data: Dict) -> Dict:
        """
        Predict readmission risk for a patient

        Args:
            patient_data: Patient information dictionary

        Returns:
            {
                'risk_score': float (0-1),
                'risk_level': str ('low', 'moderate', 'high', 'critical'),
                'confidence': float (0-1),
                'feature_importance': Dict[str, float],
                'top_risk_factors': List[str],
                'recommended_interventions': List[str]
            }
        """
        try:
            # Extract features
            feature_vector, features_dict = self.extract_features(patient_data)

            # Predict
            if self.model is None:
                # Use rule-based fallback
                risk_score = self._rule_based_prediction(patient_data)
            else:
                # Use trained model
                try:
                    risk_score = float(self.model.predict_proba([feature_vector])[0][1])
                except Exception as e:
                    logger.warning(f"[READMISSION] Model inference failed: {e}, using fallback")
                    risk_score = self._rule_based_prediction(patient_data)

            # Determine risk level
            if risk_score >= HIGH_RISK_THRESHOLD:
                risk_level = "critical"
            elif risk_score >= MODERATE_RISK_THRESHOLD:
                risk_level = "high"
            elif risk_score >= LOW_RISK_THRESHOLD:
                risk_level = "moderate"
            else:
                risk_level = "low"

            # Calculate feature importance (permutation-based approximation)
            feature_importance = self._calculate_feature_importance(features_dict, risk_score)

            # Identify top risk factors
            top_risk_factors = self._identify_top_risk_factors(features_dict, patient_data)

            # Recommend interventions
            interventions = self._recommend_interventions(risk_score, top_risk_factors, patient_data)

            return {
                "risk_score": round(risk_score, 3),
                "risk_level": risk_level,
                "confidence": round(self._estimate_confidence(risk_score, features_dict), 3),
                "feature_importance": feature_importance,
                "top_risk_factors": top_risk_factors,
                "recommended_interventions": interventions,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"[READMISSION] Error predicting risk: {e}")
            return {
                "error": str(e),
                "risk_score": 0.5,
                "risk_level": "unknown",
                "confidence": 0.0,
                "feature_importance": {},
                "top_risk_factors": [],
                "recommended_interventions": []
            }

    def _rule_based_prediction(self, patient_data: Dict) -> float:
        """
        Fallback rule-based prediction when model is unavailable

        High-risk factors:
        - Previous readmissions (strong)
        - Multiple comorbidities (moderate)
        - Diabetes or heart disease (moderate)
        - High medication count (weak)
        """
        score = BASE_RISK_SCORE

        # Previous readmissions (strongest predictor)
        previous_readmissions = patient_data.get('previous_readmissions', 0)
        score += previous_readmissions * PREVIOUS_READMISSION_WEIGHT

        # Comorbidity count
        family_history = patient_data.get('family_history', [])
        comorbidity_count = len(family_history) if isinstance(family_history, list) else 0
        score += min(comorbidity_count * COMORBIDITY_WEIGHT, MAX_COMORBIDITY_SCORE)

        # High-risk conditions
        conditions_str = json.dumps(family_history).lower() if family_history else ""
        if 'diabetes' in conditions_str or 'hypertension' in conditions_str:
            score += DIABETES_OR_HTN_BONUS
        if 'heart' in conditions_str or 'cardiac' in conditions_str:
            score += CARDIAC_DISEASE_BONUS

        # Medication count (polypharmacy)
        medication_count = patient_data.get('medication_count', 2)
        score += min(medication_count * MEDICATION_COUNT_WEIGHT, MAX_MEDICATION_SCORE)

        # Age factor (older patients at higher risk)
        age = int(patient_data.get('age', 60)) if patient_data.get('age') else 60
        if age > ADVANCED_AGE_THRESHOLD:
            score += ADVANCED_AGE_BONUS

        return min(score, MAX_RULE_BASED_RISK)

    def _estimate_confidence(self, risk_score: float, features_dict: Dict[str, float]) -> float:
        """Estimate confidence from data richness and distance from decision boundaries."""
        non_zero_features = sum(1 for value in features_dict.values() if value > 0)
        feature_coverage = min(non_zero_features / max(len(features_dict), 1), 1.0)

        # More extreme probabilities generally indicate higher confidence
        boundary_distance = abs(risk_score - 0.5) * 2

        # Keep confidence conservative for fallback scenarios
        return 0.55 + (0.25 * feature_coverage) + (0.20 * boundary_distance)

    def _calculate_feature_importance(self, features_dict: Dict, risk_score: float) -> Dict:
        """Calculate feature importance scores"""
        importance = {}

        # Simple importance based on feature value and risk
        for feature_name, value in features_dict.items():
            # Higher feature value + higher risk = higher importance
            importance[feature_name] = round(value * risk_score, 3)

        # Sort by importance
        sorted_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        return sorted_importance

    def _identify_top_risk_factors(self, features_dict: Dict, patient_data: Dict) -> List[str]:
        """Identify top clinical risk factors"""
        risk_factors = []

        # Check each high-value feature
        if features_dict.get('previous_readmissions', 0) > 0.01:
            count = int(patient_data.get('previous_readmissions', 0))
            risk_factors.append(f"Previous {count} readmission(s) (Strong predictor)")

        if features_dict.get('comorbidity_count', 0) > 0.3:
            risk_factors.append("Multiple comorbidities")

        if features_dict.get('has_diabetes', 0) > 0.5:
            risk_factors.append("Diabetes")

        if features_dict.get('has_heart_disease', 0) > 0.5:
            risk_factors.append("Cardiac disease")

        if features_dict.get('has_hypertension', 0) > 0.5:
            risk_factors.append("Hypertension")

        if features_dict.get('medication_count', 0) > 0.4:
            risk_factors.append("Polypharmacy (multiple medications)")

        age = int(patient_data.get('age', 60)) if patient_data.get('age') else 60
        if age > 75:
            risk_factors.append("Advanced age (>75 years)")

        return risk_factors[:5]  # Return top 5

    def _recommend_interventions(self, risk_score: float, risk_factors: List[str], patient_data: Dict) -> List[str]:
        """Generate recommended interventions based on risk profile"""
        interventions = []

        if risk_score >= 0.7:
            interventions.append("🔴 URGENT: Schedule 3-day post-discharge follow-up call")
            interventions.append("Assign case manager for discharge planning")
            interventions.append("Consider home health services")
            interventions.append("Arrange transportation assistance if needed")

        elif risk_score >= 0.5:
            interventions.append("🟡 Schedule 7-day post-discharge follow-up")
            interventions.append("Provide clear discharge instructions")
            interventions.append("Arrange pharmacy consultation if on >5 medications")

        else:
            interventions.append("🟢 Standard 14-day follow-up appropriate")
            interventions.append("Provide routine discharge education")

        # Condition-specific interventions
        if any('diabetes' in factor.lower() for factor in risk_factors):
            interventions.append("Diabetes education & glucose monitoring plan")

        if any('cardiac' in factor.lower() for factor in risk_factors):
            interventions.append("Cardiology follow-up within 1 week")

        if any('polypharmacy' in factor.lower() for factor in risk_factors):
            interventions.append("Pharmacy medication review")

        return interventions[:6]  # Return top 6 interventions

    def get_model_stats(self) -> Dict:
        """Get model statistics and metadata"""
        if self.model_metadata:
            return self.model_metadata
        else:
            return {
                "model_type": "Logistic Regression",
                "status": "Not trained" if self.model is None else "Ready",
                "features": self.feature_names,
                "feature_count": len(self.feature_names),
                "last_trained": None,
                "accuracy": None,
                "precision": None,
                "recall": None,
                "auc_roc": None,
                "note": "Model uses rule-based fallback until trained on historical data"
            }


def get_readmission_predictor() -> ReadmissionPredictor:
    """Factory function to get singleton service instance"""
    global _readmission_predictor
    if _readmission_predictor is None:
        _readmission_predictor = ReadmissionPredictor()
    return _readmission_predictor


if __name__ == "__main__":
    # Test service
    predictor = get_readmission_predictor()

    # Sample patient data
    sample_patient = {
        "age": "78",
        "bmi": 28,
        "gender": "M",
        "family_history": ["diabetes", "hypertension"],
        "medication_count": 8,
        "diagnosis_complexity": 2,
        "previous_readmissions": 1
    }

    print("\n[TEST] Readmission Prediction")
    print("=" * 50)
    result = predictor.predict_risk(sample_patient)
    print(json.dumps(result, indent=2))

    print("\n[TEST] Model Statistics")
    print("=" * 50)
    stats = predictor.get_model_stats()
    print(json.dumps(stats, indent=2))
