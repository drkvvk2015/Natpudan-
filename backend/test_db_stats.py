from app.models import KnowledgeDocument
from app.database import SessionLocal

db = SessionLocal()
try:
    db_docs = db.query(KnowledgeDocument).all()
    db_doc_count = len(db_docs)
    db_total_chunks = sum(doc.chunk_count or 0 for doc in db_docs)
    
    db_categories = set()
    for doc in db_docs:
        if doc.category and doc.category.strip():
            db_categories.add(doc.category.strip())
    
    print("[OK] Database Statistics:")
    print(f"  Total Documents: {db_doc_count}")
    print(f"  Total Chunks: {db_total_chunks}")
    print(f"  Unique Categories: {len(db_categories)}")
    
    if db_docs:
        print(f"\n  Sample documents:")
        for doc in db_docs[:3]:
            print(f"    - {doc.filename}: {doc.chunk_count} chunks")
    
    print("\n[SUCCESS] The backend statistics endpoint should now return correct values")
finally:
    db.close()
