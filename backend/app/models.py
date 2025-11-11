"""Database models for Natpudan AI."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role enumeration."""
    STAFF = "staff"
    DOCTOR = "doctor"
    ADMIN = "admin"


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
