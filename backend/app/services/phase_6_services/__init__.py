"""
Phase 6 Initialization

Initialize Ollama client and RAG engine at startup.
Call from main.py lifespan context.
"""

import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

# Global instances
_ollama_client = None
_rag_engine = None


async def initialize_phase_6():
    """Initialize Phase 6 (Local LLM + RAG) services."""
    global _ollama_client, _rag_engine
    
    try:
        logger.info("[PHASE-6] Initializing local LLM integration...")
        
        # Initialize Ollama client
        try:
            from app.services.phase_6_services.ollama_client import get_ollama_client
            _ollama_client = await get_ollama_client()
            
            # Check if Ollama is available
            is_available = await _ollama_client.is_available()
            if is_available:
                logger.info("[PHASE-6] ✓ Ollama service available")
                models = await _ollama_client.list_models()
                logger.info(f"[PHASE-6]   Available models: {models}")
            else:
                logger.warning("[PHASE-6] ⚠ Ollama service not available")
                logger.warning("[PHASE-6]   To use Phase 6, start Ollama service:")
                logger.warning("[PHASE-6]   $ ollama serve")
        except Exception as e:
            logger.warning(f"[PHASE-6] ⚠ Ollama client initialization failed: {e}")
            logger.info("[PHASE-6]   Phase 6 chat endpoints will not work until Ollama is running")
        
        # Initialize RAG engine with vector DB
        try:
            from app.services.vector_knowledge_base import get_vector_knowledge_base
            from app.services.phase_6_services.rag_chat_engine import get_rag_engine
            
            vector_db = get_vector_knowledge_base()
            _rag_engine = await get_rag_engine(vector_db, _ollama_client, top_k=5)
            
            if _rag_engine:
                logger.info("[PHASE-6] ✓ RAG engine initialized")
                stats = _rag_engine.get_statistics()
                logger.info(f"[PHASE-6]   Vector DB: {stats}")
            else:
                logger.warning("[PHASE-6] ⚠ RAG engine initialization incomplete")
        except Exception as e:
            logger.warning(f"[PHASE-6] ⚠ RAG engine initialization failed: {e}")
        
        # Set dependencies in Phase 6 API
        try:
            from app.api.phase_6_api import set_dependencies
            set_dependencies(_ollama_client, _rag_engine)
            logger.info("[PHASE-6] ✓ Dependencies set for Phase 6 API")
        except Exception as e:
            logger.error(f"[PHASE-6] Error setting API dependencies: {e}")
        
        logger.info("[PHASE-6] Phase 6 initialization complete")
        
    except Exception as e:
        logger.error(f"[PHASE-6] Fatal initialization error: {e}")


async def shutdown_phase_6():
    """Cleanup Phase 6 services on shutdown."""
    global _ollama_client, _rag_engine
    
    try:
        if _ollama_client:
            await _ollama_client.close()
            logger.info("[PHASE-6] Ollama client closed")
        
        _ollama_client = None
        _rag_engine = None
        
        logger.info("[PHASE-6] Phase 6 services shut down")
    except Exception as e:
        logger.error(f"[PHASE-6] Error during shutdown: {e}")


def get_ollama_client():
    """Get Ollama client instance."""
    return _ollama_client


def get_rag_engine():
    """Get RAG engine instance."""
    return _rag_engine
