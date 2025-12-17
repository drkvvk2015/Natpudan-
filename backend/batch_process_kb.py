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
import hashlib
import argparse
from pathlib import Path
import sys

# Setup path
sys.path.insert(0, '.')

def parse_args():
    parser = argparse.ArgumentParser(description="Fast batch process pending KB files")
    parser.add_argument("--limit", type=int, default=None, help="Process at most N pending files")
    parser.add_argument("--dry-run", action="store_true", help="Scan and report only; do not embed or modify index")
    parser.add_argument("--keep-files", action="store_true", help="Do not delete processed pending files")
    parser.add_argument("--include-incomplete", action="store_true", help="Also process pending files not marked complete (processing/pending)")
    return parser.parse_args()


def main():
    from sentence_transformers import SentenceTransformer
    import faiss

    args = parse_args()
    
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

    # Build hash set for duplicate detection based on existing content
    existing_hashes = set()
    for m in metadata_list:
        content = m.get('content') if isinstance(m, dict) else None
        if content:
            digest = hashlib.sha1(content.encode('utf-8')).hexdigest()
            existing_hashes.add(digest)
    
    # Load embedding model
    print("\n[2/5] Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("  Model loaded (all-MiniLM-L6-v2, 384 dims)")
    
    # Load all pending files
    print("\n[3/5] Loading pending files...")
    files = sorted(pending_dir.glob('*.json'))
    if args.limit is not None:
        files = files[:max(args.limit, 0)]
    total_files = len(files)
    print(f"  Found {total_files} pending files")

    if total_files == 0:
        print("\n  No pending files to process!")
        return

    # Load all texts and metadata into memory
    texts = []
    metadatas = []
    file_paths = []

    skipped_incomplete = 0
    skipped_short = 0
    skipped_dupe = 0
    new_hashes = set()

    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)

            status = data.get('status', 'complete')
            if (not args.include_incomplete) and status != 'complete':
                skipped_incomplete += 1
                continue

            text = (data.get('text') or '').strip()
            meta = data.get('metadata', {})

            if not text or len(text) <= 50:
                skipped_short += 1
                continue

            # Deduplicate by text hash (existing index + this batch)
            text_hash = hashlib.sha1(text.encode('utf-8')).hexdigest()
            if text_hash in existing_hashes or text_hash in new_hashes:
                skipped_dupe += 1
                continue

            # Keep
            texts.append(text)
            metadatas.append(meta)
            file_paths.append(f)
            new_hashes.add(text_hash)
        except Exception as e:
            # Skip bad files but show minimal context
            print(f"  Warning: failed to read {f.name}: {e}")

    valid_count = len(texts)
    print(f"  Loaded {valid_count} valid documents")
    if skipped_incomplete:
        print(f"    Skipped {skipped_incomplete} incomplete/processing files")
    if skipped_short:
        print(f"    Skipped {skipped_short} very short/empty files")
    if skipped_dupe:
        print(f"    Skipped {skipped_dupe} duplicates (already indexed)")

    if valid_count == 0:
        print("\n  No valid documents to embed!")
        return
    
    if args.dry_run:
        print("\n[4/5] Dry run enabled - skipping embedding/index updates")
        all_embeddings = None
        embed_time = 0.0
    else:
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
    
    if not args.dry_run:
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
    else:
        print("  Dry run: skipping index/metadata writes")
    
    # Delete processed files
    print("\n[7/7] Cleaning up processed files...")
    deleted = 0
    if args.keep_files or args.dry_run:
        print("  Skipped deletion (keep-files or dry-run enabled)")
    else:
        for f in file_paths:
            try:
                f.unlink()
                deleted += 1
            except:
                pass
        print(f"  Deleted {deleted} processed files")
    
    # Summary
    total_time = time.time() - start_time if not args.dry_run else 0.0
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
