"""
Phase 6 API - Local LLM & RAG Integration

Endpoints for medical reasoning with local LLaMA + FAISS knowledge base.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/phase-6", tags=["Phase 6 - Local LLM"])


# Global references (to be set at startup)
_ollama_client = None
_rag_engine = None


def set_dependencies(ollama_client, rag_engine):
    """Set dependencies (called at startup)."""
    global _ollama_client, _rag_engine
    _ollama_client = ollama_client
    _rag_engine = rag_engine


@router.get("/health")
async def phase6_health():
    """Health check for Phase 6 local LLM services."""
    try:
        if _ollama_client is None:
            return {
                "status": "degraded",
                "phase": "6 - Local LLM Integration",
                "message": "Ollama client not initialized",
                "recommendation": "Start Ollama service and reinitialize"
            }
        
        is_available = await _ollama_client.is_available()
        
        return {
            "status": "operational" if is_available else "unavailable",
            "phase": "6 - Local LLM Integration",
            "ollama_available": is_available,
            "features": [
                "Local LLaMA inference",
                "RAG (Retrieval-Augmented Generation)",
                "Medical knowledge base integration",
                "Streaming responses",
                "Multi-turn chat"
            ],
            "message": "Phase 6 local LLM framework ready"
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "phase": "6 - Local LLM Integration",
            "error": str(e)
        }


@router.get("/models/available")
async def list_available_models():
    """List available models on Ollama."""
    try:
        if _ollama_client is None:
            raise HTTPException(status_code=503, detail="Ollama client not initialized")
        
        models = await _ollama_client.list_models()
        
        return {
            "status": "success",
            "models": models,
            "count": len(models),
            "current_model": _ollama_client.model
        }
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/models/pull")
async def download_model(model_name: str):
    """
    Download and install a model from Ollama registry.
    
    Args:
        model_name: Model to download (e.g., "llama2", "neural-chat")
    """
    try:
        if _ollama_client is None:
            raise HTTPException(status_code=503, detail="Ollama client not initialized")
        
        logger.info(f"Downloading model: {model_name}...")
        success = await _ollama_client.pull_model(model_name)
        
        if success:
            return {
                "status": "success",
                "model": model_name,
                "message": f"Successfully pulled {model_name}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to pull model {model_name}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/models/switch")
async def switch_model(model_name: str):
    """Switch to a different local model."""
    try:
        if _ollama_client is None:
            raise HTTPException(status_code=503, detail="Ollama client not initialized")
        
        _ollama_client.switch_model(model_name)
        
        return {
            "status": "success",
            "current_model": model_name,
            "message": f"Switched to {model_name}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error switching model: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/models/info")
async def get_model_info():
    """Get information about current model."""
    try:
        if _ollama_client is None:
            raise HTTPException(status_code=503, detail="Ollama client not initialized")
        
        info = await _ollama_client.get_model_info()
        
        return {
            "status": "success",
            "model": _ollama_client.model,
            "info": info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chat")
async def medical_chat(
    query: str,
    context: Optional[str] = None,
    max_tokens: int = 500,
    temperature: float = 0.7
) -> Dict[str, Any]:
    """
    Direct chat with local LLM (non-streaming).
    
    Args:
        query: Medical question
        context: Optional context/background
        max_tokens: Maximum response tokens
        temperature: Response temperature (0.0-2.0)
    """
    try:
        if _ollama_client is None:
            raise HTTPException(status_code=503, detail="Ollama client not initialized")
        
        logger.info(f"Processing medical chat: {query[:50]}...")
        
        response = await _ollama_client.generate(
            prompt=query,
            context=context,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {
            "status": "success",
            "query": query,
            "response": response,
            "model": _ollama_client.model,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chat/stream")
async def medical_chat_stream(
    query: str,
    context: Optional[str] = None,
    max_tokens: int = 500,
    temperature: float = 0.7
):
    """
    Streaming chat with local LLM (token-by-token).
    
    Args:
        query: Medical question
        context: Optional context
        max_tokens: Maximum response tokens
        temperature: Response temperature
        
    Returns:
        Server-sent events stream
    """
    try:
        if _ollama_client is None:
            raise HTTPException(status_code=503, detail="Ollama client not initialized")
        
        logger.info(f"Streaming chat: {query[:50]}...")
        
        async def generate():
            try:
                async for token in _ollama_client.generate_stream(
                    prompt=query,
                    context=context,
                    max_tokens=max_tokens,
                    temperature=temperature
                ):
                    # Send as SSE
                    yield f"data: {json.dumps({'token': token, 'model': _ollama_client.model})}\n\n"
            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error setting up stream: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rag/query")
async def rag_medical_query(
    query: str,
    include_sources: bool = True,
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """
    Medical query with RAG (retrieval + reasoning).
    Searches knowledge base + uses local LLM for synthesis.
    
    Args:
        query: Medical question
        include_sources: Include knowledge base sources
        max_tokens: Maximum response tokens
    """
    try:
        if _rag_engine is None:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")
        
        logger.info(f"RAG query: {query[:50]}...")
        
        result = await _rag_engine.rag_query(
            query=query,
            include_sources=include_sources,
            max_tokens=max_tokens
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rag/query/stream")
async def rag_medical_query_stream(
    query: str,
    include_sources: bool = True,
    max_tokens: int = 1000
):
    """
    Streaming RAG query (retrieve + stream generate).
    
    Args:
        query: Medical question
        include_sources: Include sources in metadata
        max_tokens: Maximum response tokens
        
    Returns:
        Server-sent events stream with metadata + tokens
    """
    try:
        if _rag_engine is None:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")
        
        logger.info(f"Streaming RAG query: {query[:50]}...")
        
        async def generate():
            try:
                async for chunk in _rag_engine.rag_query_stream(
                    query=query,
                    include_sources=include_sources,
                    max_tokens=max_tokens
                ):
                    yield f"data: {chunk}\n"
            except Exception as e:
                logger.error(f"RAG stream error: {e}")
                error_msg = {"type": "error", "error": str(e)}
                yield f"data: {json.dumps(error_msg)}\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error setting up RAG stream: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/medical-reasoning")
async def medical_reasoning(
    symptoms: str,
    history: Optional[str] = None,
    max_tokens: int = 1500
) -> Dict[str, Any]:
    """
    Medical reasoning endpoint combining RAG + LLM.
    
    Args:
        symptoms: Patient symptoms/complaint
        history: Medical history context
        max_tokens: Maximum response tokens
    """
    try:
        if _rag_engine is None:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")
        
        # Build comprehensive medical query
        query = f"Patient symptoms: {symptoms}"
        if history:
            query += f"\nMedical history: {history}"
        query += "\n\nBased on the medical knowledge base, what are the possible conditions and recommended diagnostic approaches?"
        
        logger.info("Performing medical reasoning...")
        
        result = await _rag_engine.rag_query(
            query=query,
            include_sources=True,
            max_tokens=max_tokens
        )
        
        result["reasoning_type"] = "medical_differential"
        result["timestamp"] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        logger.error(f"Error in medical reasoning: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics")
async def get_statistics() -> Dict[str, Any]:
    """Get Phase 6 statistics."""
    try:
        stats = {
            "phase": "6 - Local LLM Integration",
            "timestamp": datetime.now().isoformat()
        }
        
        if _ollama_client:
            stats["ollama"] = {
                "current_model": _ollama_client.model,
                "host": _ollama_client.host,
                "available": await _ollama_client.is_available()
            }
        
        if _rag_engine:
            stats["rag_engine"] = _rag_engine.get_statistics()
        
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/roadmap")
async def phase6_roadmap():
    """Get Phase 6 roadmap and status."""
    return {
        "phase": "6 - Local LLM Integration",
        "status": "operational",
        "components": {
            "ollama_integration": {
                "status": "ready",
                "features": ["Model management", "Streaming inference", "Chat", "Context handling"]
            },
            "rag_engine": {
                "status": "ready",
                "features": ["Knowledge base search", "Context building", "Response generation", "Streaming"]
            },
            "medical_reasoning": {
                "status": "ready",
                "features": ["Symptom analysis", "Differential diagnosis", "Knowledge integration"]
            }
        },
        "next_phase": "7 - Advanced Analytics & Optimization",
        "roadmap": [
            {"step": 1, "name": "Download LLaMA model", "endpoint": "POST /phase-6/models/pull", "param": "llama2"},
            {"step": 2, "name": "List available models", "endpoint": "GET /phase-6/models/available"},
            {"step": 3, "name": "Test direct chat", "endpoint": "POST /phase-6/chat"},
            {"step": 4, "name": "Test RAG query", "endpoint": "POST /phase-6/rag/query"},
            {"step": 5, "name": "Stream medical reasoning", "endpoint": "POST /phase-6/medical-reasoning"},
            {"step": 6, "name": "View statistics", "endpoint": "GET /phase-6/statistics"}
        ]
    }


@router.get("/setup-guide")
async def setup_guide():
    """Get Ollama setup guide for local LLM."""
    return {
        "phase": "6 - Local LLM Setup Guide",
        "steps": [
            {
                "step": 1,
                "name": "Install Ollama",
                "instructions": [
                    "Download from https://ollama.ai",
                    "macOS: brew install ollama",
                    "Linux: curl https://ollama.ai/install.sh | sh",
                    "Windows: Download .msi installer"
                ]
            },
            {
                "step": 2,
                "name": "Start Ollama service",
                "instructions": [
                    "ollama serve",
                    "Service will run on localhost:11434"
                ]
            },
            {
                "step": 3,
                "name": "Download LLaMA model",
                "instructions": [
                    "POST /phase-6/models/pull with model_name='llama2'",
                    "First download: ~5GB, may take 5-10 minutes",
                    "Subsequent loads: <1 second"
                ]
            },
            {
                "step": 4,
                "name": "Test inference",
                "instructions": [
                    "POST /phase-6/chat with simple query",
                    "Test streaming: POST /phase-6/chat/stream",
                    "Test RAG: POST /phase-6/rag/query"
                ]
            },
            {
                "step": 5,
                "name": "Production deployment",
                "instructions": [
                    "Run: ollama serve (in background or systemd)",
                    "Verify: GET /phase-6/health returns operational",
                    "Monitor: Watch logs for inference speed"
                ]
            }
        ],
        "models_available": [
            {"name": "llama2", "size": "~5GB", "speed": "~100ms/token on CPU"},
            {"name": "neural-chat", "size": "~4GB", "speed": "~150ms/token on CPU"},
            {"name": "mistral", "size": "~7GB", "speed": "~200ms/token on CPU"}
        ],
        "performance_notes": {
            "cpu_inference": "Slower but works on any machine",
            "gpu_acceleration": "NVIDIA/CUDA: 10x faster, requires NVIDIA GPU",
            "memory_requirement": "Minimum 8GB RAM, recommended 16GB+",
            "context_window": "LLaMA: 4K tokens, extended: 32K tokens"
        }
    }
