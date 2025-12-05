#!/usr/bin/env python3
"""Auto-assign categories to knowledge base documents based on filename patterns."""

from app.database import SessionLocal
from app.models import KnowledgeDocument

# Define category mappings based on filename patterns
CATEGORY_MAPPINGS = {
    'mrcp': 'MRCP Exam',
    'mrcs': 'MRCS Exam',
    'oxford': 'Clinical Reference',
    'macleod': 'Clinical Reference',
    'harrison': 'Internal Medicine',
    'endocrinology': 'Endocrinology',
    'cardiovascular': 'Cardiology',
    'emergency': 'Emergency Medicine',
    'gynaecology': 'Obstetrics & Gynecology',
    'pharmacology': 'Pharmacology',
    'radiology': 'Radiology',
    'pediatric': 'Pediatrics',
    'differential': 'Diagnosis',
    'pocket': 'Clinical Reference'
}

def main():
    db = SessionLocal()
    try:
        docs = db.query(KnowledgeDocument).all()
        updated_count = 0
        
        print(f"\n[CATEGORIZATION] Processing {len(docs)} documents...\n")
        
        for doc in docs:
            filename_lower = doc.filename.lower()
            assigned_category = None
            
            # Find matching category
            for keyword, category in CATEGORY_MAPPINGS.items():
                if keyword in filename_lower:
                    assigned_category = category
                    break
            
            # Update if category found and not already set
            if assigned_category and (not doc.category or doc.category.strip() == ''):
                doc.category = assigned_category
                updated_count += 1
                print(f"[OK] {doc.filename[:50]:<50} -> {assigned_category}")
        
        db.commit()
        print(f"\n[RESULT] Updated {updated_count}/{len(docs)} documents with categories")
        
        # Show summary
        categories = set()
        for doc in docs:
            if doc.category and doc.category.strip():
                categories.add(doc.category)
        
        print(f"\n[CATEGORIES] {len(categories)} unique categories assigned:")
        for cat in sorted(categories):
            count = len([d for d in docs if d.category == cat])
            print(f"  - {cat}: {count} documents")
        
        print(f"\n[SUCCESS] Categorization complete!")

    finally:
        db.close()

if __name__ == '__main__':
    main()
