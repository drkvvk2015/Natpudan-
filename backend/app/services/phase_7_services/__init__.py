"""
Phase 7 Services - Self-Learning Engine

This package contains services for the self-learning engine:
- Data collection from validated diagnoses
- Automated model training
- A/B testing framework
- Auto-deployment system
"""

from .data_collector import DataCollector
from .training_scheduler import TrainingScheduler
from .model_performance_manager import ModelPerformanceManager

__version__ = "1.0.0"
__all__ = [
    "DataCollector",
    "TrainingScheduler",
    "ModelPerformanceManager"
]

