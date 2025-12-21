from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import enum

# Ensure canonical models are registered (avoid duplicates)
from app.models import User, PatientIntake


# ========================================
# PHASE 7: SELF-LEARNING ENGINE MODELS
# ========================================

class ValidationStatus(str, enum.Enum):
    """Status of case validation"""
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class TrainingJobStatus(str, enum.Enum):
    """Status of training job"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelType(str, enum.Enum):
    """Type of model being trained"""
    MEDSAM = "medsam"
    LLM = "llm"
    DIAGNOSIS = "diagnosis"
    PRESCRIPTION = "prescription"


class ValidatedCase(Base):
    """Validated medical cases for training data"""
    __tablename__ = "validated_cases"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Patient & Diagnosis Info
    patient_intake_id = Column(String, ForeignKey("patient_intakes.intake_id"), nullable=True)
    diagnosis = Column(Text, nullable=False)
    symptoms = Column(Text, nullable=True)  # JSON array of symptoms
    diagnosis_confidence = Column(Integer, nullable=True)  # 0-100
    
    # Validation Info
    validation_status = Column(String, default=ValidationStatus.PENDING, nullable=False)
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime, nullable=True)
    validation_notes = Column(Text, nullable=True)
    
    # Medical Data (for training)
    medical_images = Column(Text, nullable=True)  # JSON array of image paths
    lab_results = Column(Text, nullable=True)  # JSON object
    medications_prescribed = Column(Text, nullable=True)  # JSON array
    treatment_outcome = Column(String, nullable=True)  # success, partial, failed
    
    # Quality Metrics
    data_quality_score = Column(Integer, nullable=True)  # 0-100
    completeness_score = Column(Integer, nullable=True)  # 0-100
    
    # HIPAA Compliance
    is_anonymized = Column(Boolean, default=False, nullable=False)
    anonymization_date = Column(DateTime, nullable=True)
    
    # Training Usage
    used_in_training = Column(Boolean, default=False, nullable=False)
    training_job_id = Column(Integer, ForeignKey("training_jobs.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    validator = relationship("User", foreign_keys=[validated_by])
    training_job = relationship("TrainingJob", foreign_keys=[training_job_id], back_populates="cases")
    
    def __repr__(self):
        return f"<ValidatedCase(id={self.case_id}, diagnosis={self.diagnosis[:50]})>"


class ModelPerformance(Base):
    """Model performance metrics over time"""
    __tablename__ = "model_performance"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model Info
    model_version = Column(String(50), nullable=False, index=True)
    model_type = Column(String, default=ModelType.DIAGNOSIS, nullable=False)
    model_path = Column(String, nullable=True)
    
    # Performance Metrics
    accuracy = Column(Integer, nullable=True)  # 0-100
    precision = Column(Integer, nullable=True)  # 0-100
    recall = Column(Integer, nullable=True)  # 0-100
    f1_score = Column(Integer, nullable=True)  # 0-100
    
    # Specific Metrics
    dice_score = Column(Integer, nullable=True)  # For MedSAM (0-100)
    iou_score = Column(Integer, nullable=True)  # For MedSAM (0-100)
    perplexity = Column(Integer, nullable=True)  # For LLM
    
    # Dataset Info
    training_dataset_size = Column(Integer, nullable=True)
    validation_dataset_size = Column(Integer, nullable=True)
    test_dataset_size = Column(Integer, nullable=True)
    
    # Deployment Status
    is_active = Column(Boolean, default=False, nullable=False)
    deployed_at = Column(DateTime, nullable=True)
    replaced_version = Column(String(50), nullable=True)  # Previous version
    
    # A/B Testing
    ab_test_enabled = Column(Boolean, default=False)
    ab_test_traffic_percentage = Column(Integer, nullable=True)  # 0-100
    ab_test_start_date = Column(DateTime, nullable=True)
    ab_test_end_date = Column(DateTime, nullable=True)
    
    # Rollback Info
    rollback_available = Column(Boolean, default=True, nullable=False)
    rollback_reason = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    training_jobs = relationship("TrainingJob", back_populates="model_performance")
    
    def __repr__(self):
        return f"<ModelPerformance(version={self.model_version}, accuracy={self.accuracy})>"


class TrainingJob(Base):
    """Training job tracking and management"""
    __tablename__ = "training_jobs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Job Configuration
    model_type = Column(String, default=ModelType.DIAGNOSIS, nullable=False)
    model_version = Column(String(50), nullable=False)
    parent_model_version = Column(String(50), nullable=True)  # Model being fine-tuned
    
    # Training Configuration
    dataset_size = Column(Integer, nullable=False)
    batch_size = Column(Integer, default=4, nullable=False)
    learning_rate = Column(String, default="1e-5", nullable=False)
    num_epochs = Column(Integer, default=10, nullable=False)
    
    # Hyperparameters (JSON)
    hyperparameters = Column(Text, nullable=True)  # JSON object
    
    # Status
    status = Column(String, default=TrainingJobStatus.QUEUED, nullable=False)
    progress_percentage = Column(Integer, default=0, nullable=False)  # 0-100
    current_epoch = Column(Integer, default=0)
    
    # Timing
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    estimated_completion = Column(DateTime, nullable=True)
    
    # Results
    final_accuracy = Column(Integer, nullable=True)  # 0-100
    final_loss = Column(String, nullable=True)
    training_metrics = Column(Text, nullable=True)  # JSON object with all metrics
    
    # Resource Usage
    gpu_used = Column(Boolean, default=False)
    gpu_memory_mb = Column(Integer, nullable=True)
    cpu_percent = Column(Integer, nullable=True)
    ram_usage_mb = Column(Integer, nullable=True)
    
    # Logging
    log_file_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Deployment
    auto_deploy = Column(Boolean, default=False, nullable=False)
    deployed = Column(Boolean, default=False, nullable=False)
    deployment_date = Column(DateTime, nullable=True)
    
    # Metadata
    triggered_by = Column(String, nullable=True)  # manual, scheduled, threshold
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    model_performance_id = Column(Integer, ForeignKey("model_performance.id"), nullable=True)
    model_performance = relationship("ModelPerformance", back_populates="training_jobs")
    cases = relationship("ValidatedCase", foreign_keys="ValidatedCase.training_job_id", back_populates="training_job")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<TrainingJob(id={self.job_id}, status={self.status}, progress={self.progress_percentage}%)>"
