"""
Direct Knowledge Base Initialization Script
Processes PDFs directly without API calls - bypasses authentication
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.local_vector_kb import LocalVectorKnowledgeBase
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print(" NATPUDAN KNOWLEDGE BASE - DIRECT INITIALIZATION")
    print("=" * 60)
    
    # Initialize knowledge base
    kb_dir = backend_dir / "data" / "knowledge_base"
    kb = LocalVectorKnowledgeBase(storage_dir=str(kb_dir))
    
    # Check current status
    print("\n[STATS] Current Statistics:")
    stats = kb.get_statistics()
    print(f"   Documents: {stats['total_documents']}")
    print(f"   Chunks: {stats['total_chunks']}")
    print(f"   Model: {stats['embedding_model']}")
    
    # Get PDFs from medical_books directory
    medical_books_dir = backend_dir / "data" / "medical_books"
    pdf_files = list(medical_books_dir.glob("*.pdf"))
    
    print(f"\n[BOOKS] Found {len(pdf_files)} PDF files in {medical_books_dir}")
    
    if not pdf_files:
        print("[ERROR] No PDF files found!")
        return
    
    # Sort by size (process smallest first)
    pdf_files_sorted = sorted(pdf_files, key=lambda p: p.stat().st_size)
    
    total_size_mb = sum(p.stat().st_size for p in pdf_files) / (1024 * 1024)
    print(f"[STATS] Total size: {total_size_mb:.2f} MB")
    
    print("\n[STARTING] Starting PDF processing...")
    print("[TIMER]  This will take 30-60 minutes for large files")
    print("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i, pdf_path in enumerate(pdf_files_sorted, 1):
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_path.name}")
        print(f"            Size: {size_mb:.2f} MB")
        
        try:
            # Process PDF
            result = kb.add_document_from_file(str(pdf_path))
            
            if result.get("success"):
                chunks = result.get("chunks_added", 0)
                print(f"            [OK] Success! Added {chunks} chunks")
                success_count += 1
            else:
                error = result.get("error", "Unknown error")
                print(f"            [ERROR] Failed: {error}")
                fail_count += 1
                
        except Exception as e:
            print(f"            [ERROR] Error: {str(e)}")
            logger.exception(f"Failed to process {pdf_path.name}")
            fail_count += 1
        
        # Progress report every 5 files
        if i % 5 == 0:
            print("\n" + "-" * 60)
            print(f"[CHART] Progress: {i}/{len(pdf_files)} ({success_count} success, {fail_count} failed)")
            current_stats = kb.get_statistics()
            print(f"[STATS] Current: {current_stats['total_documents']} docs, {current_stats['total_chunks']} chunks")
            print("-" * 60)
    
    print("\n" + "=" * 60)
    print("[READY] PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"[OK] Successful: {success_count}")
    print(f"[ERROR] Failed: {fail_count}")
    
    # Final statistics
    print("\n[STATS] Final Knowledge Base Statistics:")
    final_stats = kb.get_statistics()
    print(f"   Documents: {final_stats['total_documents']}")
    print(f"   Chunks: {final_stats['total_chunks']}")
    print(f"   Model: {final_stats['embedding_model']}")
    print(f"   Dimension: {final_stats['embedding_dimension']}")
    print(f"   FAISS Available: {final_stats['faiss_available']}")
    
    print("\n[SUCCESS] Knowledge base is ready!")
    print("   Refresh http://localhost:5173/knowledge-base to see the data")

if __name__ == "__main__":
    main()
