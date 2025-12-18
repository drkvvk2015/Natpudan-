"""
Phase 5 API - Local Vision Models

Hybrid comparison endpoints to validate local models against Claude Vision.
Enables gradual migration from external APIs to self-hosted models.
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import Optional
import logging
import asyncio

from app.services.phase_5_services.local_vision_analyzer import LocalVisionAnalyzer
from app.services.phase_5_services.vision_model_manager import VisionModelManager
from app.services.phase_4_services.medical_image_analyzer import MedicalImageAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/phase-5", tags=["Phase 5 - Local Vision"])


@router.get("/health")
async def health_check():
    """Health check for Phase 5 services."""
    local_analyzer = LocalVisionAnalyzer()
    model_manager = VisionModelManager()
    
    info = model_manager.get_current_model_info()
    phase = "5B - MedSAM active" if info.get('model_id', '').startswith('medsam') else "5A - Rule-based foundation"
    return {
        "status": "healthy",
        "phase": phase,
        "local_analyzer": local_analyzer.get_statistics(),
        "model_manager": info,
        "message": "Phase 5 services operational. Local vision models active."
    }


@router.post("/image/analyze-local-only")
async def analyze_image_local_only(
    image: UploadFile = File(...),
    image_type: str = Form(...),
    clinical_context: str = Form("")
):
    """
    Analyze medical image using LOCAL models ONLY.
    
    Phase 5A: Uses rule-based analyzer
    Phase 5B: Will use MedSAM/MONAI
    
    Benefits:
    - Zero cost per image
    - Faster (no network latency)
    - Complete data privacy
    - Works offline
    """
    try:
        # Read image
        image_data = await image.read()
        
        # Analyze with local model
        local_analyzer = LocalVisionAnalyzer()
        result = await local_analyzer.analyze_image(
            image_data=image_data,
            image_type=image_type,
            clinical_context=clinical_context
        )
        
        return {
            "mode": "local_only",
            "result": result,
            "api_calls_made": 0,
            "cost": 0.0,
            "message": "Analysis completed using local models only"
        }
    
    except Exception as e:
        logger.error(f"Local analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/analyze-hybrid")
async def analyze_image_hybrid(
    image: UploadFile = File(...),
    image_type: str = Form(...),
    clinical_context: str = Form(""),
    compare_models: bool = Form(True)
):
    """
    HYBRID MODE: Run both local and Claude Vision in parallel.
    
    Use this to:
    - Validate local model accuracy
    - Compare speed and results
    - Build confidence in local models
    - Gradual migration strategy
    
    Returns:
    - Both results
    - Comparison metrics
    - Cost analysis
    """
    try:
        image_data = await image.read()
        
        # Initialize analyzers
        local_analyzer = LocalVisionAnalyzer()
        claude_analyzer = MedicalImageAnalyzer()
        
        if compare_models:
            # Run both in parallel
            logger.info("Running hybrid analysis (local + Claude Vision)")
            
            local_result, claude_result = await asyncio.gather(
                local_analyzer.analyze_image(image_data, image_type, clinical_context),
                claude_analyzer.analyze_image(image_data, image_type, clinical_context),
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(local_result, Exception):
                local_result = {"error": str(local_result), "findings": "Local analysis failed"}
            if isinstance(claude_result, Exception):
                claude_result = {"error": str(claude_result), "findings": "Claude analysis failed"}
            
            # Compare results
            comparison = {
                "local_model": local_result,
                "claude_vision": claude_result,
                "comparison": {
                    "severity_match": (
                        local_result.get('severity') == claude_result.get('severity')
                    ),
                    "confidence_delta": abs(
                        local_result.get('confidence', 0) - claude_result.get('confidence', 0)
                    ),
                    "local_processing_time_ms": local_result.get('processing_time_ms', 0),
                    "claude_processing_time_ms": claude_result.get('processing_time', 0),
                    "speed_improvement": (
                        f"{((claude_result.get('processing_time', 1000) - local_result.get('processing_time_ms', 0)) / claude_result.get('processing_time', 1000) * 100):.1f}%"
                        if claude_result.get('processing_time') else "N/A"
                    ),
                    "cost_comparison": {
                        "local": "$0.00",
                        "claude": "$0.03-0.05",
                        "savings_per_image": "$0.03-0.05"
                    }
                },
                "recommendation": "Review both results to build confidence in local model"
            }
            
            return comparison
        
        else:
            # Local only
            result = await local_analyzer.analyze_image(image_data, image_type, clinical_context)
            return {
                "mode": "local_only",
                "result": result,
                "message": "Analysis completed using local model (hybrid mode disabled)"
            }
    
    except Exception as e:
        logger.error(f"Hybrid analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/current")
async def get_current_model():
    """Get information about currently active local model."""
    model_manager = VisionModelManager()
    return model_manager.get_current_model_info()


@router.get("/models/available")
async def list_available_models():
    """List all available vision models."""
    model_manager = VisionModelManager()
    return model_manager.list_available_models()


@router.post("/models/switch")
async def switch_model(model_id: str):
    """
    Switch to a different vision model.
    
    Phase 5B will allow switching between:
    - rule_based_v1
    - medsam_v1
    - monai_v1
    - custom_finetuned_v1
    """
    model_manager = VisionModelManager()
    success = model_manager.switch_model(model_id)
    
    if success:
        return {
            "status": "success",
            "message": f"Switched to model: {model_id}",
            "current_model": model_manager.get_current_model_info()
        }
    else:
        # Differentiate between not found vs load failure
        available = model_manager.list_available_models().get('available_models', {})
        if model_id in available:
            err = available[model_id].get('load_error') or f"Failed to load {model_id}. Ensure required files and env vars are set."
            raise HTTPException(status_code=400, detail=err)
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Model {model_id} not found. Use /models/available to see options."
            )


@router.get("/statistics")
async def get_phase_5_statistics():
    """Get comprehensive Phase 5 statistics."""
    local_analyzer = LocalVisionAnalyzer()
    model_manager = VisionModelManager()
    
    phase = "5B - MedSAM active" if model_manager.get_current_model_info().get('model_id', '').startswith('medsam') else "5A - Rule-based foundation"
    return {
        "phase": phase,
        "analyzer_stats": local_analyzer.get_statistics(),
        "model_stats": model_manager.get_model_statistics(),
        "next_steps": {
            "phase_5b": "MedSAM integrated" if phase.startswith('5B') else "Integrate MedSAM or MONAI",
            "phase_5c": "Fine-tune on your patient cases",
            "phase_6": "Add local LLM (Ollama + LLaMA)",
            "phase_7": "Enable self-learning engine"
        }
    }


@router.post("/cache/clear")
async def clear_analysis_cache():
    """Clear local analysis cache."""
    local_analyzer = LocalVisionAnalyzer()
    local_analyzer.clear_cache()
    
    return {
        "status": "success",
        "message": "Analysis cache cleared",
        "stats": local_analyzer.get_statistics()
    }


@router.get("/roadmap")
async def get_phase_5_roadmap():
    """Get Phase 5 implementation roadmap."""
    return {
        "phase_5a": {
            "status": "✅ COMPLETE",
            "description": "Rule-based analyzer foundation",
            "features": [
                "Local image analysis (rule-based)",
                "Image caching and deduplication",
                "Hybrid comparison endpoint",
                "Model management infrastructure"
            ]
        },
        "phase_5b": {
            "status": "🚀 ACTIVE (MedSAM registered)",
            "description": "MedSAM model integrated with lazy loading and analysis pipeline",
            "tasks": [
                "Place checkpoint and set PHASE5_MEDSAM_CHECKPOINT",
                "Switch to medsam_v1 via /models/switch",
                "Run hybrid validation on clinical images"
            ],
            "estimated_time": "1-2 weeks for accuracy tuning"
        },
        "phase_5c": {
            "status": "📋 LATER (Week 3-4)",
            "description": "Fine-tune on your data",
            "tasks": [
                "Collect 100+ validated patient cases",
                "Fine-tune model on your dataset",
                "A/B test vs base model",
                "Deploy if accuracy improves"
            ],
            "estimated_time": "1-2 weeks"
        },
        "migration_strategy": {
            "week_1": "Run hybrid mode (both local + Claude)",
            "week_2": "Measure accuracy, speed, cost",
            "week_3": "10% traffic → local, 90% → Claude",
            "week_4": "50% traffic → local, 50% → Claude",
            "week_5": "100% traffic → local, Claude as fallback only",
            "result": "ZERO Claude Vision API calls by Week 5"
        }
    }
