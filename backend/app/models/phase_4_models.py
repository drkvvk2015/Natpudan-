"""
Phase 4 Database Models

Extends the existing models.py with new tables for:
- Medical images
- Analysis results
- Patient outcomes
- Generated reports
- Population analytics

Add these to backend/app/models.py
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, LargeBinary, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

# NOTE: Add these imports to models.py:
# from enum import Enum as PyEnum

# ============================================================================
# Phase 4: Medical Image Analysis Models
# ============================================================================

class MedicalImage(Base):
    """Stores medical images and their AI analysis results"""
    __tablename__ = "medical_images"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Image metadata
    image_type = Column(String, nullable=False)  # xray, ecg, ultrasound, pathology, mri, ct
    image_hash = Column(String(32), unique=True, nullable=False)
    image_data = Column(LargeBinary, nullable=False)  # Base64 encoded image
    image_size_bytes = Column(Integer)
    
    # AI Analysis Results
    ai_findings = Column(JSON)  # {"findings": [...], "confidence": 0.92, ...}
    ai_confidence = Column(Float)  # Overall confidence score 0-1
    ai_severity = Column(String)  # CRITICAL, HIGH, MODERATE, LOW, NORMAL
    ai_differential = Column(JSON)  # List of differential diagnoses
    ai_recommendations = Column(JSON)  # List of recommendations
    
    # Radiologist Verification
    verified_by = Column(Integer, ForeignKey("user.id"), nullable=True)
    verification_status = Column(String)  # approved, amended, rejected
    verification_date = Column(DateTime, nullable=True)
    radiologist_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    verified_by_user = relationship("User", foreign_keys=[verified_by])


class MedicalReport(Base):
    """Stores generated medical reports (discharge, progress, treatment plans)"""
    __tablename__ = "medical_reports"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Report metadata
    report_type = Column(String, nullable=False)  # discharge, progress, treatment_plan, follow_up
    generated_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Content
    content = Column(JSON)  # {"summary": "...", "diagnoses": [...], "medications": [...]}
    citations = Column(JSON)  # [{"text": "...", "source": "kb_doc_123", "url": "..."}]
    
    # PDF storage
    pdf_path = Column(String, nullable=True)  # S3 path or file path
    pdf_generated_at = Column(DateTime, nullable=True)
    
    # Digital signature
    signed_by = Column(Integer, ForeignKey("user.id"), nullable=True)
    signature = Column(String, nullable=True)  # JWT signature token
    signature_date = Column(DateTime, nullable=True)
    
    # Status tracking
    status = Column(String)  # draft, final, signed, archived
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    created_by_user = relationship("User", foreign_keys=[generated_by])
    signed_by_user = relationship("User", foreign_keys=[signed_by])


# ============================================================================
# Phase 4: Patient Outcome & Risk Scoring Models
# ============================================================================

class PatientOutcome(Base):
    """Tracks patient outcomes over time for longitudinal analysis"""
    __tablename__ = "patient_outcomes"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Outcome details
    visit_date = Column(DateTime, nullable=False)
    outcome_status = Column(String)  # improved, stable, worsened
    clinical_notes = Column(Text)
    
    # Lab/vital results
    lab_results = Column(JSON)  # {"glucose": 128, "HbA1c": 7.1, ...}
    vital_signs = Column(JSON)  # {"bp_systolic": 130, "heart_rate": 72, ...}
    
    # Risk scores
    hospitalization_risk = Column(Float)  # 0-1
    readmission_risk = Column(Float)  # 0-1
    complication_risk = Column(Float)  # 0-1
    
    # Related diagnoses/conditions
    primary_diagnosis = Column(String)
    secondary_diagnoses = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])


class RiskScore(Base):
    """Stores computed risk scores for patients"""
    __tablename__ = "risk_scores"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Risk metrics
    hospitalization_risk = Column(Float)  # 0-1
    readmission_risk = Column(Float)  # 0-1
    complication_risk = Column(Float)  # 0-1
    mortality_risk = Column(Float)  # 0-1
    
    # Contributing factors
    risk_factors = Column(JSON)  # ["non_adherence", "age_65+", ...]
    protective_factors = Column(JSON)  # ["controlled_bp", "regular_exercise", ...]
    
    # Model information
    model_version = Column(String)  # Version of ML model used
    confidence = Column(Float)  # Confidence in risk score
    
    # Metadata
    computed_at = Column(DateTime, default=func.now())
    valid_until = Column(DateTime)  # When to recompute
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])


class ProgressionPrediction(Base):
    """Stores disease progression predictions"""
    __tablename__ = "progression_predictions"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Condition being predicted
    condition = Column(String)  # Type 2 Diabetes, Hypertension, etc.
    primary_diagnosis = Column(String)
    
    # Prediction
    progression_trend = Column(String)  # stable, slow_decline, rapid_decline, improvement
    confidence = Column(Float)  # 0-1
    time_horizon_months = Column(Integer)  # Prediction window
    
    # Details
    current_state = Column(JSON)  # Current values
    predicted_state = Column(JSON)  # Predicted future values
    contributing_factors = Column(JSON)  # What drives prediction
    recommendations = Column(JSON)  # Action items
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    model_version = Column(String)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])


# ============================================================================
# Phase 4: Population Analytics Models
# ============================================================================

class CohortAnalytics(Base):
    """Aggregated analytics for patient cohorts"""
    __tablename__ = "cohort_analytics"
    
    id = Column(Integer, primary_key=True)
    
    # Cohort definition
    cohort_name = Column(String)
    filters = Column(JSON)  # {"age_range": [40, 65], "diagnosis": "diabetes", ...}
    
    # Population statistics
    total_patients = Column(Integer)
    mean_age = Column(Float)
    gender_distribution = Column(JSON)  # {"M": 0.55, "F": 0.45}
    
    # Clinical metrics
    mean_outcome_score = Column(Float)
    improvement_rate = Column(Float)  # Percentage improved
    complication_rate = Column(Float)
    hospitalization_rate = Column(Float)
    readmission_rate = Column(Float)
    mortality_rate = Column(Float)
    
    # Top comorbidities
    top_comorbidities = Column(JSON)  # List of diagnoses
    top_medications = Column(JSON)  # List of drugs
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class DiseasePrevalence(Base):
    """Tracks disease prevalence over time in population"""
    __tablename__ = "disease_prevalence"
    
    id = Column(Integer, primary_key=True)
    
    # Disease information
    disease_name = Column(String)
    icd10_code = Column(String, nullable=True)
    
    # Prevalence metrics
    prevalence_percent = Column(Float)  # Percentage of population
    incident_cases = Column(Integer)  # New cases in period
    total_affected = Column(Integer)  # Total patients with disease
    total_population = Column(Integer)  # Reference population
    
    # Trends
    trend = Column(String)  # up, down, stable
    trend_percent_change = Column(Float)  # YoY change
    
    # Demographics
    demographic_breakdown = Column(JSON)  # {age: {...}, gender: {...}, race: {...}}
    
    # Period
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    # Metadata
    updated_at = Column(DateTime, default=func.now())


class ComorbidityAssociation(Base):
    """Tracks disease co-occurrence (comorbidity network)"""
    __tablename__ = "comorbidity_associations"
    
    id = Column(Integer, primary_key=True)
    
    # Primary diagnosis
    primary_diagnosis = Column(String)
    
    # Associated diagnosis
    associated_diagnosis = Column(String)
    
    # Association strength
    co_occurrence_rate = Column(Float)  # How often they occur together (0-1)
    relative_risk = Column(Float)  # Risk increase if primary present
    odds_ratio = Column(Float)  # Odds ratio
    
    # Statistical significance
    p_value = Column(Float)
    confidence_interval = Column(JSON)  # [lower, upper]
    
    # Population details
    sample_size = Column(Integer)
    
    # Metadata
    updated_at = Column(DateTime, default=func.now())


class TreatmentEffectiveness(Base):
    """Compares effectiveness of treatments"""
    __tablename__ = "treatment_effectiveness"
    
    id = Column(Integer, primary_key=True)
    
    # Condition and treatments
    condition = Column(String)  # Condition being treated
    treatment_1 = Column(String)  # First treatment (e.g., Metformin)
    treatment_2 = Column(String)  # Second treatment (e.g., Sitagliptin)
    
    # Group 1 metrics
    group_1_n = Column(Integer)
    group_1_mean_outcome = Column(Float)
    group_1_std_outcome = Column(Float)
    group_1_adverse_events = Column(Float)  # Rate
    
    # Group 2 metrics
    group_2_n = Column(Integer)
    group_2_mean_outcome = Column(Float)
    group_2_std_outcome = Column(Float)
    group_2_adverse_events = Column(Float)  # Rate
    
    # Comparison
    p_value = Column(Float)
    effect_size = Column(Float)  # Cohen's d
    statistically_significant = Column(Boolean)
    winner = Column(String)  # treatment_1, treatment_2, or tie
    
    # Metadata
    updated_at = Column(DateTime, default=func.now())


class HealthEquityMetric(Base):
    """Tracks health disparities by demographic groups"""
    __tablename__ = "health_equity_metrics"
    
    id = Column(Integer, primary_key=True)
    
    # Metric being measured
    metric_name = Column(String)  # mortality_rate, complications, etc.
    condition = Column(String, nullable=True)  # Disease if applicable
    
    # Demographics and values
    demographic_breakdown = Column(JSON)  # {"gender": {M: 0.05, F: 0.08}, ...}
    disparity_index = Column(Float)  # Ratio of highest to lowest group
    
    # Statistical tests
    p_value = Column(Float)
    statistically_significant = Column(Boolean)
    
    # Recommendations
    recommendations = Column(JSON)  # Actions to reduce disparities
    priority_level = Column(String)  # critical, high, medium, low
    
    # Metadata
    updated_at = Column(DateTime, default=func.now())


# ============================================================================
# Integration Notes
# ============================================================================

"""
To integrate these models into models.py:

1. Add imports at top:
   from enum import Enum as PyEnum

2. Add each class definition to models.py before the __all__ export

3. Update __all__ to include new models:
   __all__ = [
       ...existing models...,
       'MedicalImage',
       'MedicalReport',
       'PatientOutcome',
       'RiskScore',
       'ProgressionPrediction',
       'CohortAnalytics',
       'DiseasePrevalence',
       'ComorbidityAssociation',
       'TreatmentEffectiveness',
       'HealthEquityMetric',
   ]

4. Create migration:
   alembic revision --autogenerate -m "Add Phase 4 models"

5. Run migration:
   alembic upgrade head
"""
