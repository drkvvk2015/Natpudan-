"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from app.core.config import settings

DATABASE_URL = settings.get_database_url()

engine_kwargs = {"pool_pre_ping": True}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update(
        {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    )
else:
    engine_kwargs.update(
        {
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        }
    )

engine = create_engine(DATABASE_URL, **engine_kwargs)

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
        _apply_migrations()
    except Exception as e:
        print(f"[DATABASE ERROR] Failed to create tables: {e}")
        # Don't raise - allow app to start even if DB init fails


def _apply_migrations():
    """Apply lightweight schema migrations that create_all doesn't handle."""
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            if DATABASE_URL.startswith("sqlite"):
                # Check if unique index on file_hash already exists
                result = conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='index' AND name='uq_knowledge_documents_file_hash'")
                ).fetchone()
                if not result:
                    conn.execute(
                        text("CREATE UNIQUE INDEX IF NOT EXISTS uq_knowledge_documents_file_hash ON knowledge_documents(file_hash) WHERE file_hash IS NOT NULL")
                    )
                    conn.commit()
                    print("[DATABASE] Applied migration: uq_knowledge_documents_file_hash index")
            else:
                # PostgreSQL - CREATE UNIQUE INDEX CONCURRENTLY is not allowed in a transaction
                conn.execute(text("SET LOCAL lock_timeout = '5s'"))
                conn.execute(
                    text(
                        "CREATE UNIQUE INDEX IF NOT EXISTS uq_knowledge_documents_file_hash "
                        "ON knowledge_documents(file_hash) WHERE file_hash IS NOT NULL"
                    )
                )
                conn.commit()
                print("[DATABASE] Applied migration: uq_knowledge_documents_file_hash index")
    except Exception as e:
        # Non-fatal: index may already exist or table not yet created
        print(f"[DATABASE] Migration note: {e}")
