"""Phase 4: Add medical image analysis and population health models

Revision ID: phase_4_001
Revises: 
Create Date: 2025-12-18

This migration adds all Phase 4 database tables:
- MedicalImage: Store medical images and AI analysis
- MedicalReport: Generated medical reports
- PatientOutcome: Longitudinal patient data
- RiskScore: Computed risk metrics
- ProgressionPrediction: Disease trajectory forecasts
- CohortAnalytics: Population-level analytics
- DiseasePrevalence: Epidemiology tracking
- ComorbidityAssociation: Disease network data
- TreatmentEffectiveness: Comparative analysis
- HealthEquityMetric: Disparity tracking
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'phase_4_001'
down_revision = 'b8d27bb73385'  # Points to previous migration head
branch_labels = None
depends_on = None


def upgrade():
    """Create Phase 4 tables"""
    
    # MedicalImage table
    op.create_table(
        'medical_images',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.id'), nullable=True),
        sa.Column('image_type', sa.String(50), nullable=False),  # xray, ecg, ultrasound, etc.
        sa.Column('image_hash', sa.String(64), unique=True, nullable=False, index=True),
        sa.Column('image_data', sa.LargeBinary(), nullable=False),
        sa.Column('ai_findings', sa.JSON(), nullable=True),
        sa.Column('ai_confidence', sa.Float(), nullable=True),
        sa.Column('ai_severity', sa.String(20), nullable=True),
        sa.Column('differential_diagnoses', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('clinical_significance', sa.Text(), nullable=True),
        sa.Column('verified_findings', sa.JSON(), nullable=True),
        sa.Column('verification_notes', sa.Text(), nullable=True),
        sa.Column('verified_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('verification_status', sa.String(20), default='PENDING'),
        sa.Column('ai_analysis_date', sa.DateTime(), nullable=True),
        sa.Column('verification_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # MedicalReport table
    op.create_table(
        'medical_reports',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.id'), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('citations', sa.JSON(), nullable=True),
        sa.Column('generated_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('pdf_path', sa.String(500), nullable=True),
        sa.Column('signature', sa.Text(), nullable=True),
        sa.Column('signed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('status', sa.String(20), default='DRAFT'),
        sa.Column('generated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('signed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # PatientOutcome table
    op.create_table(
        'patient_outcomes',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('visit_date', sa.DateTime(), nullable=False),
        sa.Column('outcome_status', sa.String(50), nullable=False),
        sa.Column('vital_signs', sa.JSON(), nullable=True),
        sa.Column('lab_results', sa.JSON(), nullable=True),
        sa.Column('clinical_notes', sa.Text(), nullable=True),
        sa.Column('recorded_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # RiskScore table
    op.create_table(
        'risk_scores',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('hospitalization_risk', sa.Float(), nullable=True),
        sa.Column('readmission_risk', sa.Float(), nullable=True),
        sa.Column('complication_risk', sa.Float(), nullable=True),
        sa.Column('mortality_risk', sa.Float(), nullable=True),
        sa.Column('risk_factors', sa.JSON(), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('computed_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # ProgressionPrediction table
    op.create_table(
        'progression_predictions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.id'), nullable=False, index=True),
        sa.Column('condition', sa.String(200), nullable=False),
        sa.Column('progression_trend', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('time_horizon_months', sa.Integer(), nullable=True),
        sa.Column('predicted_milestones', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('predicted_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # CohortAnalytics table
    op.create_table(
        'cohort_analytics',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('cohort_name', sa.String(200), nullable=False),
        sa.Column('cohort_definition', sa.Text(), nullable=True),
        sa.Column('filters', sa.JSON(), nullable=True),
        sa.Column('total_population', sa.Integer(), nullable=True),
        sa.Column('age_distribution', sa.JSON(), nullable=True),
        sa.Column('gender_distribution', sa.JSON(), nullable=True),
        sa.Column('diagnosis_distribution', sa.JSON(), nullable=True),
        sa.Column('comorbidities', sa.JSON(), nullable=True),
        sa.Column('medications', sa.JSON(), nullable=True),
        sa.Column('computed_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # DiseasePrevalence table
    op.create_table(
        'disease_prevalence',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('disease_name', sa.String(200), nullable=False),
        sa.Column('icd_code', sa.String(20), nullable=True),
        sa.Column('prevalence_percent', sa.Float(), nullable=True),
        sa.Column('case_count', sa.Integer(), nullable=True),
        sa.Column('population_size', sa.Integer(), nullable=True),
        sa.Column('trend', sa.String(50), nullable=True),
        sa.Column('demographic_breakdown', sa.JSON(), nullable=True),
        sa.Column('time_period_start', sa.DateTime(), nullable=True),
        sa.Column('time_period_end', sa.DateTime(), nullable=True),
        sa.Column('computed_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # ComorbidityAssociation table
    op.create_table(
        'comorbidity_associations',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('primary_diagnosis', sa.String(200), nullable=False),
        sa.Column('associated_diagnosis', sa.String(200), nullable=False),
        sa.Column('co_occurrence_count', sa.Integer(), nullable=True),
        sa.Column('co_occurrence_rate', sa.Float(), nullable=True),
        sa.Column('relative_risk', sa.Float(), nullable=True),
        sa.Column('confidence_interval', sa.JSON(), nullable=True),
        sa.Column('statistical_significance', sa.Boolean(), default=False),
        sa.Column('computed_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # TreatmentEffectiveness table
    op.create_table(
        'treatment_effectiveness',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('condition', sa.String(200), nullable=False),
        sa.Column('treatment_1', sa.String(200), nullable=False),
        sa.Column('treatment_2', sa.String(200), nullable=True),
        sa.Column('sample_size_1', sa.Integer(), nullable=True),
        sa.Column('sample_size_2', sa.Integer(), nullable=True),
        sa.Column('success_rate_1', sa.Float(), nullable=True),
        sa.Column('success_rate_2', sa.Float(), nullable=True),
        sa.Column('side_effects_1', sa.JSON(), nullable=True),
        sa.Column('side_effects_2', sa.JSON(), nullable=True),
        sa.Column('cost_1', sa.Float(), nullable=True),
        sa.Column('cost_2', sa.Float(), nullable=True),
        sa.Column('p_value', sa.Float(), nullable=True),
        sa.Column('statistical_significance', sa.Boolean(), default=False),
        sa.Column('computed_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # HealthEquityMetric table
    op.create_table(
        'health_equity_metrics',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('metric_name', sa.String(200), nullable=False),
        sa.Column('metric_description', sa.Text(), nullable=True),
        sa.Column('demographic_group', sa.String(100), nullable=True),
        sa.Column('metric_value', sa.Float(), nullable=True),
        sa.Column('comparison_baseline', sa.Float(), nullable=True),
        sa.Column('disparity_index', sa.Float(), nullable=True),
        sa.Column('demographic_breakdown', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('data_source', sa.String(200), nullable=True),
        sa.Column('computed_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    
    # Create indexes for better query performance
    op.create_index('idx_medical_images_patient', 'medical_images', ['patient_id'])
    op.create_index('idx_medical_images_type', 'medical_images', ['image_type'])
    op.create_index('idx_medical_images_severity', 'medical_images', ['ai_severity'])
    op.create_index('idx_medical_reports_patient', 'medical_reports', ['patient_id'])
    op.create_index('idx_patient_outcomes_patient', 'patient_outcomes', ['patient_id'])
    op.create_index('idx_patient_outcomes_date', 'patient_outcomes', ['visit_date'])
    op.create_index('idx_risk_scores_patient', 'risk_scores', ['patient_id'])
    op.create_index('idx_progression_predictions_patient', 'progression_predictions', ['patient_id'])
    op.create_index('idx_disease_prevalence_disease', 'disease_prevalence', ['disease_name'])
    op.create_index('idx_comorbidity_primary', 'comorbidity_associations', ['primary_diagnosis'])


def downgrade():
    """Drop Phase 4 tables"""
    
    # Drop indexes first
    op.drop_index('idx_comorbidity_primary')
    op.drop_index('idx_disease_prevalence_disease')
    op.drop_index('idx_progression_predictions_patient')
    op.drop_index('idx_risk_scores_patient')
    op.drop_index('idx_patient_outcomes_date')
    op.drop_index('idx_patient_outcomes_patient')
    op.drop_index('idx_medical_reports_patient')
    op.drop_index('idx_medical_images_severity')
    op.drop_index('idx_medical_images_type')
    op.drop_index('idx_medical_images_patient')
    
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('health_equity_metrics')
    op.drop_table('treatment_effectiveness')
    op.drop_table('comorbidity_associations')
    op.drop_table('disease_prevalence')
    op.drop_table('cohort_analytics')
    op.drop_table('progression_predictions')
    op.drop_table('risk_scores')
    op.drop_table('patient_outcomes')
    op.drop_table('medical_reports')
    op.drop_table('medical_images')
