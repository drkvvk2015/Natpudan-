import pytest
import numpy as np
from app.services.readmission_predictor import get_readmission_predictor

@pytest.fixture
def predictor():
    return get_readmission_predictor()

def test_extract_features_basic(predictor):
    patient_data = {
        "age": "70",
        "bmi": "25",
        "gender": "M",
        "family_history": ["diabetes"],
        "medication_count": 5,
        "diagnosis_complexity": 1,
        "previous_readmissions": 0
    }
    vector, features = predictor.extract_features(patient_data)
    
    assert isinstance(vector, np.ndarray)
    assert features['age'] == 0.7
    assert features['gender_male'] == 1.0
    assert features['has_diabetes'] == 1.0
    assert features['has_hypertension'] == 0.0

def test_rule_based_prediction_high_risk(predictor):
    # High risk patient: old, many readmissions, heart disease
    patient_data = {
        "age": "85",
        "previous_readmissions": 3,
        "family_history": ["heart disease", "congestive heart failure"],
        "medication_count": 10
    }
    risk_score = predictor._rule_based_prediction(patient_data)
    assert risk_score > 0.7
    
def test_predict_risk_response_structure(predictor):
    patient_data = {
        "age": "45",
        "bmi": "22",
        "gender": "F"
    }
    result = predictor.predict_risk(patient_data)
    
    assert "risk_score" in result
    assert "risk_level" in result
    assert "confidence" in result
    assert "top_risk_factors" in result
    assert "recommended_interventions" in result
    assert isinstance(result["top_risk_factors"], list)

def test_confidence_calculation(predictor):
    # High richness = higher confidence
    rich_data = {"age": 70, "bmi": 25, "gender": "M", "family_history": ["diabetes"], "medication_count": 5}
    poor_data = {"age": 70}
    
    _, rich_features = predictor.extract_features(rich_data)
    _, poor_features = predictor.extract_features(poor_data)
    
    conf_rich = predictor._estimate_confidence(0.5, rich_features)
    conf_poor = predictor._estimate_confidence(0.5, poor_features)
    
    assert conf_rich > conf_poor
