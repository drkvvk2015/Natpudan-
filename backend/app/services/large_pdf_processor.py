"""
Large PDF Processing Service - Handle PDFs up to 1GB
Features: Streaming, chunking, parallel processing, memory optimization
"""

import logging
import os
from typing import List, Dict, Any, Optional, Generator
from pathlib import Path
import hashlib
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import gc

logger = logging.getLogger(__name__)

# Try importing PDF libraries
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF not available. Install with: pip install PyMuPDF")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class LargePDFProcessor:
    """
    Process large PDF files (up to 1GB) with memory optimization.
    Uses streaming, chunking, and parallel processing.
    """
    
    def __init__(
        self,
        max_file_size: int = 1024 * 1024 * 1024,  # 1GB
        chunk_size: int = 2000,  # Characters per chunk
        overlap: int = 200,  # Overlap between chunks
        max_workers: int = 4,  # Parallel processing threads
        cache_dir: str = "data/pdf_cache"
    ):
        self.max_file_size = max_file_size
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.max_workers = max_workers
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize sentence transformer for local embeddings
        self.embedder = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("[OK] Loaded local embedding model (all-MiniLM-L6-v2)")
            except Exception as e:
                logger.warning(f"Could not load sentence transformer: {e}")
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file for caching"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            # Read in 64KB chunks to handle large files
            for chunk in iter(lambda: f.read(65536), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def get_cached_extraction(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached extraction result if available"""
        cache_file = self.cache_dir / f"{file_hash}.json"
        if cache_file.exists():
            try:
                import json
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                logger.info(f"[OK] Using cached extraction for {file_hash[:8]}...")
                return cached
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
        return None
    
    def save_extraction_cache(self, file_hash: str, data: Dict[str, Any]):
        """Save extraction result to cache"""
        cache_file = self.cache_dir / f"{file_hash}.json"
        try:
            import json
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            logger.info(f"[OK] Cached extraction for {file_hash[:8]}...")
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    async def extract_text_streaming(
        self,
        file_path: Path,
        progress_callback: Optional[callable] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Extract text from large PDF in streaming mode.
        Yields chunks as they're processed to minimize memory usage.
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF required for large PDF processing")
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise ValueError(f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds limit ({self.max_file_size / 1024 / 1024:.2f} MB)")
        
        # Check cache
        file_hash = self.calculate_file_hash(file_path)
        cached = self.get_cached_extraction(file_hash)
        if cached:
            # Yield cached chunks
            for chunk in cached.get('chunks', []):
                yield chunk
            return
        
        logger.info(f"Processing large PDF: {file_path.name} ({file_size / 1024 / 1024:.2f} MB)")
        
        try:
            # Open PDF
            doc = fitz.open(str(file_path))
            total_pages = len(doc)
            
            all_chunks = []
            text_buffer = ""
            chunk_id = 0
            
            # Process pages in batches to manage memory
            batch_size = 10  # Process 10 pages at a time
            
            for batch_start in range(0, total_pages, batch_size):
                batch_end = min(batch_start + batch_size, total_pages)
                
                # Process batch
                for page_num in range(batch_start, batch_end):
                    page = doc[page_num]
                    
                    # Extract text
                    page_text = page.get_text("text")
                    
                    # Extract tables if available
                    try:
                        tables = page.find_tables()
                        if tables:
                            for table in tables:
                                table_data = table.extract()
                                if table_data:
                                    # Format table as text
                                    table_text = self._format_table(table_data)
                                    page_text += f"\n\n{table_text}\n\n"
                    except Exception as e:
                        logger.debug(f"Table extraction failed on page {page_num + 1}: {e}")
                    
                    # Add to buffer
                    text_buffer += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
                    
                    # Create chunks when buffer is large enough
                    while len(text_buffer) >= self.chunk_size:
                        chunk_text = text_buffer[:self.chunk_size]
                        text_buffer = text_buffer[self.chunk_size - self.overlap:]
                        
                        chunk_data = {
                            'chunk_id': chunk_id,
                            'text': chunk_text,
                            'metadata': {
                                'source': file_path.name,
                                'page_start': batch_start + 1,
                                'page_end': page_num + 1,
                                'file_hash': file_hash,
                                'char_count': len(chunk_text)
                            }
                        }
                        
                        all_chunks.append(chunk_data)
                        yield chunk_data
                        chunk_id += 1
                    
                    # Update progress
                    if progress_callback:
                        progress = (page_num + 1) / total_pages * 100
                        await progress_callback(progress, f"Processing page {page_num + 1}/{total_pages}")
                
                # Clean up memory after each batch
                gc.collect()
            
            # Process remaining buffer
            if text_buffer.strip():
                chunk_data = {
                    'chunk_id': chunk_id,
                    'text': text_buffer,
                    'metadata': {
                        'source': file_path.name,
                        'page_start': batch_start + 1,
                        'page_end': total_pages,
                        'file_hash': file_hash,
                        'char_count': len(text_buffer)
                    }
                }
                all_chunks.append(chunk_data)
                yield chunk_data
            
            # Close document
            doc.close()
            
            # Cache the extraction
            cache_data = {
                'file_hash': file_hash,
                'filename': file_path.name,
                'total_pages': total_pages,
                'total_chunks': len(all_chunks),
                'extracted_at': datetime.now().isoformat(),
                'chunks': all_chunks
            }
            self.save_extraction_cache(file_hash, cache_data)
            
            logger.info(f"[OK] Extracted {len(all_chunks)} chunks from {total_pages} pages")
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}", exc_info=True)
            raise
    
    def _format_table(self, table_data: List[List[str]]) -> str:
        """Format table data as readable text"""
        if not table_data:
            return ""
        
        lines = []
        for row in table_data:
            # Filter out empty cells
            cells = [str(cell).strip() for cell in row if cell]
            if cells:
                lines.append(" | ".join(cells))
        
        return "\n".join(lines)
    
    async def process_large_pdf(
        self,
        file_path: Path,
        add_to_kb: callable,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Process large PDF and add to knowledge base.
        Uses streaming to handle files up to 1GB.
        """
        start_time = datetime.now()
        chunks_processed = 0
        
        try:
            # Stream extraction and add to KB
            async for chunk in self.extract_text_streaming(file_path, progress_callback):
                # Add chunk to knowledge base
                await add_to_kb(
                    text=chunk['text'],
                    source=f"{file_path.name} (Chunk {chunk['chunk_id']})",
                    metadata=chunk['metadata']
                )
                chunks_processed += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'status': 'success',
                'filename': file_path.name,
                'file_size_mb': file_path.stat().st_size / 1024 / 1024,
                'chunks_processed': chunks_processed,
                'processing_time_seconds': processing_time,
                'chunks_per_second': chunks_processed / processing_time if processing_time > 0 else 0
            }
            
            logger.info(f"[OK] Processed {file_path.name}: {chunks_processed} chunks in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")
            return {
                'status': 'error',
                'filename': file_path.name,
                'error': str(e),
                'chunks_processed': chunks_processed
            }
    
    def generate_embeddings_batch(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Generate embeddings for multiple texts in batch (more efficient).
        Uses local Sentence Transformers model.
        """
        if not self.embedder:
            logger.warning("No embedding model available")
            return None
        
        try:
            embeddings = self.embedder.encode(texts, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Batch embedding error: {e}")
            return None
    
    def extract_medical_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract medical entities from text (diseases, symptoms, drugs, etc.).
        Simple pattern-based extraction - can be enhanced with NER models.
        """
        entities = {
            'diseases': [],
            'symptoms': [],
            'drugs': [],
            'procedures': [],
            'anatomical_terms': []
        }
        
        # Medical term patterns (expandable)
        patterns = {
            'diseases': [
                r'\b(diabetes|hypertension|asthma|cancer|pneumonia|covid|influenza)\b',
                r'\b\w+itis\b',  # Inflammations (bronchitis, arthritis)
                r'\b\w+oma\b',   # Tumors (carcinoma, melanoma)
            ],
            'symptoms': [
                r'\b(fever|pain|cough|headache|nausea|fatigue|dizziness)\b',
                r'\b(shortness of breath|chest pain)\b'
            ],
            'drugs': [
                r'\b\w+(cillin|mycin|azole|prazole|olol|dipine)\b',  # Drug suffixes
                r'\b(aspirin|ibuprofen|acetaminophen|metformin)\b'
            ]
        }
        
        import re
        text_lower = text.lower()
        
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                entities[category].extend(matches)
        
        # Remove duplicates and limit
        for category in entities:
            entities[category] = list(set(entities[category]))[:20]
        
        return entities
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processor statistics"""
        cache_files = list(self.cache_dir.glob("*.json"))
        total_cache_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'max_file_size_mb': self.max_file_size / 1024 / 1024,
            'chunk_size': self.chunk_size,
            'overlap': self.overlap,
            'max_workers': self.max_workers,
            'cache_enabled': True,
            'cached_files': len(cache_files),
            'total_cache_size_mb': total_cache_size / 1024 / 1024,
            'local_embeddings_available': self.embedder is not None,
            'embedding_model': 'all-MiniLM-L6-v2' if self.embedder else None
        }
    
    async def clear_cache(self, older_than_days: Optional[int] = None):
        """Clear extraction cache"""
        import time
        cleared = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                if older_than_days:
                    file_age_days = (time.time() - cache_file.stat().st_mtime) / 86400
                    if file_age_days < older_than_days:
                        continue
                
                cache_file.unlink()
                cleared += 1
            except Exception as e:
                logger.warning(f"Could not delete cache file {cache_file}: {e}")
        
        logger.info(f"Cleared {cleared} cache files")
        return {'cleared_files': cleared}


# Singleton instance
_large_pdf_processor = None

def get_large_pdf_processor() -> LargePDFProcessor:
    """Get or create large PDF processor singleton"""
    global _large_pdf_processor
    if _large_pdf_processor is None:
        _large_pdf_processor = LargePDFProcessor()
    return _large_pdf_processor
