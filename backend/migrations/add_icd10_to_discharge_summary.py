"""
Database migration to add icd10_codes column to discharge_summaries table.
Run this script to update existing database schema.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use SQLite database
DATABASE_URL = "sqlite:///./natpudan.db"


def migrate():
    """Add icd10_codes column to discharge_summaries table"""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
    
    with engine.connect() as connection:
        try:
            # Check if column already exists
            if "sqlite" in DATABASE_URL:
                result = connection.execute(text("PRAGMA table_info(discharge_summaries)"))
                columns = [row[1] for row in result]
            else:  # PostgreSQL
                result = connection.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='discharge_summaries'
                """))
                columns = [row[0] for row in result]
            
            if 'icd10_codes' in columns:
                logger.info("Column 'icd10_codes' already exists in discharge_summaries table")
                return
            
            # Add the column
            logger.info("Adding 'icd10_codes' column to discharge_summaries table...")
            connection.execute(text("""
                ALTER TABLE discharge_summaries 
                ADD COLUMN icd10_codes TEXT
            """))
            connection.commit()
            logger.info("✅ Successfully added 'icd10_codes' column")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            connection.rollback()
            raise


if __name__ == "__main__":
    logger.info("Starting database migration: add_icd10_to_discharge_summary")
    migrate()
    logger.info("Migration completed successfully")
