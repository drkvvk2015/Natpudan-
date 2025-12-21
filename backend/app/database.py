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
    """Initialize database tables and seed default admin user."""
    try:
        from app.models import Base
        Base.metadata.create_all(bind=engine)
        print("[DATABASE] Tables created successfully")
        
        # Seed default admin user if it doesn't exist
        seed_admin_user()
        
    except Exception as e:
        print(f"[DATABASE ERROR] Failed to create tables: {e}")
        # Don't raise - allow app to start even if DB init fails


def seed_admin_user():
    """Create default admin user if it doesn't exist."""
    try:
        from app.models import User, UserRole
        from app.utils.security import hash_password
        
        db = SessionLocal()
        
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "admin@admin.com").first()
        
        if not admin:
            # Hash password using bcrypt (same as auth system)
            password = "Admin@123"
            hashed_password = hash_password(password)
            
            # Create admin user
            admin = User(
                email="admin@admin.com",
                hashed_password=hashed_password,
                full_name="System Administrator",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("[DATABASE] Default admin user created: admin@admin.com / Admin@123")
        else:
            print("[DATABASE] Admin user already exists")
            
        db.close()
        
    except Exception as e:
        print(f"[DATABASE WARNING] Failed to seed admin user: {e}")
        # Don't raise - allow app to start even if seeding fails
