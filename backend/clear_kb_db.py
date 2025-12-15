"""Clear all knowledge base database records."""
import sys
sys.path.insert(0, '.')

from app.database import get_db
from app.models import KnowledgeDocument

def clear_kb():
    db = next(get_db())
    try:
        count = db.query(KnowledgeDocument).count()
        print(f"Found {count} KB documents in database")
        
        if count > 0:
            db.query(KnowledgeDocument).delete()
            db.commit()
            print(f"✓ Cleared {count} database records")
        else:
            print("✓ Database already empty")
    except Exception as e:
        print(f"✗ Database error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_kb()
