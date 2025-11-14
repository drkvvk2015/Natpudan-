"""
Hybrid Search Service - Combines vector similarity with BM25 keyword search
Uses reciprocal rank fusion (RRF) for optimal results
"""

import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict
import math

logger = logging.getLogger(__name__)

# Optional import
try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    logger.warning("rank-bm25 not available. Install with: pip install rank-bm25")
    BM25_AVAILABLE = False


class HybridSearchEngine:
    """
    Advanced hybrid search combining:
    1. Vector similarity (semantic understanding)
    2. BM25 keyword matching (exact term matching)
    3. Reciprocal Rank Fusion (RRF) for result merging
    """
    
    def __init__(self):
        self.bm25_index = None
        self.documents = []
        self.tokenized_docs = []
        logger.info("Hybrid search engine initialized")
    
    def index_documents(self, documents: List[Dict[str, Any]]):
        """
        Index documents for BM25 search.
        
        Args:
            documents: List of documents with 'content' field
        """
        if not BM25_AVAILABLE:
            logger.warning("BM25 not available, skipping indexing")
            return
        
        self.documents = documents
        
        # Tokenize documents
        self.tokenized_docs = [
            self._tokenize(doc.get('content', ''))
            for doc in documents
        ]
        
        # Build BM25 index
        if self.tokenized_docs:
            self.bm25_index = BM25Okapi(self.tokenized_docs)
            logger.info(f"Indexed {len(documents)} documents for BM25 search")
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for BM25.
        Simple whitespace + punctuation splitting.
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and split
        tokens = []
        current_token = []
        
        for char in text:
            if char.isalnum():
                current_token.append(char)
            else:
                if current_token:
                    tokens.append(''.join(current_token))
                    current_token = []
        
        if current_token:
            tokens.append(''.join(current_token))
        
        return tokens
    
    def bm25_search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Perform BM25 keyword search.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of documents with BM25 scores
        """
        if not BM25_AVAILABLE or self.bm25_index is None:
            return []
        
        # Tokenize query
        query_tokens = self._tokenize(query)
        
        # Get BM25 scores
        scores = self.bm25_index.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]
        
        # Build results
        results = []
        for rank, idx in enumerate(top_indices, 1):
            if scores[idx] > 0:  # Only include relevant results
                doc = self.documents[idx].copy()
                doc['bm25_score'] = float(scores[idx])
                doc['bm25_rank'] = rank
                results.append(doc)
        
        return results
    
    def hybrid_search(
        self,
        query: str,
        vector_results: List[Dict[str, Any]],
        top_k: int = 10,
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search using Reciprocal Rank Fusion (RRF).
        
        Args:
            query: Search query
            vector_results: Results from vector search
            top_k: Number of final results
            alpha: Weight for vector search (0-1). 0=BM25 only, 1=vector only
            
        Returns:
            Fused and re-ranked results
        """
        # Get BM25 results
        bm25_results = self.bm25_search(query, top_k=top_k * 2)
        
        if not bm25_results:
            # BM25 not available, return vector results only
            return vector_results[:top_k]
        
        # Apply Reciprocal Rank Fusion (RRF)
        # RRF formula: RRF(d) = sum(1 / (k + rank(d)))
        # where k is a constant (typically 60)
        k = 60
        rrf_scores = defaultdict(float)
        doc_map = {}
        
        # Add vector search results
        for rank, doc in enumerate(vector_results, 1):
            doc_id = doc.get('metadata', {}).get('document_id', str(rank))
            rrf_scores[doc_id] += alpha * (1 / (k + rank))
            doc_map[doc_id] = doc
        
        # Add BM25 results
        for rank, doc in enumerate(bm25_results, 1):
            doc_id = doc.get('metadata', {}).get('document_id', str(rank))
            rrf_scores[doc_id] += (1 - alpha) * (1 / (k + rank))
            
            # Merge document info
            if doc_id in doc_map:
                doc_map[doc_id]['bm25_score'] = doc.get('bm25_score', 0)
                doc_map[doc_id]['bm25_rank'] = doc.get('bm25_rank', 0)
            else:
                doc_map[doc_id] = doc
        
        # Sort by RRF score
        sorted_ids = sorted(
            rrf_scores.keys(),
            key=lambda x: rrf_scores[x],
            reverse=True
        )
        
        # Build final results
        results = []
        for doc_id in sorted_ids[:top_k]:
            doc = doc_map[doc_id]
            doc['rrf_score'] = float(rrf_scores[doc_id])
            results.append(doc)
        
        return results


# Global instance
_hybrid_search = None

def get_hybrid_search() -> HybridSearchEngine:
    """Get or create hybrid search instance"""
    global _hybrid_search
    if _hybrid_search is None:
        _hybrid_search = HybridSearchEngine()
    return _hybrid_search
