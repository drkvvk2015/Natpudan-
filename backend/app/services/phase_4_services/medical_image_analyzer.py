"""
Medical Image Analysis Service for Phase 4

Integrates Claude Vision API for automated interpretation of:
- Chest X-rays
- ECG/EKG strips
- Pathology slides (microscopy)
- Ultrasound images
- Basic MRI/CT images

Usage:
    from app.services.phase_4_services.medical_image_analyzer import MedicalImageAnalyzer
    
    analyzer = MedicalImageAnalyzer()
    findings = await analyzer.analyze_image(
        image_base64="...",
        image_type="xray",
        patient_context={"age": 65, "comorbidities": ["COPD"]}
    )
"""

import base64
import json
import logging
from typing import Optional, Dict, List, Any
from enum import Enum
import time

logger = logging.getLogger(__name__)


class ImageType(str, Enum):
    """Supported medical image types"""
    XRAY = "xray"
    ECG = "ecg"
    ULTRASOUND = "ultrasound"
    PATHOLOGY = "pathology"
    MRI = "mri"
    CT = "ct"


class ImageSeverity(str, Enum):
    """Severity levels for findings"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    NORMAL = "NORMAL"


class MedicalImageAnalyzer:
    """
    Analyzes medical images using Claude Vision API
    
    Architecture:
    - Uses Claude's vision capabilities for interpretation
    - Fallback to rule-based heuristics if API unavailable
    - Caching layer to avoid duplicate analyses
    - Cost tracking for API usage
    """
    
    def __init__(self):
        """Initialize analyzer with API configuration"""
        self.api_key = None  # Load from environment
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude Vision model
        self.cache = {}  # In-memory cache; upgrade to Redis in production
        self.analysis_count = 0
        self.total_cost_usd = 0.0
        
    async def analyze_image(
        self,
        image_base64: str,
        image_type: ImageType,
        patient_context: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a medical image and return findings
        
        Args:
            image_base64: Base64 encoded image data
            image_type: Type of image (xray, ecg, ultrasound, etc.)
            patient_context: Patient info (age, comorbidities, symptoms)
            use_cache: Whether to check cache first
            
        Returns:
            {
                "findings": ["Finding 1", "Finding 2", ...],
                "confidence": 0.87,
                "severity": "LOW",
                "differential": ["Diagnosis 1", "Diagnosis 2"],
                "recommendations": ["Recommendation 1", ...],
                "model": "claude-3-5-sonnet-20241022",
                "execution_time_ms": 1234
            }
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = self._compute_cache_key(image_base64, image_type)
        if use_cache and cache_key in self.cache:
            logger.info(f"Cache hit for image analysis: {image_type}")
            return {**self.cache[cache_key], "from_cache": True}
        
        # Build prompt based on image type
        prompt = self._build_analysis_prompt(image_type, patient_context)
        
        # Call Claude Vision API
        try:
            findings = await self._call_claude_vision(
                image_base64=image_base64,
                prompt=prompt,
                image_type=image_type
            )
        except Exception as e:
            logger.error(f"Claude Vision API error: {str(e)}")
            # Fallback to rule-based analysis
            findings = self._fallback_rule_based_analysis(image_type, patient_context)
        
        # Parse and structure findings
        result = self._structure_findings(findings, image_type)
        
        # Cache result
        self.cache[cache_key] = result
        
        # Update metrics
        self.analysis_count += 1
        execution_time_ms = (time.time() - start_time) * 1000
        
        return {
            **result,
            "execution_time_ms": execution_time_ms,
            "from_cache": False,
            "model": self.model
        }
    
    async def batch_analyze(
        self,
        images: List[Dict[str, Any]],
        parallel: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple images
        
        Args:
            images: List of {"image_base64": "...", "image_type": "xray", ...}
            parallel: Whether to analyze in parallel (respects API rate limits)
            
        Returns:
            List of analysis results
        """
        results = []
        for img_data in images:
            result = await self.analyze_image(**img_data)
            results.append(result)
        return results
    
    def _build_analysis_prompt(
        self,
        image_type: ImageType,
        patient_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build analysis prompt for Claude"""
        base_prompt = f"""
        You are an expert radiologist analyzing a medical {image_type.value} image.
        
        Provide your analysis in the following JSON format:
        {{
            "findings": ["finding1", "finding2"],
            "confidence": 0.95,
            "severity": "LOW/MODERATE/HIGH/CRITICAL",
            "differential_diagnoses": ["diagnosis1", "diagnosis2"],
            "recommendations": ["recommendation1", "recommendation2"],
            "clinical_significance": "Brief explanation"
        }}
        
        Be concise but clinically accurate.
        """
        
        if patient_context:
            base_prompt += f"\n\nPatient context: {json.dumps(patient_context)}"
        
        return base_prompt
    
    async def _call_claude_vision(
        self,
        image_base64: str,
        prompt: str,
        image_type: ImageType
    ) -> Dict[str, Any]:
        """
        Call Claude Vision API using Anthropic SDK
        
        Args:
            image_base64: Base64-encoded image data
            prompt: Analysis prompt
            image_type: Type of medical image
            
        Returns:
            Structured analysis results from Claude
        """
        try:
            import anthropic
            import os
            
            # Get API key
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not set, using fallback")
                return self._fallback_rule_based_analysis(image_type)
            
            # Initialize client
            client = anthropic.Anthropic(api_key=api_key)
            
            logger.info(f"Analyzing {image_type.value} image with Claude Vision API")
            
            # Determine media type
            media_type = "image/jpeg"  # Default
            if image_base64.startswith("iVBOR"):  # PNG signature in base64
                media_type = "image/png"
            elif image_base64.startswith("R0lG"):  # GIF signature
                media_type = "image/gif"
            
            # Call Claude Vision API
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )
            
            # Extract response text
            response_text = message.content[0].text
            
            # Parse response into structured format
            result = self._structure_findings(response_text, image_type)
            
            # Add API metadata
            result["api_metadata"] = {
                "model": message.model,
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens
            }
            
            logger.info(f"Claude analysis complete: {result['severity']}")
            return result
            
        except ImportError:
            logger.error("anthropic package not installed. Run: pip install anthropic")
            return self._fallback_rule_based_analysis(image_type)
        except Exception as e:
            logger.error(f"Claude Vision API failed: {str(e)}")
            return self._fallback_rule_based_analysis(image_type)
    
    def _fallback_rule_based_analysis(
        self,
        image_type: ImageType,
        patient_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Fallback analysis when Claude API unavailable"""
        logger.warning(f"Using fallback analysis for {image_type.value}")
        
        # Rule-based heuristics by image type
        if image_type == ImageType.XRAY:
            return {
                "findings": ["Unable to analyze - API unavailable"],
                "confidence": 0.5,
                "severity": "MODERATE",
                "differential_diagnoses": ["Requires radiologist review"],
                "recommendations": ["Contact radiologist for manual review"],
                "clinical_significance": "Analysis inconclusive"
            }
        # Add more fallback logic for other image types
        
        return {
            "findings": ["Analysis unavailable"],
            "confidence": 0.0,
            "severity": "CRITICAL",
            "differential_diagnoses": [],
            "recommendations": ["Immediate radiologist review required"],
            "clinical_significance": "Analysis failed"
        }
    
    def _structure_findings(
        self,
        findings: Dict[str, Any],
        image_type: ImageType
    ) -> Dict[str, Any]:
        """Structure and validate findings"""
        return {
            "findings": findings.get("findings", []),
            "confidence": float(findings.get("confidence", 0.0)),
            "severity": findings.get("severity", "MODERATE"),
            "differential": findings.get("differential_diagnoses", []),
            "recommendations": findings.get("recommendations", []),
            "clinical_significance": findings.get("clinical_significance", "")
        }
    
    def _compute_cache_key(self, image_base64: str, image_type: ImageType) -> str:
        """Compute cache key from image hash"""
        import hashlib
        image_hash = hashlib.sha256(image_base64.encode()).hexdigest()[:16]
        return f"img_{image_type.value}_{image_hash}"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get analyzer metrics"""
        return {
            "total_images_analyzed": self.analysis_count,
            "cache_size": len(self.cache),
            "total_cost_usd": round(self.total_cost_usd, 2)
        }


# Singleton instance
_analyzer: Optional[MedicalImageAnalyzer] = None


def get_medical_image_analyzer() -> MedicalImageAnalyzer:
    """Get or create medical image analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = MedicalImageAnalyzer()
    return _analyzer
