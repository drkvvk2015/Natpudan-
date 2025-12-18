"""
Phase 5 Services - Local Vision Models

This module provides self-hosted medical image analysis
to replace external Claude Vision API.

Key Components:
- LocalVisionAnalyzer: Main analyzer using local models
- VisionModelManager: Model loading and caching
- HybridComparer: Compare local vs Claude Vision results
"""

from .local_vision_analyzer import LocalVisionAnalyzer
from .vision_model_manager import VisionModelManager

__all__ = [
    "LocalVisionAnalyzer",
    "VisionModelManager",
]
