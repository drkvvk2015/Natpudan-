"""CRUD operations for database models."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.models import User, Conversation, Message, DischargeSummary, UserRole
from app.utils.security import hash_password, verify_password


# User CRUD operations
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(
    db: Session,
    email: str,
    password: Optional[str],
    full_name: str,
    role: str = "staff",
    license_number: Optional[str] = None,
    oauth_provider: Optional[str] = None,
    oauth_id: Optional[str] = None,
) -> User:
    """Create new user."""
    hashed_password = hash_password(password) if password else None
    
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=UserRole(role),
        license_number=license_number,
        oauth_provider=oauth_provider,
        oauth_id=oauth_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    user = get_user_by_email(db, email)
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user_password(db: Session, user_id: int, new_password: str) -> Optional[User]:
    """Update user password."""
    user = get_user_by_id(db, user_id)
    if user:
        user.hashed_password = hash_password(new_password)
        db.commit()
        db.refresh(user)
    return user


# Conversation CRUD operations
def create_conversation(db: Session, user_id: int, title: Optional[str] = None) -> Conversation:
    """Create new conversation."""
    conversation = Conversation(user_id=user_id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_user_conversations(db: Session, user_id: int) -> List[Conversation]:
    """Get all conversations for a user."""
    return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).all()


def get_conversation(db: Session, conversation_id: int, user_id: int) -> Optional[Conversation]:
    """Get conversation by ID for specific user."""
    return db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()


def delete_conversation(db: Session, conversation_id: int, user_id: int) -> bool:
    """Delete conversation."""
    conversation = get_conversation(db, conversation_id, user_id)
    if conversation:
        db.delete(conversation)
        db.commit()
        return True
    return False


# Message CRUD operations
def create_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
) -> Message:
    """Create new message in conversation."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    db.add(message)
    
    # Update conversation updated_at
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    return message


def get_conversation_messages(db: Session, conversation_id: int) -> List[Message]:
    """Get all messages in a conversation."""
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()


# Discharge Summary CRUD operations
def create_discharge_summary(
    db: Session,
    created_by_id: int,
    patient_data: dict,
) -> DischargeSummary:
    """Create new discharge summary."""
    import json
    # Convert ICD-10 codes list to JSON string if present
    if 'icd10_codes' in patient_data and isinstance(patient_data['icd10_codes'], list):
        patient_data['icd10_codes'] = json.dumps(patient_data['icd10_codes'])
    
    summary = DischargeSummary(
        created_by_id=created_by_id,
        **patient_data
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary


def get_discharge_summary(db: Session, summary_id: int) -> Optional[DischargeSummary]:
    """Get discharge summary by ID."""
    return db.query(DischargeSummary).filter(DischargeSummary.id == summary_id).first()


def get_user_discharge_summaries(db: Session, user_id: int) -> List[DischargeSummary]:
    """Get all discharge summaries created by a user."""
    return db.query(DischargeSummary).filter(
        DischargeSummary.created_by_id == user_id
    ).order_by(DischargeSummary.created_at.desc()).all()


def update_discharge_summary(
    db: Session,
    summary_id: int,
    patient_data: dict,
) -> Optional[DischargeSummary]:
    """Update discharge summary."""
    import json
    summary = get_discharge_summary(db, summary_id)
    if summary:
        # Convert ICD-10 codes list to JSON string if present
        if 'icd10_codes' in patient_data and isinstance(patient_data['icd10_codes'], list):
            patient_data['icd10_codes'] = json.dumps(patient_data['icd10_codes'])
        
        for key, value in patient_data.items():
            if hasattr(summary, key):
                setattr(summary, key, value)
        summary.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(summary)
    return summary


def delete_discharge_summary(db: Session, summary_id: int) -> bool:
    """Delete discharge summary."""
    summary = get_discharge_summary(db, summary_id)
    if summary:
        db.delete(summary)
        db.commit()
        return True
    return False
