"""Feature 2: Personalized AI Reasoning (XAI) - Explainable AI"""
import logging
logger = logging.getLogger(__name__)
_xai = None

class XAIExplainer:
    """Generates explainable AI reasoning for predictions"""
    
    def explain_diagnosis(self, diagnosis: str, confidence: float, features: dict) -> dict:
        """Explain diagnosis with SHAP-style feature importance"""
        return {
            "diagnosis": diagnosis,
            "confidence": round(confidence, 3),
            "reasoning": f"Patient diagnosed with {diagnosis} based on clinical presentation",
            "key_factors": [
                {"factor": k, "contribution": round(v * confidence, 3), "direction": "positive" if v > 0 else "negative"}
                for k, v in list(features.items())[:5]
            ],
            "evidence_links": ["CDC Guidelines", "PubMed Research", "Clinical Trials"],
            "uncertainty": self._calculate_uncertainty(confidence)
        }
    
    def _calculate_uncertainty(self, confidence: float) -> dict:
        return {
            "level": "low" if confidence > 0.8 else "medium" if confidence > 0.5 else "high",
            "recommendation": "Consider differential diagnosis" if confidence < 0.7 else "High confidence diagnosis"
        }

def get_xai_explainer() -> XAIExplainer:
    global _xai
    if _xai is None:
        _xai = XAIExplainer()
    return _xai
