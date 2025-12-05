#!/usr/bin/env python3
"""Clear all documents from knowledge base database"""

from app.database import SessionLocal
from app.models import KnowledgeDocument

def clear_knowledge_base():
    """Delete all documents from knowledge base"""
    db = SessionLocal()
    try:
        # Get count before deletion
        count_before = db.query(KnowledgeDocument).count()
        print(f"[INFO] Documents in KB: {count_before}")
        
        if count_before > 0:
            # Delete all documents
            db.query(KnowledgeDocument).delete()
            db.commit()
            
            # Verify deletion
            count_after = db.query(KnowledgeDocument).count()
            print(f"[OK] Deleted {count_before} documents")
            print(f"[OK] Remaining documents: {count_after}")
        else:
            print("[INFO] KB already empty")
        
    finally:
        db.close()

if __name__ == "__main__":
    clear_knowledge_base()
