from app.services.readmission_predictor import ReadmissionPredictor


def test_predict_returns_expected_shape():
    predictor = ReadmissionPredictor()
    result = predictor.predict_risk(
        patient_data={
            "age": 70,
            "conditions": ["diabetes", "hypertension"],
            "recent_admissions": 1,
            "medications": ["metformin"],
        }
    )

    assert isinstance(result, dict)
    assert "risk_score" in result
    assert "risk_level" in result
    assert "confidence" in result
    assert 0 <= result["risk_score"] <= 1
    assert 0 <= result["confidence"] <= 1
