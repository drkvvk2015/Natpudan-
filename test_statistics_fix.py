#!/usr/bin/env python
"""Test script to verify the statistics endpoint returns correct data"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.models import KnowledgeDocument
from backend.app.database import SessionLocal

def test_statistics():
    """Test database statistics query"""
    db = SessionLocal()
    try:
        # Get document count and total chunks from database
        db_docs = db.query(KnowledgeDocument).all()
        db_doc_count = len(db_docs)
        db_total_chunks = sum(doc.chunk_count or 0 for doc in db_docs)
        
        # Get unique categories
        db_categories = set()
        for doc in db_docs:
            if doc.category and doc.category.strip():
                db_categories.add(doc.category.strip())
        
        print("[OK] Database Statistics Query Results:")
        print(f"  Total Documents: {db_doc_count}")
        print(f"  Total Chunks: {db_total_chunks}")
        print(f"  Unique Categories: {len(db_categories)}")
        
        if db_categories:
            print(f"\n  Categories found:")
            for cat in sorted(db_categories):
                print(f"    - {cat}")
        else:
            print(f"\n  No categories found - documents need categorization")
        
        # Show first few documents
        print(f"\n  First 3 documents:")
        for doc in db_docs[:3]:
            print(f"    - {doc.filename}: {doc.chunk_count} chunks, category: {doc.category}")
        
        return {
            'total_documents': db_doc_count,
            'total_chunks': db_total_chunks,
            'categories_count': len(db_categories),
            'categories': list(db_categories)
        }
    finally:
        db.close()

if __name__ == '__main__':
    result = test_statistics()
    print(f"\n[RESULT] {result}")
