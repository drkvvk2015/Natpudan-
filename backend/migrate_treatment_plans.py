"""
Database migration script to add treatment plan tables
Run this to create the treatment plan tables in the database
"""

from app.database import engine, Base
from app.models.patient_intake_models import PatientIntake, TravelHistory, FamilyHistory
from app.models.treatment_plan import TreatmentPlan, Medication, FollowUp, MonitoringRecord
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Create treatment plan tables"""
    try:
        logger.info("Creating treatment plan tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Treatment plan tables created successfully!")
        logger.info("Tables created: treatment_plans, medications, follow_ups, monitoring_records")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
