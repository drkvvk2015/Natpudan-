"""
Local Vision Analyzer - Phase 5

Self-hosted medical image analysis using local models.
Replaces Claude Vision API for cost savings, privacy, and self-learning.

Currently uses rule-based analysis as foundation.
TODO: Integrate MedSAM, MONAI, or other medical vision models.
"""

import hashlib
import io
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from PIL import Image
import numpy as np

from .vision_model_manager import VisionModelManager

logger = logging.getLogger(__name__)


class LocalVisionAnalyzer:
    """
    Self-hosted medical image analyzer.
    
    Phase 5A (Current): Rule-based analysis foundation
    Phase 5B (Next): MedSAM integration
    Phase 5C (Later): Custom fine-tuned models
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalVisionAnalyzer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        logger.info("Initializing LocalVisionAnalyzer (Phase 5A - Rule-based)")
        
        # Statistics
        self.analysis_count = 0
        self.total_processing_time = 0.0
        
        # Image cache
        self.cache = {}
        self.cache_hits = 0
        
        self._initialized = True
        logger.info("✅ LocalVisionAnalyzer initialized successfully")
    
    async def analyze_image(
        self,
        image_data: bytes,
        image_type: str,
        clinical_context: str = ""
    ) -> Dict:
        """
        Analyze medical image using LOCAL models.
        
        Args:
            image_data: Raw image bytes
            image_type: 'xray', 'ct', 'mri', 'ultrasound', 'pathology', 'ecg'
            clinical_context: Optional clinical information
        
        Returns:
            {
                'findings': str,
                'severity': 'CRITICAL|HIGH|MODERATE|LOW|NORMAL',
                'confidence': 0.0-1.0,
                'regions_of_interest': List[dict],
                'differential_diagnoses': List[str],
                'recommendations': List[str],
                'model': 'local_rule_based_v1',
                'processing_time_ms': float,
                'cache_used': bool
            }
        """
        start_time = time.time()
        
        # 1. Check cache
        image_hash = hashlib.sha256(image_data).hexdigest()
        if image_hash in self.cache:
            self.cache_hits += 1
            cached_result = self.cache[image_hash].copy()
            cached_result['cache_used'] = True
            cached_result['processing_time_ms'] = 5  # Cache lookup is instant
            logger.info(f"✅ Cache hit for image {image_hash[:8]}")
            return cached_result
        
        # 2. Load and preprocess image
        try:
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            image_array = np.array(image)
            image_stats = self._get_image_statistics(image_array)
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return self._error_response(str(e))
        
        # 3. Analyze based on current active model (Phase 5B aware)
        model_manager = VisionModelManager()
        active_type = model_manager.get_active_model_type()
        model_used = 'local_rule_based_v1'
        if active_type == 'ml' and model_manager.current_model.startswith('medsam'):
            model = model_manager.get_active_model_instance()
            if model is not None:
                try:
                    ml_out = model.analyze(image_array, image_type=image_type, clinical_context=clinical_context)
                    findings = {
                        'summary': ml_out.get('summary', 'MedSAM analysis'),
                        'severity': ml_out.get('severity', 'MODERATE'),
                        'confidence': ml_out.get('confidence', 0.6),
                        'rois': ml_out.get('rois', []),
                        'differentials': ml_out.get('differentials', []),
                        'recommendations': ml_out.get('recommendations', [])
                    }
                    model_used = 'medsam_v1'
                except Exception as e:
                    logger.warning(f"MedSAM analyze failed, falling back to rule-based: {e}")
                    findings = self._analyze_by_type(
                        image_array=image_array,
                        image_type=image_type,
                        clinical_context=clinical_context,
                        image_stats=image_stats
                    )
            else:
                findings = self._analyze_by_type(
                    image_array=image_array,
                    image_type=image_type,
                    clinical_context=clinical_context,
                    image_stats=image_stats
                )
        else:
            findings = self._analyze_by_type(
                image_array=image_array,
                image_type=image_type,
                clinical_context=clinical_context,
                image_stats=image_stats
            )
        
        # 4. Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        result = {
            'findings': findings['summary'],
            'severity': findings['severity'],
            'confidence': findings['confidence'],
            'regions_of_interest': findings.get('rois', []),
            'differential_diagnoses': findings.get('differentials', []),
            'recommendations': findings.get('recommendations', []),
            'model': model_used,
            'processing_time_ms': processing_time,
            'cache_used': False,
            'timestamp': datetime.utcnow().isoformat(),
            'image_type': image_type
        }
        
        # 5. Cache result
        self.cache[image_hash] = result.copy()
        
        # 6. Update statistics
        self.analysis_count += 1
        self.total_processing_time += processing_time
        
        logger.info(
            f"✅ Analysis complete: {image_type} in {processing_time:.1f}ms "
            f"(Total: {self.analysis_count}, Avg: {self.total_processing_time/self.analysis_count:.1f}ms)"
        )
        
        return result
    
    def _get_image_statistics(self, image_array: np.ndarray) -> Dict:
        """Extract basic image statistics for analysis."""
        return {
            'shape': image_array.shape,
            'mean_intensity': float(np.mean(image_array)),
            'std_intensity': float(np.std(image_array)),
            'min_intensity': float(np.min(image_array)),
            'max_intensity': float(np.max(image_array)),
            'dynamic_range': float(np.max(image_array) - np.min(image_array))
        }
    
    def _analyze_by_type(
        self,
        image_array: np.ndarray,
        image_type: str,
        clinical_context: str,
        image_stats: Dict
    ) -> Dict:
        """Route to appropriate analyzer based on image type."""
        
        analyzers = {
            'xray': self._analyze_xray,
            'ct': self._analyze_ct,
            'mri': self._analyze_mri,
            'ultrasound': self._analyze_ultrasound,
            'pathology': self._analyze_pathology,
            'ecg': self._analyze_ecg,
        }
        
        analyzer = analyzers.get(image_type, self._analyze_unknown)
        return analyzer(image_array, clinical_context, image_stats)
    
    def _analyze_xray(self, image_array: np.ndarray, clinical_context: str, stats: Dict) -> Dict:
        """Analyze X-ray images."""
        
        # Rule-based heuristics (Phase 5A)
        # TODO Phase 5B: Replace with MedSAM segmentation
        
        findings = {
            'summary': 'Chest X-ray analysis (rule-based): ',
            'severity': 'NORMAL',
            'confidence': 0.75,
            'rois': [],
            'differentials': [],
            'recommendations': []
        }
        
        # Check image quality
        if stats['dynamic_range'] < 50:
            findings['summary'] += 'Low contrast image, recommend repeat. '
            findings['severity'] = 'LOW'
            findings['recommendations'].append('Consider repeat imaging with adjusted technique')
            return findings
        
        # Basic density analysis
        mean_intensity = stats['mean_intensity']
        
        if mean_intensity < 80:
            findings['summary'] += 'Generally radiopaque appearance, suggest dense structures or fluid. '
            findings['rois'].append({
                'region': 'overall',
                'finding': 'Increased density',
                'concern': True
            })
            findings['differentials'] = [
                'Pleural effusion',
                'Consolidation',
                'Mass effect'
            ]
            findings['severity'] = 'MODERATE'
            findings['recommendations'] = [
                'Recommend CT chest for further characterization',
                'Clinical correlation advised'
            ]
        elif mean_intensity > 180:
            findings['summary'] += 'Hyperinflated appearance, consider emphysematous changes. '
            findings['rois'].append({
                'region': 'lung_fields',
                'finding': 'Hyperinflation',
                'concern': False
            })
            findings['differentials'] = ['Emphysema', 'Asthma', 'COPD']
            findings['severity'] = 'LOW'
        else:
            findings['summary'] += 'No acute cardiopulmonary process identified. '
            findings['recommendations'] = [
                'Clinical correlation recommended',
                'Follow-up as clinically indicated'
            ]
        
        # Context-based adjustments
        if clinical_context:
            if 'fever' in clinical_context.lower() or 'cough' in clinical_context.lower():
                findings['differentials'].insert(0, 'Pneumonia')
                findings['severity'] = 'MODERATE'
            if 'trauma' in clinical_context.lower() or 'fall' in clinical_context.lower():
                findings['differentials'].insert(0, 'Fracture')
                findings['recommendations'].insert(0, 'Rule out rib fractures')
        
        return findings
    
    def _analyze_ct(self, image_array: np.ndarray, clinical_context: str, stats: Dict) -> Dict:
        """Analyze CT scans."""
        return {
            'summary': 'CT scan analysis (rule-based): Image received, detailed analysis pending local model integration.',
            'severity': 'NORMAL',
            'confidence': 0.70,
            'rois': [],
            'differentials': [],
            'recommendations': [
                'Radiologist review recommended',
                'Local model integration pending (Phase 5B)'
            ]
        }
    
    def _analyze_mri(self, image_array: np.ndarray, clinical_context: str, stats: Dict) -> Dict:
        """Analyze MRI scans."""
        return {
            'summary': 'MRI analysis (rule-based): Image received, detailed analysis pending local model integration.',
            'severity': 'NORMAL',
            'confidence': 0.70,
            'rois': [],
            'differentials': [],
            'recommendations': [
                'Radiologist review recommended',
                'Local model integration pending (Phase 5B)'
            ]
        }
    
    def _analyze_ultrasound(self, image_array: np.ndarray, clinical_context: str, stats: Dict) -> Dict:
        """Analyze ultrasound images."""
        return {
            'summary': 'Ultrasound analysis (rule-based): Image received, detailed analysis pending local model integration.',
            'severity': 'NORMAL',
            'confidence': 0.70,
            'rois': [],
            'differentials': [],
            'recommendations': [
                'Radiologist review recommended',
                'Local model integration pending (Phase 5B)'
            ]
        }
    
    def _analyze_pathology(self, image_array: np.ndarray, clinical_context: str, stats: Dict) -> Dict:
        """Analyze pathology slides."""
        return {
            'summary': 'Pathology slide analysis (rule-based): Image received, detailed analysis pending local model integration.',
            'severity': 'NORMAL',
            'confidence': 0.70,
            'rois': [],
            'differentials': [],
            'recommendations': [
                'Pathologist review required',
                'Local model integration pending (Phase 5B)'
            ]
        }
    
    def _analyze_ecg(self, image_array: np.ndarray, clinical_context: str, stats: Dict) -> Dict:
        """Analyze ECG images."""
        return {
            'summary': 'ECG analysis (rule-based): Image received, detailed analysis pending local model integration.',
            'severity': 'NORMAL',
            'confidence': 0.70,
            'rois': [],
            'differentials': [],
            'recommendations': [
                'Cardiologist review recommended',
                'Local model integration pending (Phase 5B)'
            ]
        }
    
    def _analyze_unknown(self, image_array: np.ndarray, clinical_context: str, stats: Dict) -> Dict:
        """Handle unknown image types."""
        return {
            'summary': f'Unknown image type. Basic analysis: {stats["shape"]} image received.',
            'severity': 'LOW',
            'confidence': 0.50,
            'rois': [],
            'differentials': [],
            'recommendations': [
                'Specify correct image type for better analysis',
                'Specialist review recommended'
            ]
        }
    
    def _error_response(self, error_message: str) -> Dict:
        """Return error response."""
        return {
            'findings': f'Error processing image: {error_message}',
            'severity': 'LOW',
            'confidence': 0.0,
            'regions_of_interest': [],
            'differential_diagnoses': [],
            'recommendations': ['Re-upload image or contact support'],
            'model': 'local_rule_based_v1',
            'processing_time_ms': 0,
            'cache_used': False,
            'error': True
        }
    
    def get_statistics(self) -> Dict:
        """Get analyzer statistics."""
        avg_time = self.total_processing_time / self.analysis_count if self.analysis_count > 0 else 0
        cache_hit_rate = self.cache_hits / self.analysis_count if self.analysis_count > 0 else 0
        
        model_manager = VisionModelManager()
        return {
            'total_analyses': self.analysis_count,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': f'{cache_hit_rate * 100:.1f}%',
            'average_processing_time_ms': f'{avg_time:.1f}',
            'cache_size': len(self.cache),
            'model_version': model_manager.current_model,
            'phase': '5B (MedSAM active)' if model_manager.get_active_model_type() == 'ml' else '5A (Rule-based foundation)'
        }
    
    def clear_cache(self):
        """Clear image cache."""
        cache_size = len(self.cache)
        self.cache.clear()
        logger.info(f"✅ Cleared {cache_size} cached analyses")
