"""
BiomedBERT Embeddings Service
Advanced biomedical embeddings using domain-specific BERT model fine-tuned on medical texts.

BiomedBERT (Gururangan et al., 2020):
- BERT model fine-tuned on large biomedical corpus (PubMed, MIMIC)
- Superior performance on medical NLP tasks vs. generic BERT
- 768-dimensional embeddings optimized for clinical language

Free models available:
- allenai/scibert (SciBERT): Fine-tuned on scientific papers
- microsoft/BiomedBERT: Fine-tuned on medical texts
- microsoft/PubMedBERT: Fine-tuned on PubMed articles

Usage:
    embedder = BiomedBERTEmbeddings(model_name="microsoft/BiomedBERT")
    embeddings = embedder.embed_documents(texts)  # Batch embedding
    query_embedding = embedder.embed_query(query)  # Single query embedding
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional
import torch
from sentence_transformers import SentenceTransformer
import hashlib

logger = logging.getLogger(__name__)


class BiomedBERTEmbeddings:
    """
    Biomedical BERT embeddings service with medical domain optimization.
    
    Uses fine-tuned BERT models specifically trained on medical/biomedical corpora
    for superior performance on clinical language understanding.
    """
    
    def __init__(
        self,
        model_name: str = "allenai/scibert",
        device: str = "cpu",
        batch_size: int = 32,
        cache_embeddings: bool = True
    ):
        """
        Initialize BiomedBERT embeddings.
        
        Args:
            model_name: Hugging Face model identifier
                - "allenai/scibert" - SciBERT (768-dim)
                - "microsoft/BiomedBERT" - BiomedBERT (768-dim)
                - "microsoft/PubMedBERT" - PubMedBERT (768-dim)
            device: "cpu" or "cuda" for GPU acceleration
            batch_size: Batch size for embedding computation
            cache_embeddings: Whether to cache computed embeddings
        """
        self.model_name = model_name
        self.device = device if torch.cuda.is_available() else "cpu"
        self.batch_size = batch_size
        self.cache_embeddings = cache_embeddings
        self.embedding_cache = {}  # Hash -> embedding
        self.embedding_dim = 768  # Default for biomedical BERT models
        
        try:
            logger.info(f"Loading {model_name} model on device={self.device}...")
            self.model = SentenceTransformer(model_name, device=self.device)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"✅ Loaded {model_name} (dimension: {self.embedding_dim})")
        except Exception as e:
            logger.error(f"❌ Failed to load {model_name}: {e}")
            raise
    
    def _get_text_hash(self, text: str) -> str:
        """Get SHA-256 hash of text for caching"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def embed_documents(self, texts: List[str], metadata: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Embed multiple documents with biomedical BERT.
        
        Args:
            texts: List of texts to embed
            metadata: Optional list of metadata dicts (one per text)
            
        Returns:
            Dictionary containing:
                - embeddings: np.array of shape (len(texts), embedding_dim)
                - texts: Original texts
                - metadata: Metadata for each embedding
                - model_info: Model name and dimension
        """
        embeddings = []
        cache_hits = 0
        cache_misses = 0
        
        # Check cache
        uncached_indices = []
        uncached_texts = []
        
        for i, text in enumerate(texts):
            text_hash = self._get_text_hash(text)
            if text_hash in self.embedding_cache:
                embeddings.append(self.embedding_cache[text_hash])
                cache_hits += 1
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)
                embeddings.append(None)  # Placeholder
                cache_misses += 1
        
        # Compute uncached embeddings
        if uncached_texts:
            try:
                # Use model in eval mode for inference
                with torch.no_grad():
                    new_embeddings = self.model.encode(
                        uncached_texts,
                        batch_size=self.batch_size,
                        convert_to_numpy=True,
                        show_progress_bar=False
                    )
                
                # Cache and place results
                for orig_idx, new_idx in enumerate(uncached_indices):
                    embedding = new_embeddings[orig_idx]
                    text_hash = self._get_text_hash(uncached_texts[orig_idx])
                    
                    if self.cache_embeddings:
                        self.embedding_cache[text_hash] = embedding
                    
                    embeddings[new_idx] = embedding
                
                logger.info(f"📊 Embedding stats: cache_hits={cache_hits}, cache_misses={cache_misses}, "
                           f"cache_size={len(self.embedding_cache)}")
                
            except Exception as e:
                logger.error(f"❌ Error computing embeddings: {e}")
                raise
        
        return {
            "embeddings": np.array(embeddings),
            "texts": texts,
            "metadata": metadata or [{}] * len(texts),
            "model_info": {
                "model_name": self.model_name,
                "embedding_dim": self.embedding_dim,
                "device": self.device
            }
        }
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query text.
        
        Args:
            query: Query text to embed
            
        Returns:
            np.ndarray of shape (embedding_dim,)
        """
        query_hash = self._get_text_hash(query)
        
        if query_hash in self.embedding_cache:
            return self.embedding_cache[query_hash]
        
        try:
            with torch.no_grad():
                embedding = self.model.encode(query, convert_to_numpy=True)
            
            if self.cache_embeddings:
                self.embedding_cache[query_hash] = embedding
            
            return embedding
        
        except Exception as e:
            logger.error(f"❌ Error computing query embedding: {e}")
            raise
    
    def similarity(self, query_embedding: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
        """
        Compute cosine similarity between query and documents.
        
        Args:
            query_embedding: np.ndarray of shape (embedding_dim,)
            doc_embeddings: np.ndarray of shape (n_docs, embedding_dim)
            
        Returns:
            np.ndarray of shape (n_docs,) with similarity scores in [-1, 1]
        """
        # Normalize embeddings for cosine similarity
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
        doc_norms = doc_embeddings / (np.linalg.norm(doc_embeddings, axis=1, keepdims=True) + 1e-10)
        
        # Cosine similarity = dot product of normalized vectors
        similarities = np.dot(doc_norms, query_norm)
        return similarities
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get embedding cache statistics"""
        return {
            "cache_size": len(self.embedding_cache),
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "device": self.device,
            "memory_usage_mb": len(self.embedding_cache) * self.embedding_dim * 4 / (1024 ** 2)
        }
    
    def clear_cache(self):
        """Clear embedding cache"""
        self.embedding_cache.clear()
        logger.info("✅ Embedding cache cleared")


# Global instance manager
_biomedbert_instance: Optional[BiomedBERTEmbeddings] = None


def get_biomedbert_embeddings(
    model_name: str = "allenai/scibert",
    device: str = "cpu"
) -> BiomedBERTEmbeddings:
    """
    Get or create BiomedBERT embeddings instance (singleton pattern).
    
    Args:
        model_name: Hugging Face model identifier
        device: "cpu" or "cuda"
        
    Returns:
        BiomedBERTEmbeddings instance
    """
    global _biomedbert_instance
    
    if _biomedbert_instance is None:
        _biomedbert_instance = BiomedBERTEmbeddings(model_name=model_name, device=device)
    
    return _biomedbert_instance
