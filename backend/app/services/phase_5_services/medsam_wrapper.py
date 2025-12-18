"""
MedSAM Wrapper - Phase 5B

Lightweight wrapper to load a MedSAM checkpoint and run inference.

Notes:
- This wrapper assumes a SAM-like checkpoint (e.g., ViT-B/H) fine-tuned for medical images.
- We avoid hard dependencies beyond torch and numpy/PIL to keep install simple.
- If the checkpoint/model code requires the official 'segment_anything' package, this
  wrapper will try to import it; otherwise, it will raise a clear error.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional
import numpy as np

import torch

logger = logging.getLogger(__name__)


class MedSAMWrapper:
    def __init__(self) -> None:
        self.model: Optional[Any] = None
        self.device: str = 'cpu'
        self.model_name: str = 'MedSAM'
        self.model_version: str = '1.0.0'

    def load(self, checkpoint_path: str, device: str = 'cpu') -> None:
        """
        Load MedSAM checkpoint. This uses segment_anything's registry if available,
        else raises a helpful error instructing how to install dependencies.
        """
        try:
            try:
                from segment_anything import sam_model_registry  # type: ignore
            except Exception as e:
                raise RuntimeError(
                    "segment_anything not installed. Install it or provide a compatible loader."
                ) from e

            # Heuristic: use ViT-B by default unless overridden via env PHASE5_MEDSAM_MODEL
            import os
            arch = os.getenv('PHASE5_MEDSAM_MODEL', 'vit_b')
            if arch not in sam_model_registry:
                logger.warning(f"PHASE5_MEDSAM_MODEL={arch} not found; falling back to vit_b")
                arch = 'vit_b'

            self.device = device if torch.cuda.is_available() and device.startswith('cuda') else 'cpu'
            
            # Load with map_location to handle CUDA checkpoints on CPU
            # Monkey-patch torch.load temporarily to add map_location
            original_torch_load = torch.load
            def patched_load(f, *args, **kwargs):
                if 'map_location' not in kwargs and self.device == 'cpu':
                    kwargs['map_location'] = 'cpu'
                return original_torch_load(f, *args, **kwargs)
            
            try:
                torch.load = patched_load
                model = sam_model_registry[arch](checkpoint=checkpoint_path)  # type: ignore[index]
            finally:
                torch.load = original_torch_load
            
            model.to(device=self.device)
            model.eval()
            self.model = model
            logger.info(f"MedSAM loaded ({arch}) on device={self.device}")
        except Exception as e:
            logger.exception(f"Failed to load MedSAM: {e}")
            raise

    @torch.inference_mode()
    def analyze(self, image_array: np.ndarray, image_type: str = 'xray', clinical_context: str = '') -> Dict[str, Any]:
        """
        Run a simple forward pass pipeline.

        Note: SAM typically requires prompts (points/boxes). For Phase 5B baseline,
        we simulate an autoprompt approach by sampling center points and producing
        coarse region proposals. This provides usable regions_of_interest and a
        confidence score for downstream UX while keeping the code self-contained.
        """
        if self.model is None:
            raise RuntimeError("MedSAM model is not loaded")

        # Minimal preprocessing: ensure HxWxC uint8
        if image_array.ndim == 2:
            image_array = np.stack([image_array] * 3, axis=-1)
        image_array = image_array.astype(np.uint8)

        # Create dummy prompts: center point and a few offsets
        h, w, _ = image_array.shape
        cx, cy = w // 2, h // 2
        points = np.array([[cx, cy], [int(0.3 * w), int(0.3 * h)], [int(0.7 * w), int(0.7 * h)]])
        labels = np.array([1, 1, 1])

        # Use SAM predictor if available on model
        try:
            from segment_anything import SamPredictor  # type: ignore
            predictor = SamPredictor(self.model)
            predictor.set_image(image_array)
            masks, scores, _ = predictor.predict(point_coords=points, point_labels=labels, multimask_output=True)
            # Aggregate masks and take best score
            best_idx = int(np.argmax(scores))
            mask = masks[best_idx]
            score = float(scores[best_idx])

            roi_area = float(mask.sum())
            roi_ratio = roi_area / float(mask.size)
            severity = 'LOW'
            if roi_ratio > 0.4:
                severity = 'HIGH'
            elif roi_ratio > 0.15:
                severity = 'MODERATE'

            return {
                'summary': f'MedSAM segmentation produced a region proposal (ratio={roi_ratio:.2f}).',
                'severity': severity,
                'confidence': min(max(score, 0.0), 1.0),
                'rois': [
                    {
                        'type': 'mask',
                        'area': int(roi_area),
                        'ratio': float(roi_ratio),
                        'description': 'Auto-proposed region from MedSAM'
                    }
                ],
                'differentials': [],
                'recommendations': [
                    'Radiologist review recommended',
                    'Refine with interactive prompts for better localization'
                ],
                'model': 'medsam_v1'
            }
        except Exception as e:
            # If predictor is not available, return a graceful fallback using intensity map
            logger.warning(f"MedSAM predictor not available; using intensity-based fallback: {e}")
            gray = image_array.mean(axis=2)
            thr = gray.mean() + 0.5 * gray.std()
            mask = (gray > thr).astype(np.uint8)
            roi_area = float(mask.sum())
            roi_ratio = roi_area / float(mask.size)
            severity = 'LOW'
            if roi_ratio > 0.4:
                severity = 'HIGH'
            elif roi_ratio > 0.15:
                severity = 'MODERATE'

            return {
                'summary': f'MedSAM fallback segmentation by intensity (ratio={roi_ratio:.2f}).',
                'severity': severity,
                'confidence': 0.55,
                'rois': [
                    {
                        'type': 'mask',
                        'area': int(roi_area),
                        'ratio': float(roi_ratio),
                        'description': 'Heuristic region (predictor unavailable)'
                    }
                ],
                'differentials': [],
                'recommendations': [
                    'Install segment_anything for full MedSAM capability',
                    'Radiologist review recommended'
                ],
                'model': 'medsam_v1'
            }
