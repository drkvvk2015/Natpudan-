#!/usr/bin/env python3
"""Inspect the current Knowledge Base to see what metadata is stored."""

import sys
from pathlib import Path
import pickle

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.local_vector_kb import LocalVectorKnowledgeBase

def main():
    print("[SEARCH] INSPECTING KNOWLEDGE BASE METADATA")
    print("=" * 60)
    
    kb = LocalVectorKnowledgeBase(storage_dir="data/knowledge_base")
    
    print(f"\n[STATS] Total documents: {kb.document_count}")
    print(f"[STATS] Total chunks stored: {len(kb.documents)}")
    
    if len(kb.documents) > 0:
        print("\n[SEARCH] Inspecting first 3 documents:")
        for i, doc in enumerate(kb.documents[:3]):
            print(f"\n--- Document {i+1} ---")
            for key, value in doc.items():
                if key == 'chunk_text':
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
        
        print("\n[INFO] Keys found in documents:")
        all_keys = set()
        for doc in kb.documents:
            all_keys.update(doc.keys())
        
        for key in sorted(all_keys):
            count = sum(1 for doc in kb.documents if key in doc)
            print(f"  - {key}: present in {count}/{len(kb.documents)} chunks")
    
    print("\n[OK] Inspection complete!")

if __name__ == "__main__":
    main()
