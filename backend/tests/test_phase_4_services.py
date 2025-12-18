"""
Unit tests for Phase 4 services - Medical Image Analysis

Tests cover:
- Medical image analyzer service
- Image cache manager
- Claude Vision API integration (mocked)
"""

import pytest
import base64
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.services.phase_4_services.medical_image_analyzer import (
    MedicalImageAnalyzer,
    ImageType,
    ImageSeverity,
    get_medical_image_analyzer
)
from app.services.phase_4_services.image_cache import (
    ImageCache,
    ImageCacheManager,
    get_image_cache_manager
)


# ============================================================================
# Medical Image Analyzer Tests
# ============================================================================

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic Claude client"""
    with patch('app.services.phase_4_services.medical_image_analyzer.anthropic') as mock:
        # Create mock message response
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Normal chest X-ray. No acute findings.")]
        mock_message.model = "claude-3-5-sonnet-20241022"
        mock_message.usage.input_tokens = 1000
        mock_message.usage.output_tokens = 150
        
        # Configure mock client
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_message
        mock.Anthropic.return_value = mock_client
        
        yield mock


@pytest.fixture
def sample_image_data():
    """Sample image data (1x1 PNG)"""
    # Minimal valid PNG (1x1 pixel)
    png_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    return png_data


class TestMedicalImageAnalyzer:
    """Tests for MedicalImageAnalyzer service"""
    
    def test_singleton_pattern(self):
        """Test that get_medical_image_analyzer returns same instance"""
        analyzer1 = get_medical_image_analyzer()
        analyzer2 = get_medical_image_analyzer()
        assert analyzer1 is analyzer2
    
    def test_build_analysis_prompt_xray(self):
        """Test X-ray analysis prompt generation"""
        analyzer = MedicalImageAnalyzer()
        
        prompt = analyzer._build_analysis_prompt(
            ImageType.XRAY,
            patient_context={"age": 45, "symptoms": "chest pain"}
        )
        
        assert "chest X-ray" in prompt.lower()
        assert "findings" in prompt.lower()
        assert "age" in prompt.lower() or "45" in prompt
    
    def test_build_analysis_prompt_ecg(self):
        """Test ECG analysis prompt generation"""
        analyzer = MedicalImageAnalyzer()
        
        prompt = analyzer._build_analysis_prompt(ImageType.ECG)
        
        assert "ecg" in prompt.lower() or "electrocardiogram" in prompt.lower()
        assert "rhythm" in prompt.lower()
    
    def test_structure_findings_normal(self):
        """Test structuring findings from normal result"""
        analyzer = MedicalImageAnalyzer()
        
        response_text = "Normal chest X-ray. No acute findings. Heart size normal. Lungs clear."
        result = analyzer._structure_findings(response_text, ImageType.XRAY)
        
        assert result["severity"] == "NORMAL"
        assert len(result["findings"]) > 0
        assert result["confidence"] > 0.8
    
    def test_structure_findings_abnormal(self):
        """Test structuring findings from abnormal result"""
        analyzer = MedicalImageAnalyzer()
        
        response_text = "URGENT: Large pneumothorax on right side. Immediate intervention required."
        result = analyzer._structure_findings(response_text, ImageType.XRAY)
        
        assert result["severity"] in ["CRITICAL", "HIGH"]
        assert len(result["findings"]) > 0
        assert any("pneumothorax" in f.lower() for f in result["findings"])
    
    @pytest.mark.asyncio
    async def test_analyze_image_success(self, mock_anthropic_client, sample_image_data):
        """Test successful image analysis"""
        analyzer = MedicalImageAnalyzer()
        
        result = await analyzer.analyze_image(
            image_data=sample_image_data,
            image_type=ImageType.XRAY,
            patient_context={"clinical_context": "Routine checkup"}
        )
        
        assert "findings" in result
        assert "confidence" in result
        assert "severity" in result
        assert isinstance(result["findings"], list)
    
    @pytest.mark.asyncio
    async def test_analyze_image_fallback(self, sample_image_data):
        """Test fallback when API key not set"""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': ''}, clear=True):
            analyzer = MedicalImageAnalyzer()
            
            result = await analyzer.analyze_image(
                image_data=sample_image_data,
                image_type=ImageType.XRAY
            )
            
            # Should use fallback analysis
            assert "findings" in result
            assert "unavailable" in str(result["findings"]).lower()
    
    def test_fallback_analysis(self):
        """Test fallback rule-based analysis"""
        analyzer = MedicalImageAnalyzer()
        
        result = analyzer._fallback_rule_based_analysis(ImageType.XRAY)
        
        assert "findings" in result
        assert "severity" in result
        assert result["confidence"] < 0.8  # Lower confidence for fallback


# ============================================================================
# Image Cache Tests
# ============================================================================

class TestImageCache:
    """Tests for ImageCache service"""
    
    def test_cache_basic_operations(self):
        """Test basic cache get/set operations"""
        cache = ImageCache()
        
        # Set value
        cache.set("key1", {"findings": ["Normal"]}, ttl_seconds=60)
        
        # Get value
        value = cache.get("key1")
        assert value is not None
        assert value["findings"] == ["Normal"]
    
    def test_cache_expiration(self):
        """Test cache TTL expiration"""
        cache = ImageCache()
        
        # Set with 1 second TTL
        cache.set("key_expire", {"data": "test"}, ttl_seconds=1)
        
        # Should exist immediately
        assert cache.get("key_expire") is not None
        
        # Wait for expiration (in real test, use freezegun or similar)
        # For now, test that setting lower TTL works
        cache.set("key_expire", {"data": "test"}, ttl_seconds=0)
        assert cache.get("key_expire") is None
    
    def test_cache_statistics(self):
        """Test cache hit/miss statistics"""
        cache = ImageCache()
        
        # Initial stats
        initial_stats = cache.get_statistics()
        assert initial_stats["hits"] == 0
        assert initial_stats["misses"] == 0
        
        # Set and get (hit)
        cache.set("key1", {"data": "test"})
        cache.get("key1")
        
        # Get non-existent (miss)
        cache.get("key_nonexistent")
        
        stats = cache.get_statistics()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
    
    def test_cache_clear(self):
        """Test cache clear operation"""
        cache = ImageCache()
        
        cache.set("key1", {"data": "test1"})
        cache.set("key2", {"data": "test2"})
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestImageCacheManager:
    """Tests for ImageCacheManager service"""
    
    def test_singleton_pattern(self):
        """Test that get_image_cache_manager returns same instance"""
        manager1 = get_image_cache_manager()
        manager2 = get_image_cache_manager()
        assert manager1 is manager2
    
    def test_compute_image_hash(self, sample_image_data):
        """Test image hash computation"""
        manager = ImageCacheManager()
        
        hash1 = manager.compute_image_hash(sample_image_data)
        hash2 = manager.compute_image_hash(sample_image_data)
        
        # Same image should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 32  # SHA256 first 32 chars
    
    def test_compute_image_hash_different(self, sample_image_data):
        """Test different images produce different hashes"""
        manager = ImageCacheManager()
        
        hash1 = manager.compute_image_hash(sample_image_data)
        hash2 = manager.compute_image_hash(b"different_data")
        
        assert hash1 != hash2
    
    def test_cache_analysis(self, sample_image_data):
        """Test caching and retrieving analysis"""
        manager = ImageCacheManager()
        
        image_hash = manager.compute_image_hash(sample_image_data)
        analysis_data = {
            "findings": ["Normal chest X-ray"],
            "severity": "NORMAL",
            "confidence": 0.95
        }
        
        # Cache the analysis
        manager.cache_analysis(image_hash, analysis_data)
        
        # Retrieve from cache
        cached = manager.get_cached_analysis(image_hash)
        assert cached is not None
        assert cached["findings"] == analysis_data["findings"]
    
    def test_get_cache_statistics(self):
        """Test cache statistics retrieval"""
        manager = ImageCacheManager()
        
        stats = manager.get_cache_statistics()
        
        assert "total_entries" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_analysis_workflow(mock_anthropic_client, sample_image_data):
    """Test complete analysis workflow with caching"""
    analyzer = get_medical_image_analyzer()
    cache_manager = get_image_cache_manager()
    
    # Clear cache
    cache_manager.cache.clear()
    
    # First analysis (cache miss)
    result1 = await analyzer.analyze_image(
        image_data=sample_image_data,
        image_type=ImageType.XRAY
    )
    
    # Compute hash and cache
    image_hash = cache_manager.compute_image_hash(sample_image_data)
    cache_manager.cache_analysis(image_hash, result1)
    
    # Second analysis (cache hit)
    cached_result = cache_manager.get_cached_analysis(image_hash)
    
    assert cached_result is not None
    assert cached_result["findings"] == result1["findings"]
    
    # Verify cache stats
    stats = cache_manager.get_cache_statistics()
    assert stats["hits"] >= 1


@pytest.mark.asyncio
async def test_batch_analysis(mock_anthropic_client, sample_image_data):
    """Test batch image analysis"""
    analyzer = get_medical_image_analyzer()
    
    images = [
        (sample_image_data, ImageType.XRAY),
        (sample_image_data, ImageType.ECG),
        (sample_image_data, ImageType.ULTRASOUND)
    ]
    
    results = await analyzer.batch_analyze(images)
    
    assert len(results) == 3
    for result in results:
        assert "findings" in result
        assert "severity" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
