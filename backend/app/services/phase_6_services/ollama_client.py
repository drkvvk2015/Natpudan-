"""
Phase 6 - Ollama Local LLM Integration

Provides interface to Ollama for local LLaMA inference.
Supports both streaming and non-streaming responses.
"""

import httpx
import logging
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Ollama defaults
import os
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = "llama2"  # Default, can switch to llama2-medical, etc.
OLLAMA_TIMEOUT = 300  # 5 minutes for long responses


class OllamaClient:
    """Client for local Ollama LLM inference."""
    
    def __init__(self, host: str = OLLAMA_HOST, model: str = OLLAMA_MODEL):
        """Initialize Ollama client."""
        self.host = host
        self.model = model
        self.client = None
        self._available_models = []
    
    async def initialize(self):
        """Initialize async HTTP client."""
        self.client = httpx.AsyncClient(timeout=OLLAMA_TIMEOUT)
        logger.info(f"✓ Ollama client initialized (host: {self.host}, model: {self.model})")
    
    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
    
    async def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            if not self.client:
                await self.initialize()
            response = await self.client.get(f"{self.host}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama unavailable: {e}")
            return False
    
    async def list_models(self) -> List[str]:
        """List available models on Ollama."""
        try:
            if not self.client:
                await self.initialize()
            response = await self.client.get(f"{self.host}/api/tags")
            data = response.json()
            models = [m.get("name", "unknown") for m in data.get("models", [])]
            self._available_models = models
            logger.info(f"✓ Available models: {models}")
            return models
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """
        Download and install a model from Ollama registry.
        
        Args:
            model_name: Model name (e.g., "llama2", "neural-chat")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.client:
                await self.initialize()
            
            logger.info(f"Downloading model {model_name}...")
            response = await self.client.post(
                f"{self.host}/api/pull",
                json={"name": model_name}
            )
            
            if response.status_code == 200:
                logger.info(f"✓ Successfully pulled model: {model_name}")
                self.model = model_name
                return True
            else:
                logger.error(f"Failed to pull model: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Generate response from local LLM (non-streaming).
        
        Args:
            prompt: User prompt
            context: Optional context (e.g., from RAG)
            max_tokens: Maximum tokens in response
            temperature: Response temperature (0.0-2.0)
            top_p: Top-p sampling
            
        Returns:
            Generated text
        """
        try:
            if not self.client:
                await self.initialize()
            
            # Build full prompt with context if provided
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
            
            logger.info(f"Generating response from {self.model}...")
            
            response = await self.client.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("response", "")
                logger.debug(f"Generated {len(result)} chars")
                return result
            else:
                logger.error(f"LLM error: {response.text}")
                return ""
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""
    
    async def generate_stream(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response from local LLM.
        
        Args:
            prompt: User prompt
            context: Optional context (e.g., from RAG)
            max_tokens: Maximum tokens in response
            temperature: Response temperature
            top_p: Top-p sampling
            
        Yields:
            Response tokens one at a time
        """
        try:
            if not self.client:
                await self.initialize()
            
            # Build full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
            
            logger.info(f"Streaming response from {self.model}...")
            
            async with self.client.stream(
                "POST",
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": True,
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            token = data.get("response", "")
                            if token:
                                yield token
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            yield f"\n[Error: {str(e)}]"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Multi-turn chat with local LLM.
        
        Args:
            messages: List of {"role": "user"/"assistant", "content": "..."} dicts
            max_tokens: Maximum tokens
            temperature: Response temperature
            
        Returns:
            Assistant response
        """
        try:
            if not self.client:
                await self.initialize()
            
            # Convert messages to prompt format
            prompt = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    prompt += f"User: {content}\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n"
            
            prompt += "Assistant: "
            
            logger.info("Processing multi-turn chat...")
            
            response = await self.client.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                logger.error(f"Chat error: {response.text}")
                return ""
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return ""
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        try:
            if not self.client:
                await self.initialize()
            
            response = await self.client.post(
                f"{self.host}/api/show",
                json={"name": self.model}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Model not found"}
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {"error": str(e)}
    
    def switch_model(self, model_name: str):
        """Switch to a different model."""
        self.model = model_name
        logger.info(f"✓ Switched to model: {model_name}")


# Singleton instance
_ollama_client: Optional[OllamaClient] = None


async def get_ollama_client(
    host: str = OLLAMA_HOST,
    model: str = OLLAMA_MODEL
) -> OllamaClient:
    """Get or create global Ollama client."""
    global _ollama_client
    
    if _ollama_client is None:
        _ollama_client = OllamaClient(host, model)
        await _ollama_client.initialize()
    
    return _ollama_client


async def close_ollama_client():
    """Close global Ollama client."""
    global _ollama_client
    if _ollama_client:
        await _ollama_client.close()
        _ollama_client = None
