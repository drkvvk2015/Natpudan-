"""Database models for Natpudan AI - Consolidated from app/models.py and app/database/models.py"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

# Import Base from database/base.py (single source of truth)
from app.database.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    STAFF = "staff"
    DOCTOR = "doctor"
    ADMIN = "admin"


# Enums for Treatment Plan features
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


class User(Base):
    """User model for authentication and profile."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STAFF, nullable=False)
    license_number = Column(String(100), nullable=True)
    
    # OAuth fields
    oauth_provider = Column(String(50), nullable=True)  # google, github, microsoft
    oauth_id = Column(String(255), nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    discharge_summaries = relationship("DischargeSummary", back_populates="created_by", cascade="all, delete-orphan")
    pdf_processing_jobs = relationship("PDFProcessing", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    """Conversation model for chat history."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    """Message model for conversation messages."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class DischargeSummary(Base):
    """Discharge summary model for patient discharge documentation."""
    __tablename__ = "discharge_summaries"

    id = Column(Integer, primary_key=True, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Patient Information
    patient_name = Column(String(255), nullable=False)
    patient_age = Column(String(10), nullable=True)
    patient_gender = Column(String(20), nullable=True)
    mrn = Column(String(100), nullable=True)
    admission_date = Column(String(50), nullable=True)
    discharge_date = Column(String(50), nullable=True)
    
    # Clinical Information
    chief_complaint = Column(Text, nullable=True)
    history_present_illness = Column(Text, nullable=True)
    past_medical_history = Column(Text, nullable=True)
    physical_examination = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    hospital_course = Column(Text, nullable=True)
    procedures_performed = Column(Text, nullable=True)
    medications = Column(Text, nullable=True)
    
    # Discharge Information
    discharge_medications = Column(Text, nullable=True)
    follow_up_instructions = Column(Text, nullable=True)
    diet_restrictions = Column(Text, nullable=True)
    activity_restrictions = Column(Text, nullable=True)
    
    # AI Generated Content
    ai_summary = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    created_by = relationship("User", back_populates="discharge_summaries")


# ==================== Patient Intake Models ====================

class PatientIntake(Base):
    """Patient intake information model"""
    __tablename__ = "patient_intakes"
    
    id = Column(Integer, primary_key=True, index=True)
    intake_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    age = Column(String(10))
    gender = Column(String(20))
    blood_type = Column(String(10))
    
    # Extended Anthropometry
    height_cm = Column(Integer, nullable=True)
    weight_kg = Column(Integer, nullable=True)
    bmi = Column(Integer, nullable=True)
    waist_cm = Column(Integer, nullable=True)
    hip_cm = Column(Integer, nullable=True)
    whr = Column(Integer, nullable=True)
    muac_cm = Column(Integer, nullable=True)
    head_circumference_cm = Column(Integer, nullable=True)
    chest_expansion_cm = Column(Integer, nullable=True)
    sitting_height_cm = Column(Integer, nullable=True)
    standing_height_cm = Column(Integer, nullable=True)
    arm_span_cm = Column(Integer, nullable=True)
    body_fat_percent = Column(Integer, nullable=True)
    bp_systolic = Column(Integer, nullable=True)
    bp_diastolic = Column(Integer, nullable=True)
    pulse_per_min = Column(Integer, nullable=True)
    resp_rate_per_min = Column(Integer, nullable=True)
    temperature_c = Column(Integer, nullable=True)
    
    # Chief Complaints and Present History (stored as JSON)
    chief_complaints = Column(JSON, nullable=True)  # JSON: List of structured complaints with chronology
    associated_symptoms = Column(JSON, nullable=True)  # JSON: List of associated symptoms
    present_history = Column(Text, nullable=True)  # JSON: Legacy field for backward compatibility
    
    # Past history
    past_medical_history = Column(JSON, nullable=True)  # List of past medical conditions
    past_surgical_history = Column(JSON, nullable=True)  # List of past surgeries
    current_medications = Column(JSON, nullable=True)  # List of current medications
    allergies = Column(JSON, nullable=True)  # List of allergies
    
    # Social history
    smoking = Column(String(100), nullable=True)
    alcohol = Column(String(100), nullable=True)
    occupation = Column(String(200), nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
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


# ==================== Treatment Plan Models ====================

class TreatmentPlan(Base):
    __tablename__ = "treatment_plans"

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


# ==================== Knowledge Base Models ====================

class KnowledgeDocument(Base):
    """Knowledge base document model for tracking uploaded medical documents"""
    __tablename__ = "knowledge_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA-256 hash
    file_size = Column(Integer, nullable=False)
    extension = Column(String(10), nullable=False)
    
    # Content metadata
    text_length = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    
    # Indexing status
    is_indexed = Column(Boolean, default=False)
    indexed_at = Column(DateTime, nullable=True)
    indexing_error = Column(Text, nullable=True)
    
    # Metadata
    source = Column(String(100), nullable=True)  # e.g., "CDC", "WHO", "PubMed"
    category = Column(String(100), nullable=True)  # e.g., "Clinical Guidelines", "Research Paper"
    tags = Column(Text, nullable=True)  # JSON array of tags
    description = Column(Text, nullable=True)
    
    # User tracking
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
    extracted_images = relationship("ExtractedImage", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<KnowledgeDocument(id={self.document_id}, filename={self.filename})>"

class DocumentProcessingStatus(Base):
    """Track processing status of uploaded documents during background embedding"""
    __tablename__ = "document_processing_status"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(36), ForeignKey("knowledge_documents.document_id"), unique=True, index=True)
    
    # Status tracking
    status = Column(String(20), default="queued", index=True)  # queued|processing|completed|failed
    progress_percent = Column(Integer, default=0)  # 0-100
    current_chunk = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Metadata
    processing_type = Column(String(50), default="embedding")  # embedding|indexing|verification
    estimated_time_seconds = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    document = relationship("KnowledgeDocument", foreign_keys=[document_id])
    
    def __repr__(self):
        return f"<DocumentProcessingStatus(doc_id={self.document_id}, status={self.status})>"


class ExtractedImage(Base):
    """Model for storing extracted PDF images with metadata"""
    __tablename__ = "extracted_images"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(String, unique=True, index=True)  # Unique identifier
    document_id = Column(String, ForeignKey("knowledge_documents.document_id"), index=True)
    filename = Column(String)  # Image filename
    file_path = Column(String)  # Path to saved image
    page_number = Column(Integer)  # Page in PDF
    image_index = Column(Integer)  # Index on page
    xref = Column(Integer)  # PyMuPDF xref
    extension = Column(String)  # Image format (png, jpg, etc.)
    size_bytes = Column(Integer)  # File size
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # OCR/AI analysis (for future use)
    ocr_text = Column(Text, nullable=True)  # OCR'd text from image
    caption = Column(Text, nullable=True)  # AI-generated caption
    tags = Column(JSON, nullable=True)  # Image tags/labels
    
    # Timestamps
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("KnowledgeDocument", back_populates="extracted_images")
    
    def __repr__(self):
        return f"<ExtractedImage(id={self.image_id}, doc={self.document_id}, page={self.page_number})>"


class PDFProcessingStatus(str, enum.Enum):
    """PDF processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class PDFProcessing(Base):
    """Track PDF processing state for pause/resume functionality."""
    __tablename__ = "pdf_processing"
    
    id = Column(Integer, primary_key=True, index=True)
    pdf_file_id = Column(String, unique=True, index=True)  # Unique identifier for PDF
    pdf_name = Column(String)  # Original filename
    status = Column(String, default=PDFProcessingStatus.PENDING)  # PENDING, PROCESSING, PAUSED, COMPLETED, FAILED
    
    # Progress tracking
    total_pages = Column(Integer, default=0)
    pages_processed = Column(Integer, default=0)
    last_page_processed = Column(Integer, default=0)
    embeddings_created = Column(Integer, default=0)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)  # Store detailed error info
    
    # Processing metadata
    file_size = Column(Integer)  # File size in bytes
    started_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # User tracking
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="pdf_processing_jobs")
    
    def __repr__(self):
        return f"<PDFProcessing(id={self.id}, name={self.pdf_name}, status={self.status}, progress={self.pages_processed}/{self.total_pages})>"
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_pages == 0:
            return 0.0
        return (self.pages_processed / self.total_pages) * 100


# ============================================================================
# PHASE 4 MODELS - Medical Image Analysis & Population Health
# ============================================================================
# Import Phase 4 models to register them with SQLAlchemy Base
from app.models.phase_4_models import (
    MedicalImage,
    MedicalReport,
    PatientOutcome,
    RiskScore,
    ProgressionPrediction,
    CohortAnalytics,
    DiseasePrevalence,
    ComorbidityAssociation,
    TreatmentEffectiveness,
    HealthEquityMetric
)