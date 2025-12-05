"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os

# Simple SQLite database - no external dependencies
DATABASE_URL = "sqlite:///./natpudan.db"

# Create engine - lazy connection
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    pool_pre_ping=False,  # Disable pre-ping to avoid connection attempts at import time
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    try:
        from app.models import Base
        Base.metadata.create_all(bind=engine)
        print("[DATABASE] Tables created successfully")
    except Exception as e:
        print(f"[DATABASE ERROR] Failed to create tables: {e}")
        # Don't raise - allow app to start even if DB init fails
