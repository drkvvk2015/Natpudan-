from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    __tablename__ = "users"

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

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("ChatMessage", back_populates="conversation")
    user = relationship("User", back_populates="conversations")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

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
