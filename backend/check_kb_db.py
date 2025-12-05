"""Check knowledge base database"""
from app.database import SessionLocal
from app.models import KnowledgeDocument

db = SessionLocal()
try:
    docs = db.query(KnowledgeDocument).all()
    print(f'Total documents in DB: {len(docs)}')
    print(f'\nDocuments:')
    for d in docs:
        print(f'  - {d.filename}')
        print(f'    Chunks: {d.chunk_count}, Size: {d.file_size/1024/1024:.1f}MB')
        print(f'    Indexed: {d.is_indexed}, UUID: {d.document_id}')
        print()
finally:
    db.close()
