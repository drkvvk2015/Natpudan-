"""
Phase 7: Model Performance Manager

Tracks model performance metrics, manages deployments, and enables A/B testing.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ...database.models import (
    ModelPerformance,
    ModelType,
    TrainingJob
)

logger = logging.getLogger(__name__)


class ModelPerformanceManager:
    """
    Manages model performance tracking and deployment
    
    Features:
    - Performance metrics recording
    - Model activation/deactivation
    - A/B testing support
    - Deployment history
    - Performance comparison
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def record_performance(
        self,
        model_version: str,
        model_type: ModelType,
        accuracy: Optional[int] = None,
        precision: Optional[int] = None,
        recall: Optional[int] = None,
        f1_score: Optional[int] = None
    ) -> ModelPerformance:
        """
        Record model performance metrics
        
        Args:
            model_version: Version identifier
            model_type: Type of model
            accuracy: Overall accuracy percentage
            precision: Precision percentage
            recall: Recall percentage
            f1_score: F1 score percentage
            additional_metrics: Optional additional metrics
            
        Returns:
            Created ModelPerformance record
        """
        try:
            performance = ModelPerformance(
                model_version=model_version,
                model_type=model_type.value,
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1_score,
                is_active=False,  # Not active by default
                created_at=datetime.utcnow()
            )
            
            self.db.add(performance)
            self.db.commit()
            self.db.refresh(performance)
            
            logger.info(f"Recorded performance for {model_type.value} v{model_version}")
            return performance
            
        except Exception as e:
            logger.error(f"Error recording performance: {e}")
            self.db.rollback()
            raise
    
    def activate_model(
        self,
        model_version: str,
        model_type: ModelType,
        deactivate_others: bool = True
    ) -> ModelPerformance:
        """
        Activate a model version for production use
        
        Args:
            model_version: Version to activate
            model_type: Type of model
            deactivate_others: If True, deactivate other models of same type
            
        Returns:
            Activated ModelPerformance record
        """
        try:
            # Deactivate other models if requested
            if deactivate_others:
                self.db.query(ModelPerformance).filter(
                    ModelPerformance.model_type == model_type.value,
                    ModelPerformance.is_active == True
                ).update({
                    "is_active": False,
                    "deactivated_at": datetime.utcnow()
                })
            
            # Activate target model
            model = self.db.query(ModelPerformance).filter(
                ModelPerformance.model_version == model_version,
                ModelPerformance.model_type == model_type.value
            ).first()
            
            if not model:
                raise ValueError(f"Model {model_type.value} v{model_version} not found")
            
            model.is_active = True
            model.deployed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(model)
            
            logger.info(f"Activated model {model_type.value} v{model_version}")
            return model
            
        except Exception as e:
            logger.error(f"Error activating model: {e}")
            self.db.rollback()
            raise
    
    def deactivate_model(
        self,
        model_version: str,
        model_type: ModelType
    ) -> ModelPerformance:
        """
        Deactivate a model version
        
        Args:
            model_version: Version to deactivate
            model_type: Type of model
            
        Returns:
            Deactivated ModelPerformance record
        """
        try:
            model = self.db.query(ModelPerformance).filter(
                ModelPerformance.model_version == model_version,
                ModelPerformance.model_type == model_type.value
            ).first()
            
            if not model:
                raise ValueError(f"Model {model_type.value} v{model_version} not found")
            
            model.is_active = False
            model.deactivated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(model)
            
            logger.info(f"Deactivated model {model_type.value} v{model_version}")
            return model
            
        except Exception as e:
            logger.error(f"Error deactivating model: {e}")
            self.db.rollback()
            raise
    
    def get_active_model(self, model_type: ModelType) -> Optional[ModelPerformance]:
        """
        Get currently active model for a type
        
        Args:
            model_type: Type of model
            
        Returns:
            Active ModelPerformance or None
        """
        try:
            model = self.db.query(ModelPerformance).filter(
                ModelPerformance.model_type == model_type.value,
                ModelPerformance.is_active == True
            ).first()
            
            return model
            
        except Exception as e:
            logger.error(f"Error getting active model: {e}")
            return None
    
    def compare_models(
        self,
        model_version_a: str,
        model_version_b: str,
        model_type: ModelType
    ) -> Dict:
        """
        Compare performance of two models
        
        Args:
            model_version_a: First model version
            model_version_b: Second model version
            model_type: Type of model
            
        Returns:
            Comparison results
        """
        try:
            model_a = self.db.query(ModelPerformance).filter(
                ModelPerformance.model_version == model_version_a,
                ModelPerformance.model_type == model_type.value
            ).first()
            
            model_b = self.db.query(ModelPerformance).filter(
                ModelPerformance.model_version == model_version_b,
                ModelPerformance.model_type == model_type.value
            ).first()
            
            if not model_a or not model_b:
                raise ValueError("One or both models not found")
            
            comparison = {
                "model_type": model_type.value,
                "model_a": {
                    "version": model_version_a,
                    "accuracy": model_a.accuracy,
                    "precision": model_a.precision,
                    "recall": model_a.recall,
                    "f1_score": model_a.f1_score,
                    "is_active": model_a.is_active
                },
                "model_b": {
                    "version": model_version_b,
                    "accuracy": model_b.accuracy,
                    "precision": model_b.precision,
                    "recall": model_b.recall,
                    "f1_score": model_b.f1_score,
                    "is_active": model_b.is_active
                },
                "differences": {
                    "accuracy_delta": (model_a.accuracy or 0) - (model_b.accuracy or 0),
                    "precision_delta": (model_a.precision or 0) - (model_b.precision or 0),
                    "recall_delta": (model_a.recall or 0) - (model_b.recall or 0),
                    "f1_score_delta": (model_a.f1_score or 0) - (model_b.f1_score or 0)
                },
                "recommendation": self._get_recommendation(model_a, model_b)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing models: {e}")
            raise
    
    def get_model_history(
        self,
        model_type: ModelType,
        limit: int = 10
    ) -> List[ModelPerformance]:
        """
        Get historical performance records for a model type
        
        Args:
            model_type: Type of model
            limit: Maximum number of records
            
        Returns:
            List of ModelPerformance records
        """
        try:
            records = self.db.query(ModelPerformance).filter(
                ModelPerformance.model_type == model_type.value
            ).order_by(desc(ModelPerformance.created_at)).limit(limit).all()
            
            return records
            
        except Exception as e:
            logger.error(f"Error getting model history: {e}")
            return []
    
    def setup_ab_test(
        self,
        model_version_a: str,
        model_version_b: str,
        model_type: ModelType,
        traffic_split: float = 0.5
    ) -> Dict:
        """
        Setup A/B test between two models
        
        Args:
            model_version_a: First model version
            model_version_b: Second model version
            model_type: Type of model
            traffic_split: Percentage of traffic to model A (0.0-1.0)
            
        Returns:
            A/B test configuration
        """
        try:
            model_a = self.db.query(ModelPerformance).filter(
                ModelPerformance.model_version == model_version_a,
                ModelPerformance.model_type == model_type.value
            ).first()
            
            model_b = self.db.query(ModelPerformance).filter(
                ModelPerformance.model_version == model_version_b,
                ModelPerformance.model_type == model_type.value
            ).first()
            
            if not model_a or not model_b:
                raise ValueError("One or both models not found")
            
            # Update AB test configuration in additional_metrics
            ab_config = {
                "ab_test_active": True,
                "ab_test_partner": model_version_b,
                "traffic_split": traffic_split,
                "ab_test_started_at": datetime.utcnow().isoformat()
            }
            
            # Safely merge without dict unpack to avoid Mock incompatibilities
            existing_a = dict(model_a.additional_metrics or {})
            existing_a.update(ab_config)
            model_a.additional_metrics = existing_a
            
            ab_config_b = {
                "ab_test_active": True,
                "ab_test_partner": model_version_a,
                "traffic_split": 1.0 - traffic_split,
                "ab_test_started_at": datetime.utcnow().isoformat()
            }
            
            existing_b = dict(model_b.additional_metrics or {})
            existing_b.update(ab_config_b)
            model_b.additional_metrics = existing_b
            
            # Activate both models
            model_a.is_active = True
            model_b.is_active = True
            
            self.db.commit()
            
            logger.info(f"Setup A/B test: {model_version_a} vs {model_version_b}")
            
            return {
                "status": "ab_test_active",
                "model_a": model_version_a,
                "model_b": model_version_b,
                "traffic_split": {
                    "model_a": traffic_split,
                    "model_b": 1.0 - traffic_split
                },
                "started_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error setting up A/B test: {e}")
            self.db.rollback()
            raise
    
    def _get_recommendation(
        self,
        model_a: ModelPerformance,
        model_b: ModelPerformance
    ) -> str:
        """Get recommendation based on model comparison"""
        score_a = (
            (model_a.accuracy or 0) * 0.4 +
            (model_a.precision or 0) * 0.2 +
            (model_a.recall or 0) * 0.2 +
            (model_a.f1_score or 0) * 0.2
        )
        
        score_b = (
            (model_b.accuracy or 0) * 0.4 +
            (model_b.precision or 0) * 0.2 +
            (model_b.recall or 0) * 0.2 +
            (model_b.f1_score or 0) * 0.2
        )
        
        diff = score_a - score_b
        
        if abs(diff) < 2:
            return "Models are comparable - consider A/B testing"
        elif diff > 0:
            return f"Model A is better (+{diff:.1f} points)"
        else:
            return f"Model B is better (+{abs(diff):.1f} points)"
