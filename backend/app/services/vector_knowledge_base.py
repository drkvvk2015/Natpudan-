"""
Vector Knowledge Base Service - Semantic search using FAISS and OpenAI embeddings

Added fallback: if FAISS or OpenAI client unavailable, perform simple keyword search over stored chunk texts.
"""

import logging
import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from datetime import datetime
import re

logger = logging.getLogger(__name__)

# Optional imports (will use stub if not available)
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    logger.warning("FAISS not available. Install with: pip install faiss-cpu")
    FAISS_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI not available. Install with: pip install openai")
    OPENAI_AVAILABLE = False


class VectorKnowledgeBase:
    """
    Vector-based knowledge base using FAISS for similarity search.
    Stores document chunks with OpenAI embeddings for semantic search.
    """
    
    def __init__(
        self,
        storage_dir: str = "data/knowledge_base",
        embedding_model: str = "text-embedding-3-small",
        embedding_dimension: int = 1536
    ):
        """
        Initialize vector knowledge base.
        
        Args:
            storage_dir: Directory to store index and metadata
            embedding_model: OpenAI embedding model to use
            embedding_dimension: Dimension of embeddings
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension
        
        self.index_path = self.storage_dir / "faiss_index.bin"
        self.metadata_path = self.storage_dir / "metadata.pkl"
        
        # Initialize OpenAI client
        self.openai_client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
        
        # Initialize FAISS index
        self.index = None
        self.documents = []  # Store document chunks with metadata
        self.document_count = 0
        
        # Load existing index if available
        self._load_index()
        
        logger.info(f"Vector knowledge base initialized with {self.document_count} documents")
    
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
                
                logger.info(f"Loaded existing index with {len(self.documents)} chunks")
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                self._initialize_new_index()
        else:
            self._initialize_new_index()
    
    def _initialize_new_index(self):
        """Initialize a new FAISS index"""
        if FAISS_AVAILABLE:
            # Use IndexFlatL2 for exact similarity search
            # For larger datasets, consider IndexIVFFlat or IndexHNSW
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
            
            logger.info(f"Saved index with {len(self.documents)} chunks")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Get embedding vector for text using OpenAI API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not self.openai_client:
            logger.warning("OpenAI client not available")
            return None
        
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            embedding = np.array(response.data[0].embedding, dtype='float32')
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None
    
    def _get_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[np.ndarray]:
        """
        Get embeddings for multiple texts in batches (10-20x faster than one-by-one).
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per API call (max 2048 for OpenAI)
            
        Returns:
            List of embedding vectors
        """
        if not self.openai_client:
            logger.warning("OpenAI client not available")
            return []
        
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = self.openai_client.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                batch_embeddings = [np.array(item.embedding, dtype='float32') for item in response.data]
                embeddings.extend(batch_embeddings)
                logger.info(f"Generated {len(batch_embeddings)} embeddings (batch {i//batch_size + 1})")
            except Exception as e:
                logger.error(f"Error getting batch embeddings: {e}")
                # Fallback to individual embeddings for this batch
                for text in batch:
                    emb = self._get_embedding(text)
                    if emb is not None:
                        embeddings.append(emb)
        
        return embeddings
    
    def add_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> int:
        """
        Add a document to the knowledge base with chunking.
        
        Args:
            content: Full document text
            metadata: Document metadata (filename, source, date, etc.)
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Number of chunks added
        """
        if not FAISS_AVAILABLE or not self.openai_client:
            logger.warning("FAISS or OpenAI not available, cannot add documents")
            return 0
        
        # Split content into chunks
        chunks = self._chunk_text(content, chunk_size, chunk_overlap)
        
        # PERFORMANCE: Generate embeddings in batch (10-20x faster)
        logger.info(f"Generating embeddings for {len(chunks)} chunks in batch...")
        embeddings_batch = self._get_embeddings_batch(chunks, batch_size=100)
        
        if len(embeddings_batch) != len(chunks):
            logger.warning(f"Only got {len(embeddings_batch)}/{len(chunks)} embeddings")
        
        chunks_added = 0
        documents_batch = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_batch)):
            # Store chunk with metadata
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_index': i,
                'chunk_text': chunk,
                'added_at': datetime.utcnow().isoformat()
            })
            
            documents_batch.append(chunk_metadata)
            chunks_added += 1
        
        # Add to FAISS index
        if embeddings_batch:
            embeddings_array = np.array(embeddings_batch, dtype='float32')
            self.index.add(embeddings_array)
            self.documents.extend(documents_batch)
            self.document_count += 1
            
            # Save index
            self._save_index()
            
            logger.info(f"Added document '{metadata.get('filename', 'unknown')}' with {chunks_added} chunks")
        
        return chunks_added
    
    def add_chunks_batch(
        self,
        chunks: List[str],
        metadata: Dict[str, Any]
    ) -> int:
        """
        Add pre-chunked text to knowledge base in batch (optimized for parallel processing).
        
        This is used by PDF processor for fast batch chunk insertion with shared embeddings.
        
        Args:
            chunks: List of pre-chunked text
            metadata: Document metadata to attach to all chunks
            
        Returns:
            Number of chunks added
        """
        if not FAISS_AVAILABLE or not self.openai_client:
            logger.warning("FAISS or OpenAI not available, cannot add chunks")
            return 0
        
        if not chunks:
            return 0
        
        # PERFORMANCE: Generate embeddings in batch (25x texts per API call)
        logger.debug(f"Generating embeddings for {len(chunks)} pre-chunked texts in batch...")
        embeddings_batch = self._get_embeddings_batch(chunks, batch_size=100)
        
        if len(embeddings_batch) != len(chunks):
            logger.warning(f"Only got {len(embeddings_batch)}/{len(chunks)} embeddings")
        
        chunks_added = 0
        documents_batch = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_batch)):
            # Store chunk with metadata
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_index': i,
                'chunk_text': chunk,
                'added_at': datetime.utcnow().isoformat()
            })
            
            documents_batch.append(chunk_metadata)
            chunks_added += 1
        
        # Add all to FAISS index at once
        if embeddings_batch:
            embeddings_array = np.array(embeddings_batch, dtype='float32')
            self.index.add(embeddings_array)
            self.documents.extend(documents_batch)
            self.document_count += 1
            
            # Save index
            self._save_index()
            
            logger.debug(f"Added batch of {chunks_added} chunks")
        
        return chunks_added
    
    def _chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum chunk size
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending
                for delimiter in ['. ', '! ', '? ', '\n\n']:
                    last_delimiter = text.rfind(delimiter, start, end)
                    if last_delimiter != -1:
                        end = last_delimiter + len(delimiter)
                        break
            
            chunks.append(text[start:end].strip())
            start = end - overlap
        
        return chunks
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of relevant document chunks with metadata and scores
        """
        # If vector stack not available, fallback to simple keyword search
        if not FAISS_AVAILABLE or not self.openai_client or not self.index:
            logger.warning("FAISS/OpenAI not available - using keyword fallback search")
            results = []
            q = query.lower()
            for doc in self.documents:
                text = (doc.get('chunk_text') or '').lower()
                if not text:
                    continue
                score = 0
                # simple scoring: count occurrences
                occurrences = len(re.findall(re.escape(q), text))
                if occurrences > 0:
                    score = occurrences
                else:
                    # partial match on words
                    for token in q.split():
                        if token and token in text:
                            score += 0.5
                if score > 0:
                    results.append({
                        'content': doc.get('chunk_text', ''),
                        'metadata': {k: v for k, v in doc.items() if k != 'chunk_text'},
                        'similarity_score': float(min(1.0, score / 10.0)),
                        'distance': 1.0 - float(min(1.0, score / 10.0))
                    })
            # sort by score desc
            results.sort(key=lambda r: r.get('similarity_score', 0), reverse=True)
            return results[:top_k]

        if len(self.documents) == 0:
            logger.warning("No documents in knowledge base")
            return []
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        if query_embedding is None:
            return []
        
        # Search FAISS index
        query_vector = np.array([query_embedding], dtype='float32')
        
        # Search for more results than needed for filtering
        search_k = min(top_k * 3, len(self.documents))
        distances, indices = self.index.search(query_vector, search_k)
        
        # Collect results
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx >= len(self.documents):
                continue
            
            doc = self.documents[idx]
            
            # Apply metadata filters
            if filter_metadata:
                match = all(
                    doc.get(key) == value
                    for key, value in filter_metadata.items()
                )
                if not match:
                    continue
            
            # Convert L2 distance to similarity score (0-1)
            similarity = 1 / (1 + distance)
            
            results.append({
                'content': doc.get('chunk_text', ''),
                'metadata': {k: v for k, v in doc.items() if k != 'chunk_text'},
                'similarity_score': float(similarity),
                'distance': float(distance)
            })
            
            if len(results) >= top_k:
                break
        
        return results
    
    def delete_document(self, document_id: str) -> int:
        """
        Delete all chunks of a document.
        
        Args:
            document_id: Document identifier
            
        Returns:
            Number of chunks deleted
        """
        # Find chunks to delete
        indices_to_keep = []
        documents_to_keep = []
        deleted_count = 0
        
        for i, doc in enumerate(self.documents):
            if doc.get('document_id') == document_id:
                deleted_count += 1
            else:
                indices_to_keep.append(i)
                documents_to_keep.append(doc)
        
        if deleted_count > 0:
            # Rebuild index (FAISS doesn't support deletion)
            self._initialize_new_index()
            
            if FAISS_AVAILABLE and self.openai_client and indices_to_keep:
                # Re-embed remaining documents
                for doc in documents_to_keep:
                    embedding = self._get_embedding(doc['chunk_text'])
                    if embedding is not None:
                        self.index.add(np.array([embedding], dtype='float32'))
                
            self.documents = documents_to_keep
            self.document_count -= 1
            self._save_index()
            
            logger.info(f"Deleted {deleted_count} chunks for document {document_id}")
        
        return deleted_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics.
        
        Returns:
            Statistics dictionary
        """
        unique_documents = set(doc.get('document_id') for doc in self.documents)
        
        return {
            'total_documents': self.document_count,
            'total_chunks': len(self.documents),
            'unique_document_ids': len(unique_documents),
            'embedding_model': self.embedding_model,
            'embedding_dimension': self.embedding_dimension,
            'faiss_available': FAISS_AVAILABLE,
            'openai_available': OPENAI_AVAILABLE and self.openai_client is not None,
            'index_size_bytes': self.index_path.stat().st_size if self.index_path.exists() else 0
        }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all unique documents in the knowledge base.
        
        Returns:
            List of document metadata
        """
        # Group chunks by document_id
        docs_dict = {}
        for doc in self.documents:
            doc_id = doc.get('document_id')
            if doc_id not in docs_dict:
                docs_dict[doc_id] = {
                    'document_id': doc_id,
                    'filename': doc.get('filename'),
                    'source': doc.get('source'),
                    'added_at': doc.get('added_at'),
                    'chunk_count': 0
                }
            docs_dict[doc_id]['chunk_count'] += 1
        
        return list(docs_dict.values())


# Global instance
_vector_kb = None

def get_vector_knowledge_base() -> VectorKnowledgeBase:
    """Get or create vector knowledge base instance"""
    global _vector_kb
    if _vector_kb is None:
        _vector_kb = VectorKnowledgeBase()
    return _vector_kb
