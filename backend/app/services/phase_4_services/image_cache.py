"""
Image Cache Service for Phase 4

Caches medical image analyses to:
- Avoid duplicate Claude Vision API calls
- Detect similar images (FAISS)
- Reduce latency for common images
- Track API costs

Usage:
    from app.services.phase_4_services.image_cache import ImageCacheManager
    
    cache = ImageCacheManager()
    cached_result = cache.get(image_hash)
    cache.set(image_hash, analysis_result)
"""

import hashlib
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger(__name__)


class ImageCache:
    """In-memory image analysis cache"""
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 168):
        """
        Initialize cache
        
        Args:
            max_size: Maximum cache entries
            ttl_hours: Time-to-live in hours (default 7 days)
        """
        self.cache = {}
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self.hits = 0
        self.misses = 0
        
    def get(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result"""
        if image_hash not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[image_hash]
        
        # Check TTL
        created_at = datetime.fromisoformat(entry["created_at"])
        if datetime.utcnow() - created_at > timedelta(hours=self.ttl_hours):
            del self.cache[image_hash]
            logger.info(f"Cache entry expired: {image_hash}")
            self.misses += 1
            return None
        
        self.hits += 1
        return entry["result"]
    
    def set(self, image_hash: str, result: Dict[str, Any]) -> None:
        """Cache an analysis result"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k]["created_at"]
            )
            del self.cache[oldest_key]
            logger.debug(f"Evicted oldest cache entry: {oldest_key}")
        
        self.cache[image_hash] = {
            "result": result,
            "created_at": datetime.utcnow().isoformat()
        }
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate (0-1)"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def clear(self) -> None:
        """Clear entire cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")


class ImageCacheManager:
    """
    Manages image analysis caching
    
    Features:
    - Content-based deduplication (hash-based)
    - Similar image detection (using FAISS for embeddings)
    - TTL-based expiration
    - Hit/miss metrics
    - Persistent storage (optional)
    """
    
    def __init__(self):
        """Initialize cache manager"""
        self.cache = ImageCache()
        self.similarity_index = None  # FAISS index for similar images
        self.image_embeddings = {}  # image_hash -> embedding
        
    def compute_image_hash(self, image_base64: str) -> str:
        """
        Compute SHA256 hash of image
        
        Args:
            image_base64: Base64 encoded image data
            
        Returns:
            Hex string hash (first 32 chars for readability)
        """
        return hashlib.sha256(image_base64.encode()).hexdigest()[:32]
    
    def get_cached_analysis(
        self,
        image_base64: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis for image
        
        Args:
            image_base64: Base64 encoded image data
            
        Returns:
            Cached analysis result or None if not found
        """
        image_hash = self.compute_image_hash(image_base64)
        return self.cache.get(image_hash)
    
    def cache_analysis(
        self,
        image_base64: str,
        analysis_result: Dict[str, Any]
    ) -> str:
        """
        Cache an analysis result
        
        Args:
            image_base64: Base64 encoded image data
            analysis_result: Analysis result to cache
            
        Returns:
            Image hash for future lookups
        """
        image_hash = self.compute_image_hash(image_base64)
        self.cache.set(image_hash, analysis_result)
        logger.info(f"Cached analysis for image: {image_hash}")
        return image_hash
    
    def find_similar_images(
        self,
        image_base64: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar images using embedding similarity
        
        TODO: Implement FAISS-based similarity search
        - Generate embedding for image
        - Query FAISS index for nearest neighbors
        - Return cached results for similar images
        
        Args:
            image_base64: Base64 encoded image data
            top_k: Number of similar images to return
            
        Returns:
            List of similar image analyses with similarity scores
        """
        logger.debug(f"Finding {top_k} similar images")
        return []  # To be implemented
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get cache metrics"""
        return {
            "cache_size": len(self.cache.cache),
            "cache_hits": self.cache.hits,
            "cache_misses": self.cache.misses,
            "hit_rate": round(self.cache.get_hit_rate(), 3),
            "max_size": self.cache.max_size,
            "ttl_hours": self.cache.ttl_hours
        }
    
    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()


# Singleton instance
_cache_manager: Optional[ImageCacheManager] = None


def get_image_cache_manager() -> ImageCacheManager:
    """Get or create image cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = ImageCacheManager()
    return _cache_manager
