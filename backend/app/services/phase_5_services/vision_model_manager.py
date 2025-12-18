"""
Vision Model Manager - Phase 5

Manages loading, caching, and versioning of vision models.
Currently manages configuration for rule-based analyzer.
TODO Phase 5B: Load and manage actual ML models (MedSAM, MONAI, etc.)
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime
import os

try:
    # Optional import; MedSAM integration will work only if this file is present
    from .medsam_wrapper import MedSAMWrapper
except Exception:
    MedSAMWrapper = None  # type: ignore

logger = logging.getLogger(__name__)


class VisionModelManager:
    """
    Manages vision model lifecycle.
    
    Phase 5A: Configuration management
    Phase 5B: Actual model loading (PyTorch, ONNX, etc.)
    Phase 5C: Multi-model management and A/B testing
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VisionModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        logger.info("Initializing VisionModelManager (Phase 5A)")
        
        self.current_model = "rule_based_v1"
        self.model_version = "1.0.0"
        self.models: Dict[str, Any] = {}
        self.loaded_models: Dict[str, Any] = {}
        
        # Model registry
        self.available_models: Dict[str, Dict[str, Any]] = {
            'rule_based_v1': {
                'name': 'Rule-based Analyzer',
                'version': '1.0.0',
                'type': 'heuristic',
                'status': 'active',
                'loaded_at': datetime.utcnow().isoformat()
            },
            # Phase 5B: MedSAM registration (lazy-loaded on demand)
            'medsam_v1': {
                'name': 'MedSAM (Medical Segment Anything)',
                'version': '1.0.0',
                'type': 'ml',
                'status': 'available',
                'requires': 'PHASE5_MEDSAM_CHECKPOINT',
                'device': os.getenv('PHASE5_DEVICE', 'cpu'),
                'loaded_at': None,
                'load_error': None
            },
        }
        
        self._initialized = True
        logger.info(f"✅ VisionModelManager initialized with model: {self.current_model}")
    
    def get_current_model_info(self) -> Dict:
        """Get information about currently active model."""
        return {
            'model_id': self.current_model,
            'model_info': self.available_models.get(self.current_model, {}),
            'phase': '5A (Rule-based foundation)',
            'next_phase': '5B (MedSAM/MONAI integration)',
            'models_available': len(self.available_models)
        }
    
    def list_available_models(self) -> Dict:
        """List all available models."""
        return {
            'current_model': self.current_model,
            'available_models': self.available_models,
            'count': len(self.available_models)
        }
    
    def register_model(
        self,
        model_id: str,
        model_name: str,
        model_version: str,
        model_type: str = 'ml'
    ) -> bool:
        """
        Register a new model in the system.
        
        Phase 5B will use this to register MedSAM, MONAI, etc.
        """
        try:
            self.available_models[model_id] = {
                'name': model_name,
                'version': model_version,
                'type': model_type,
                'status': 'registered',
                'loaded_at': datetime.utcnow().isoformat()
            }
            logger.info(f"✅ Registered model: {model_id} ({model_name} v{model_version})")
            return True
        except Exception as e:
            logger.error(f"Failed to register model {model_id}: {e}")
            return False
    
    def switch_model(self, model_id: str) -> bool:
        """Switch to a different model."""
        if model_id not in self.available_models:
            logger.error(f"Model {model_id} not found in registry")
            return False
        
        # If ML model, ensure it's loaded before switching
        if self.available_models[model_id].get('type') == 'ml':
            if not self._ensure_model_loaded(model_id):
                logger.error(f"Failed to load model {model_id}. Staying on {self.current_model}")
                return False
        
        previous_model = self.current_model
        self.current_model = model_id
        self.available_models[model_id]['status'] = 'active'
        
        if previous_model in self.available_models:
            self.available_models[previous_model]['status'] = 'inactive'
        
        logger.info(f"✅ Switched from {previous_model} to {model_id}")
        return True
    
    def get_model_statistics(self) -> Dict:
        """Get statistics for all models."""
        return {
            'current_model': self.current_model,
            'total_models': len(self.available_models),
            'models': self.available_models,
            'manager_version': '1.0.0',
            'phase': '5B' if self.current_model.startswith('medsam') else '5A'
        }

    # -------- Phase 5B: Model Loading Helpers --------
    def _ensure_model_loaded(self, model_id: str) -> bool:
        """Lazy-load ML model if required and not already loaded."""
        try:
            if model_id in self.loaded_models:
                return True

            if model_id == 'medsam_v1':
                if MedSAMWrapper is None:
                    self.available_models[model_id]['load_error'] = 'medsam_wrapper not available'
                    logger.error("MedSAMWrapper not available - import failed")
                    return False

                ckpt = os.getenv('PHASE5_MEDSAM_CHECKPOINT')
                device = os.getenv('PHASE5_DEVICE', 'cpu')
                if not ckpt or not os.path.exists(ckpt):
                    self.available_models[model_id]['load_error'] = 'Missing or invalid PHASE5_MEDSAM_CHECKPOINT'
                    logger.error("PHASE5_MEDSAM_CHECKPOINT missing or path not found")
                    return False

                wrapper = MedSAMWrapper()
                wrapper.load(checkpoint_path=ckpt, device=device)
                self.loaded_models[model_id] = wrapper
                self.available_models[model_id]['loaded_at'] = datetime.utcnow().isoformat()
                self.available_models[model_id]['load_error'] = None
                logger.info("✅ MedSAM model loaded successfully")
                return True

            logger.error(f"Unknown ML model_id: {model_id}")
            return False
        except Exception as e:
            logger.exception(f"Failed to load model {model_id}: {e}")
            if model_id in self.available_models:
                self.available_models[model_id]['load_error'] = str(e)
            return False

    def get_active_model_instance(self) -> Optional[Any]:
        """Return the active model instance if loaded (ML only)."""
        model_id = self.current_model
        return self.loaded_models.get(model_id)

    def get_active_model_type(self) -> str:
        info = self.available_models.get(self.current_model, {})
        return info.get('type', 'heuristic')


# TODO Phase 5B: Add actual model loading functions
"""
Example Phase 5B implementation:

import torch
from segment_anything import sam_model_registry

class MedSAMLoader:
    def load_medsam(self, checkpoint_path: str):
        sam = sam_model_registry["vit_h"](checkpoint=checkpoint_path)
        sam.to(device='cuda' if torch.cuda.is_available() else 'cpu')
        return sam
    
    def predict(self, image, model):
        with torch.no_grad():
            masks = model.predict(image)
        return masks
"""
