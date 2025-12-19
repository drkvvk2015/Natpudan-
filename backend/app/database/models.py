from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="patient", nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    address = Column(Text, nullable=True)
    license_number = Column(String(100), nullable=True)
    specialization = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    conversations = relationship("Conversation", back_populates="user")

    def to_dict(self):
        """Convert to dictionary for API responses (exclude password)"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "phone": self.phone,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("ChatMessage", back_populates="conversation")
    user = relationship("User", back_populates="conversations")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # ... existing code ...
    conversation = relationship("Conversation", back_populates="messages")


class PatientIntake(Base):
    """Patient intake information model"""
    __tablename__ = "patient_intakes"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    intake_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    age = Column(String(10))
    gender = Column(String(20))
    blood_type = Column(String(10))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    travel_history = relationship("TravelHistory", back_populates="patient", cascade="all, delete-orphan")
    family_history = relationship("FamilyHistory", back_populates="patient", cascade="all, delete-orphan")
    treatment_plans = relationship("TreatmentPlan", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PatientIntake(id={self.intake_id}, name={self.name})>"


class TravelHistory(Base):
    """Travel history model"""
    __tablename__ = "travel_history"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    patient_intake_id = Column(Integer, ForeignKey("patient_intakes.id", ondelete="CASCADE"))
    destination = Column(String(200), nullable=False)
    departure_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=False)
    duration = Column(String(50))  # Human-readable duration (e.g., "2 weeks")
    purpose = Column(String(100))
    activities = Column(Text)  # List of activities
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    patient = relationship("PatientIntake", back_populates="travel_history")
    
    def __repr__(self):
        return f"<TravelHistory(id={self.id}, destination={self.destination})>"


class FamilyHistory(Base):
    """Family medical history model"""
    __tablename__ = "family_history"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    patient_intake_id = Column(Integer, ForeignKey("patient_intakes.id", ondelete="CASCADE"))
    family_relationship = Column(String(100), nullable=False)
    condition = Column(String(200), nullable=False)
    age_of_onset = Column(String(50))
    duration = Column(String(50))
    status = Column(String(20))  # ongoing, resolved, deceased
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    patient = relationship("PatientIntake", back_populates="family_history")
    
    def __repr__(self):
        return f"<FamilyHistory(id={self.id}, family_relationship={self.family_relationship}, condition={self.condition})>"


import enum
class MedicationFrequency(str, enum.Enum):
    ONCE_DAILY = "once_daily"
    TWICE_DAILY = "twice_daily"
    THREE_TIMES_DAILY = "three_times_daily"
    FOUR_TIMES_DAILY = "four_times_daily"
    EVERY_4_HOURS = "every_4_hours"
    EVERY_6_HOURS = "every_6_hours"
    EVERY_8_HOURS = "every_8_hours"
    EVERY_12_HOURS = "every_12_hours"
    AS_NEEDED = "as_needed"
    BEFORE_MEALS = "before_meals"
    AFTER_MEALS = "after_meals"
    AT_BEDTIME = "at_bedtime"


class MedicationRoute(str, enum.Enum):
    ORAL = "oral"
    INTRAVENOUS = "intravenous"
    INTRAMUSCULAR = "intramuscular"
    SUBCUTANEOUS = "subcutaneous"
    TOPICAL = "topical"
    INHALATION = "inhalation"
    RECTAL = "rectal"
    SUBLINGUAL = "sublingual"
    TRANSDERMAL = "transdermal"


class TreatmentStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"
    ON_HOLD = "on_hold"


class FollowUpStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    MISSED = "missed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class TreatmentPlan(Base):
    __tablename__ = "treatment_plans"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String, unique=True, index=True, nullable=False)
    patient_intake_id = Column(String, ForeignKey("patient_intakes.intake_id"), nullable=False)
    diagnosis_id = Column(String, nullable=True)  # Optional link to diagnosis session
    
    # Treatment metadata
    primary_diagnosis = Column(String, nullable=False)
    icd_code = Column(String, nullable=True)
    treatment_goals = Column(Text, nullable=True)
    clinical_notes = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(String, default=TreatmentStatus.ACTIVE, nullable=False)
    start_date = Column(DateTime, default=func.now(), nullable=False)
    end_date = Column(DateTime, nullable=True)
    last_review_date = Column(DateTime, nullable=True)
    next_review_date = Column(DateTime, nullable=True)
    
    # Metadata
    created_by = Column(String, nullable=True)  # Doctor/user ID
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("PatientIntake", back_populates="treatment_plans")
    medications = relationship("Medication", back_populates="treatment_plan", cascade="all, delete-orphan")
    follow_ups = relationship("FollowUp", back_populates="treatment_plan", cascade="all, delete-orphan")
    monitoring_records = relationship("MonitoringRecord", back_populates="treatment_plan", cascade="all, delete-orphan")


class Medication(Base):
    __tablename__ = "medications"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    treatment_plan_id = Column(Integer, ForeignKey("treatment_plans.id"), nullable=False)
    
    # Medication details
    medication_name = Column(String, nullable=False)
    generic_name = Column(String, nullable=True)
    dosage = Column(String, nullable=False)  # e.g., "500mg", "10ml"
    route = Column(String, default=MedicationRoute.ORAL, nullable=False)
    frequency = Column(String, default=MedicationFrequency.ONCE_DAILY, nullable=False)
    duration_days = Column(Integer, nullable=True)
    
    # Instructions
    instructions = Column(Text, nullable=True)
    precautions = Column(Text, nullable=True)
    side_effects = Column(Text, nullable=True)
    
    # Prescription tracking
    prescribed_date = Column(DateTime, default=func.now(), nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    refills_remaining = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    discontinuation_reason = Column(String, nullable=True)
    discontinuation_date = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    treatment_plan = relationship("TreatmentPlan", back_populates="medications")


class FollowUp(Base):
    __tablename__ = "follow_ups"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    treatment_plan_id = Column(Integer, ForeignKey("treatment_plans.id"), nullable=False)
    
    # Appointment details
    scheduled_date = Column(DateTime, nullable=False)
    appointment_type = Column(String, nullable=True)  # e.g., "Routine Check-up", "Lab Review"
    location = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    
    # Status
    status = Column(String, default=FollowUpStatus.SCHEDULED, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    
    # Notes
    pre_appointment_instructions = Column(Text, nullable=True)
    post_appointment_notes = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)
    
    # Reminders
    reminder_sent = Column(Boolean, default=False)
    reminder_date = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    treatment_plan = relationship("TreatmentPlan", back_populates="follow_ups")


class MonitoringRecord(Base):
    __tablename__ = "monitoring_records"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    treatment_plan_id = Column(Integer, ForeignKey("treatment_plans.id"), nullable=False)
    
    # Monitoring details
    record_date = Column(DateTime, default=func.now(), nullable=False)
    monitoring_type = Column(String, nullable=False)  # e.g., "Vital Signs", "Lab Results", "Symptoms"
    
    # Measurements
    measurements = Column(Text, nullable=True)  # JSON string of measurements
    
    # Assessment
    assessment = Column(Text, nullable=True)
    concerns = Column(Text, nullable=True)
    action_taken = Column(Text, nullable=True)
    
    # Metadata
    recorded_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    treatment_plan = relationship("TreatmentPlan", back_populates="monitoring_records")


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
