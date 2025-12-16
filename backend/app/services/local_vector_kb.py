"""
Local Vector Knowledge Base - Uses sentence-transformers instead of OpenAI
No API costs, no quota limits, runs entirely on your machine
"""

import logging
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

# Import local sentence transformer
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not available. Install with: pip install sentence-transformers")
    SENTENCE_TRANSFORMER_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    logger.warning("FAISS not available. Install with: pip install faiss-cpu")
    FAISS_AVAILABLE = False


class LocalVectorKnowledgeBase:
    """
    100% Local Vector Knowledge Base using sentence-transformers
    - No OpenAI API calls
    - No costs
    - No quota limits
    - Fast embedding generation (batch processing)
    - Good quality semantic search
    """
    
    def __init__(
        self,
        storage_dir: str = "data/knowledge_base",
        model_name: str = "all-MiniLM-L6-v2",  # Fast, good quality, 384 dimensions
        embedding_dimension: int = 384
    ):
        """
        Initialize local vector knowledge base.
        
        Args:
            storage_dir: Directory to store index and metadata
            model_name: Sentence transformer model (all-MiniLM-L6-v2, all-mpnet-base-v2, etc.)
            embedding_dimension: Dimension of embeddings (384 for MiniLM, 768 for mpnet)
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.model_name = model_name
        self.embedding_dimension = embedding_dimension
        
        self.index_path = self.storage_dir / "local_faiss_index.bin"
        self.metadata_path = self.storage_dir / "local_metadata.pkl"
        
        # Initialize local embedding model (LAZY LOADING - only when needed)
        self.embedding_model = None
        self.model_name_to_load = model_name
        self._model_loaded = False
        
        # DON'T load model during init - load it when first needed
        # This prevents backend startup delays
        logger.info(f"Local AI model configured: {model_name} (lazy loading - will load on first use)")
        
        # Initialize FAISS index
        self.index = None
        self.documents: List[Dict[str, Any]] = []
        self.document_count = 0

        # Hybrid/BM25 support (optional)
        try:
            from app.services.hybrid_search import HybridSearchEngine  # local import to avoid hard dependency
            self.hybrid_engine = HybridSearchEngine()
        except Exception:
            self.hybrid_engine = None
        self._bm25_indexed = False
        
        # Load existing index
        self._load_index()

        # Build BM25 index if we already have documents
        if self.hybrid_engine and self.documents:
            self._rebuild_bm25_index()
        
        logger.info(f"Local vector KB ready with {self.document_count} documents")
    
    def _load_index(self):
        """Load FAISS index and metadata from disk"""
        if self.index_path.exists() and self.metadata_path.exists():
            try:
                if FAISS_AVAILABLE:
                    self.index = faiss.read_index(str(self.index_path))
                
                with open(self.metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.document_count = data.get('document_count', 0)
                
                logger.info(f"Loaded local index with {len(self.documents)} chunks")
            except Exception as e:
                logger.error(f"Error loading local index: {e}")
                self._initialize_new_index()
        else:
            self._initialize_new_index()
    
    def _initialize_new_index(self):
        """Initialize a new FAISS index"""
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatL2(self.embedding_dimension)
        self.documents = []
        self.document_count = 0
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            if FAISS_AVAILABLE and self.index is not None:
                faiss.write_index(self.index, str(self.index_path))
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'document_count': self.document_count
                }, f)
            
            logger.info(f"Saved local index with {len(self.documents)} chunks")
        except Exception as e:
            logger.error(f"Error saving local index: {e}")

    def _rebuild_bm25_index(self):
        """(Re)build BM25 index for hybrid search"""
        if not self.hybrid_engine:
            return

        try:
            bm25_docs = [
                {
                    "content": doc.get("text", ""),
                    "metadata": doc.get("metadata", {})
                }
                for doc in self.documents
                if doc.get("text")
            ]
            self.hybrid_engine.index_documents(bm25_docs)
            self._bm25_indexed = True
            logger.info(f"Indexed {len(bm25_docs)} documents for BM25 hybrid search")
        except Exception as e:
            logger.warning(f"BM25 indexing failed: {e}")
            self._bm25_indexed = False
    
    def _ensure_model_loaded(self):
        """Load model on first use (lazy loading)"""
        if self._model_loaded:
            return
            
        if SENTENCE_TRANSFORMER_AVAILABLE and self.embedding_model is None:
            try:
                logger.info(f"[FAST] Loading embedding model once: {self.model_name_to_load}...")
                self.embedding_model = SentenceTransformer(self.model_name_to_load)
                self._model_loaded = True
                logger.info(f"[OK] Model loaded - future embeddings will be faster")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
    
    def _get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings locally (NO API CALLS, VERY FAST)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        self._ensure_model_loaded()  # Load model if not already loaded
        
        if not self.embedding_model:
            logger.warning("Local embedding model not available")
            return []
        
        try:
            # FAST: Process all texts at once (batched internally)
            embeddings = self.embedding_model.encode(
                texts,
                batch_size=128,  # Increased for maximum speed (no data loss)
                show_progress_bar=True,
                convert_to_numpy=True,
                normalize_embeddings=True  # Pre-normalize for faster search
                # Note: num_workers removed - not supported in newer sentence-transformers
            )
            logger.info(f"[OK] Generated {len(embeddings)} local embeddings (no API cost)")
            return [emb.astype('float32') for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating local embeddings: {e}")
            return []
    
    def add_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        chunk_size: int = 2000,
        chunk_overlap: int = 50
    ) -> int:
        """
        Add document with local embeddings (NO API CALLS).
        
        Args:
            content: Full document text
            metadata: Document metadata
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Number of chunks added
        """
        # CRITICAL: Load model FIRST before checking if it exists!
        self._ensure_model_loaded()
        
        if not self.embedding_model or not FAISS_AVAILABLE:
            logger.warning("Local embeddings or FAISS not available")
            return 0
        
        # Split into chunks
        chunks = self._chunk_text(content, chunk_size, chunk_overlap)
        
        # Generate embeddings locally (FAST, NO COST)
        logger.info(f"Generating local embeddings for {len(chunks)} chunks...")
        embeddings_batch = self._get_embeddings_batch(chunks)
        
        if len(embeddings_batch) != len(chunks):
            logger.warning(f"Only got {len(embeddings_batch)}/{len(chunks)} embeddings")
            return 0
        
        # Add to index
        chunks_added = 0
        documents_batch = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_batch)):
            # Build document entry with text and metadata
            metadata_copy = metadata.copy()
            metadata_copy.setdefault('category', metadata.get('category', 'general'))
            metadata_copy.setdefault('section', metadata.get('section', 'unspecified'))
            metadata_copy.setdefault('year', metadata.get('year'))
            metadata_copy.setdefault('outdated', metadata.get('outdated', False))
            metadata_copy.setdefault('filename', metadata.get('filename') or metadata.get('source'))

            doc_entry = {
                'text': chunk,  # The actual text content for search results
                'metadata': metadata_copy
            }
            doc_entry['metadata'].update({
                'chunk_index': i,
                'chunk_text': chunk,
                'added_at': datetime.utcnow().isoformat()
            })
            documents_batch.append(doc_entry)
            chunks_added += 1
        
        # Add to FAISS
        if embeddings_batch:
            embeddings_array = np.array(embeddings_batch, dtype='float32')
            self.index.add(embeddings_array)
            self.documents.extend(documents_batch)
            self.document_count += 1
            self._save_index()

            # Rebuild BM25 index so hybrid search includes the new content
            if self.hybrid_engine:
                self._rebuild_bm25_index()
            
            logger.info(f"[OK] Added '{metadata.get('source', 'unknown')}' with {chunks_added} chunks (LOCAL)")
        
        return chunks_added
    
    def _chunk_text(self, text: str, chunk_size: int = 2000, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks if chunks else [text]

    def _passes_filters(self, metadata: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> bool:
        if not filters:
            return True
        category = filters.get("category")
        section = filters.get("section")
        min_year = filters.get("min_year")
        allow_outdated = filters.get("allow_outdated", True)

        if category and metadata.get("category") and metadata.get("category") != category:
            return False
        if section and metadata.get("section") and section.lower() not in str(metadata.get("section", "")).lower():
            return False
        if min_year:
            try:
                year = int(metadata.get("year")) if metadata.get("year") else None
                if year and year < int(min_year):
                    return False
            except Exception:
                pass
        if not allow_outdated and metadata.get("outdated"):
            return False
        return True
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
        alpha: float = 0.6,
        use_bm25: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search using local embeddings (NO API CALLS) with optional BM25 hybrid fusion.
        """
        self._ensure_model_loaded()  # Load model if not already loaded
        
        if not self.embedding_model or not FAISS_AVAILABLE or self.index is None:
            logger.warning("Local search not available")
            return []
        
        if len(self.documents) == 0:
            return []

        if use_bm25 and self.hybrid_engine and not self._bm25_indexed:
            self._rebuild_bm25_index()
        
        try:
            # Generate query embedding locally
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)[0]
            query_embedding = query_embedding.astype('float32').reshape(1, -1)
            
            # Search FAISS (retrieve extra for filtering)
            k = min(max(top_k * 3, top_k), len(self.documents))
            distances, indices = self.index.search(query_embedding, k)
            
            vector_results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(self.documents):
                    doc = self.documents[idx].copy()
                    metadata = doc.get('metadata', {})
                    if not self._passes_filters(metadata, filters):
                        continue
                    similarity = 1.0 / (1.0 + dist)  # Convert distance to similarity
                    
                    if similarity >= min_score:
                        citation = {
                            "document_id": metadata.get("document_id") or metadata.get("document_uuid"),
                            "filename": metadata.get("filename") or metadata.get("source"),
                            "page": metadata.get("page") or metadata.get("page_number"),
                            "chunk_index": metadata.get("chunk_index"),
                            "section": metadata.get("section"),
                            "category": metadata.get("category"),
                            "year": metadata.get("year"),
                        }

                        vector_results.append({
                            'text': doc.get('text', ''),
                            'metadata': metadata,
                            'score': float(similarity),
                            'distance': float(dist),
                            'citation': citation,
                            'source_type': metadata.get('source', 'Local Vector KB'),
                            'document_title': metadata.get('title', 'Medical Reference')
                        })
            
            # BM25-only path if enabled
            if use_bm25 and self.hybrid_engine and self._bm25_indexed:
                fused = self.hybrid_engine.hybrid_search(
                    query=query,
                    vector_results=vector_results,
                    top_k=top_k,
                    alpha=alpha
                )
                results = fused
            else:
                results = sorted(vector_results, key=lambda r: r.get('score', 0), reverse=True)[:top_k]

            # Add previews/full text and enforce score filter
            final_results = []
            for doc in results:
                if doc.get('score', 0) < min_score:
                    continue
                text = doc.get('text', '')
                if text:
                    if len(text) <= 2000:
                        doc['full_text'] = text
                    else:
                        doc['full_text'] = text
                        doc['preview'] = text[:2000] + '...'
                final_results.append(doc)
            
            logger.info(f"Local search found {len(final_results)} results (hybrid={use_bm25})")
            return final_results
            
        except Exception as e:
            logger.error(f"Local search error: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return {
            "total_documents": self.document_count,
            "total_chunks": len(self.documents),
            "embedding_model": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "storage_type": "local (no API)",
            "faiss_available": FAISS_AVAILABLE,
            "model_loaded": self.embedding_model is not None,
            "hybrid_enabled": self.hybrid_engine is not None,
            "bm25_indexed": self._bm25_indexed
        }


# Global instance
_local_kb_instance = None

def get_local_knowledge_base() -> LocalVectorKnowledgeBase:
    """Get or create local knowledge base instance"""
    global _local_kb_instance
    if _local_kb_instance is None:
        _local_kb_instance = LocalVectorKnowledgeBase()
    return _local_kb_instance
