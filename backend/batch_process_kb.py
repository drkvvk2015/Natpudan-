#!/usr/bin/env python3
"""
FAST Batch Knowledge Base Processor
====================================
This script processes pending KB files ~50-100x faster by:
1. Loading ALL pending files into memory first
2. Batching texts together (500 at a time)
3. Embedding entire batches in single GPU/CPU calls
4. Bulk-adding to FAISS index

Expected: ~5-10 minutes instead of 5+ hours
"""

import json
import time
import pickle
import numpy as np
from pathlib import Path
import sys

# Setup path
sys.path.insert(0, '.')

def main():
    from sentence_transformers import SentenceTransformer
    import faiss
    
    print("=" * 60)
    print("FAST BATCH KNOWLEDGE BASE PROCESSOR")
    print("=" * 60)
    
    # Paths
    pending_dir = Path('data/knowledge_base/pending')
    kb_dir = Path('data/knowledge_base')
    index_path = kb_dir / 'local_faiss_index.bin'
    metadata_path = kb_dir / 'local_metadata.pkl'
    
    # Load existing index and metadata
    print("\n[1/5] Loading existing KB...")
    
    if index_path.exists():
        index = faiss.read_index(str(index_path))
        print(f"  Loaded FAISS index with {index.ntotal} vectors")
    else:
        # Create new index (384 dimensions for all-MiniLM-L6-v2)
        index = faiss.IndexFlatIP(384)
        print("  Created new FAISS index")
    
    if metadata_path.exists():
        with open(metadata_path, 'rb') as f:
            metadata_obj = pickle.load(f)
        # Handle dict format with 'documents' key
        if isinstance(metadata_obj, dict) and 'documents' in metadata_obj:
            metadata_list = metadata_obj.get('documents', [])
        elif isinstance(metadata_obj, list):
            metadata_list = metadata_obj
        else:
            metadata_list = []
        print(f"  Loaded {len(metadata_list)} metadata entries")
    else:
        metadata_list = []
        print("  Created new metadata list")
    
    # Load embedding model
    print("\n[2/5] Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("  Model loaded (all-MiniLM-L6-v2, 384 dims)")
    
    # Load all pending files
    print("\n[3/5] Loading pending files...")
    files = sorted(pending_dir.glob('*.json'))
    total_files = len(files)
    print(f"  Found {total_files} pending files")
    
    if total_files == 0:
        print("\n  No pending files to process!")
        return
    
    # Load all texts and metadata into memory
    texts = []
    metadatas = []
    file_paths = []
    
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            text = data.get('text', '').strip()
            meta = data.get('metadata', {})
            
            if text and len(text) > 50:
                texts.append(text)
                metadatas.append(meta)
                file_paths.append(f)
        except Exception as e:
            pass  # Skip bad files
    
    valid_count = len(texts)
    print(f"  Loaded {valid_count} valid documents")
    
    if valid_count == 0:
        print("\n  No valid documents to embed!")
        return
    
    # Batch embed all texts at once
    print("\n[4/5] Batch embedding all documents...")
    batch_size = 512  # Process 512 texts at a time for efficiency
    
    start_time = time.time()
    all_embeddings = []
    
    for i in range(0, valid_count, batch_size):
        batch_texts = texts[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (valid_count + batch_size - 1) // batch_size
        
        print(f"  Embedding batch {batch_num}/{total_batches} ({len(batch_texts)} texts)...", end='', flush=True)
        
        embeddings = model.encode(
            batch_texts,
            batch_size=128,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        all_embeddings.append(embeddings)
        print(f" Done!")
    
    # Concatenate all embeddings
    all_embeddings = np.vstack(all_embeddings).astype('float32')
    embed_time = time.time() - start_time
    print(f"  Embedded {valid_count} documents in {embed_time:.1f}s ({valid_count/embed_time:.1f} docs/sec)")
    
    # Add to FAISS index
    print("\n[5/5] Adding to FAISS index...")
    
    # Get current max ID (handle various metadata formats)
    max_id = 0
    if metadata_list:
        for m in metadata_list:
            if isinstance(m, dict):
                max_id = max(max_id, m.get('id', 0))
            elif isinstance(m, (int, float)):
                max_id = max(max_id, int(m))
    
    # Add embeddings to index
    index.add(all_embeddings)
    
    # Add metadata entries
    for i, meta in enumerate(metadatas):
        entry = {
            'id': max_id + i + 1,
            'content': texts[i][:1000],  # Store first 1000 chars
            **meta
        }
        metadata_list.append(entry)
    
    print(f"  Added {valid_count} vectors to index")
    print(f"  Index now has {index.ntotal} total vectors")
    
    # Save index and metadata
    print("\n[6/6] Saving to disk...")
    
    # Ensure directory exists
    kb_dir.mkdir(parents=True, exist_ok=True)
    
    faiss.write_index(index, str(index_path))
    print(f"  Saved FAISS index: {index_path}")
    
    # Save metadata in the expected format (dict with 'documents' key)
    metadata_obj = {
        'documents': metadata_list,
        'document_count': len(metadata_list)
    }
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata_obj, f)
    print(f"  Saved metadata: {metadata_path}")
    
    # Delete processed files
    print("\n[7/7] Cleaning up processed files...")
    deleted = 0
    for f in file_paths:
        try:
            f.unlink()
            deleted += 1
        except:
            pass
    print(f"  Deleted {deleted} processed files")
    
    # Summary
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    print(f"  Documents processed: {valid_count}")
    print(f"  Total vectors in KB: {index.ntotal}")
    print(f"  Total metadata entries: {len(metadata_list)}")
    print(f"  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"  Speed: {valid_count/total_time:.1f} documents/second")
    print("=" * 60)

if __name__ == '__main__':
    main()
