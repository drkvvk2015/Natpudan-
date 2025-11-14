"""Database models for Natpudan AI - Consolidated from app/models.py and app/database/models.py"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


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
    
    def __repr__(self):
        return f"<KnowledgeDocument(id={self.document_id}, filename={self.filename})>"
