"""Hybrid AI service supporting OpenAI, local Ollama, and embedded TinyLLama models for medical AI tasks."""

import os
import logging
from typing import List, Dict, Literal, Optional
from enum import Enum
import httpx

from openai import OpenAI, APITimeoutError, RateLimitError, APIError
from dotenv import load_dotenv

# Optional: llama-cpp-python for embedded models
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    Llama = None

logger = logging.getLogger(__name__)

# Load environment variables from backend/.env file
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)


class AIProvider(str, Enum):
    """Available AI providers"""
    OPENAI = "openai"
    OLLAMA = "ollama"
    EMBEDDED = "embedded"  # TinyLLama or other GGUF models
    AUTO = "auto"  # Try embedded/ollama first, fallback to OpenAI


class HybridAIService:
    """
    Hybrid AI service that switches between OpenAI, local Ollama, and embedded TinyLLama.
    
    Configuration via environment variables:
    - AI_PROVIDER: "openai", "ollama", "embedded", or "auto" (default: "auto")
    - EMBEDDED_MODEL_PATH: Path to GGUF model (e.g., "models/tinyllama.gguf")
    - OLLAMA_BASE_URL: Ollama server URL (default: "http://localhost:11434")
    - OLLAMA_MODEL: Local model to use (default: "mistral")
    - OPENAI_API_KEY: OpenAI API key (required for OpenAI fallback)
    - OPENAI_MODEL: OpenAI model (default: "gpt-4o")
    - MODEL_GPU_LAYERS: Layers to offload to GPU for TinyLLama (default: 0 for CPU only)
    """
    
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "auto").lower()
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        
        # Embedded model configuration
        self.embedded_model_path = os.getenv("EMBEDDED_MODEL_PATH", None)
        self.model_gpu_layers = int(os.getenv("MODEL_GPU_LAYERS", "0"))
        self.embedded_model = None
        self.embedded_available = False
        
        # Initialize embedded model if configured
        if self.embedded_model_path:
            self._load_embedded_model()
        
        # Initialize OpenAI client
        self.openai_client = None
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and not api_key.startswith("sk-your"):
            try:
                self.openai_client = OpenAI(api_key=api_key, timeout=30.0, max_retries=2)
                logger.info("[OK] OpenAI client initialized")
            except Exception as e:
                logger.warning(f"[WARNING] OpenAI client failed: {e}")
        
        # Check Ollama availability
        self.ollama_available = self._check_ollama_health()
        
        logger.info(f"[OK] HybridAI initialized - Provider: {self.provider}, "
                   f"Embedded: {self.embedded_available}, Ollama: {self.ollama_available}, OpenAI: {self.openai_client is not None}")
    
    def _load_embedded_model(self):
        """Load embedded TinyLLama or GGUF model"""
        if not LLAMA_CPP_AVAILABLE:
            logger.warning("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            return
        
        if not os.path.exists(self.embedded_model_path):
            logger.warning(f"Embedded model not found at {self.embedded_model_path}")
            return
        
        try:
            logger.info(f"Loading embedded model: {self.embedded_model_path}")
            self.embedded_model = Llama(
                model_path=self.embedded_model_path,
                n_gpu_layers=self.model_gpu_layers,
                n_ctx=4096,
                n_threads=os.cpu_count() or 4,
                verbose=False,
            )
            self.embedded_available = True
            logger.info("[OK] Embedded model loaded successfully")
        except Exception as e:
            logger.error(f"[ERROR] Failed to load embedded model: {e}")
            self.embedded_available = False
    
    def _check_ollama_health(self) -> bool:
        """Check if Ollama server is running and accessible"""
        try:
            response = httpx.get(f"{self.ollama_base_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama health check failed: {e}")
            return False
    
    def _get_active_provider(self) -> Literal["openai", "ollama", "embedded"]:
        """Determine which provider to use based on configuration and availability"""
        if self.provider == "embedded":
            if not self.embedded_available:
                logger.warning("Embedded model requested but not available, falling back")
            else:
                return "embedded"
        
        if self.provider == "ollama":
            if not self.ollama_available:
                logger.warning("Ollama requested but not available, falling back")
            else:
                return "ollama"
        
        if self.provider == "openai":
            if not self.openai_client:
                raise Exception("OpenAI requested but not configured")
            return "openai"
        
        # Auto mode: try embedded first, then Ollama, then OpenAI
        if self.embedded_available:
            return "embedded"
        elif self.ollama_available:
            logger.debug("Embedded unavailable, using Ollama")
            return "ollama"
        elif self.openai_client:
            logger.warning("Embedded and Ollama unavailable, using OpenAI fallback")
            return "openai"
        else:
            raise Exception("No AI provider available")
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "You are a helpful medical AI assistant. Provide accurate, professional medical information.",
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> Dict:
        """
        Generate AI response using available provider.
        
        Args:
            messages: List of conversation messages with role and content
            system_prompt: System prompt to set AI behavior
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0-2)
            
        Returns:
            Dict with keys: 'content', 'provider', 'model'
        """
        provider = self._get_active_provider()
        
        try:
            if provider == "embedded":
                return self._embedded_request(messages, system_prompt, max_tokens, temperature)
            elif provider == "ollama":
                return await self._ollama_request(messages, system_prompt, max_tokens, temperature)
            else:
                return self._openai_request(messages, system_prompt, max_tokens, temperature)
        except Exception as e:
            logger.error(f"Error with {provider}: {e}")
            
            # Fallback logic: try next provider
            fallback_order = {
                "embedded": ["ollama", "openai"],
                "ollama": ["openai"],
                "openai": []
            }
            
            for fallback in fallback_order.get(provider, []):
                logger.info(f"{provider} failed, attempting {fallback} fallback")
                try:
                    if fallback == "embedded" and self.embedded_available:
                        return self._embedded_request(messages, system_prompt, max_tokens, temperature)
                    elif fallback == "ollama" and self.ollama_available:
                        return await self._ollama_request(messages, system_prompt, max_tokens, temperature)
                    elif fallback == "openai" and self.openai_client:
                        return self._openai_request(messages, system_prompt, max_tokens, temperature)
                except Exception as fallback_error:
                    logger.warning(f"{fallback} fallback also failed: {fallback_error}")
                    continue
            
            raise Exception(f"All providers failed. Last error: {e}")
    
    def _embedded_request(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Dict:
        """Make request to embedded model (TinyLLama/Gemma/Qwen via llama-cpp-python)"""
        if not self.embedded_model:
            raise Exception("Embedded model not loaded")

        model_name = os.path.basename(self.embedded_model_path).lower()

        # Format prompt based on model type
        if "gemma" in model_name:
            # Gemma chat format
            prompt = f"<start_of_turn>user\n{system_prompt}\n\n"
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    prompt += f"{content}\n"
                elif role == "assistant":
                    prompt += f"<end_of_turn>\n<start_of_turn>model\n{content}<end_of_turn>\n<start_of_turn>user\n"
            prompt += "<end_of_turn>\n<start_of_turn>model\n"
            stop_tokens = ["<end_of_turn>", "<start_of_turn>"]
        elif "qwen" in model_name:
            # Qwen chat format
            prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
            prompt += "<|im_start|>assistant\n"
            stop_tokens = ["<|im_end|>", "<|im_start|>"]
        else:
            # TinyLLama / generic chat format
            prompt = system_prompt + "\n\n"
            for msg in messages:
                role = msg.get("role", "user").upper()
                content = msg.get("content", "")
                prompt += f"{role}: {content}\n"
            prompt += "ASSISTANT:"
            stop_tokens = ["USER:", "DOCTOR:", "PATIENT:"]

        try:
            logger.debug(f"Calling embedded model with prompt ({len(prompt)} chars)")

            response = self.embedded_model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
                stop=stop_tokens
            )

            content = response["choices"][0]["text"].strip()
            logger.debug(f"Embedded model response received ({len(content)} chars)")

            return {
                "content": content,
                "provider": "embedded",
                "model": os.path.basename(self.embedded_model_path),
            }

        except Exception as e:
            logger.error(f"Embedded model error: {e}")
            raise Exception(f"Embedded model error: {str(e)[:200]}")
    
    async def _ollama_request(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Dict:
        """Make request to local Ollama server"""
        # Prepare messages with system prompt
        formatted_messages = [{"role": "system", "content": system_prompt}]
        formatted_messages.extend(messages)
        
        payload = {
            "model": self.ollama_model,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                logger.debug(f"Calling Ollama {self.ollama_model} with {len(messages)} messages")
                response = await client.post(
                    f"{self.ollama_base_url}/api/chat",
                    json=payload
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"Ollama error {response.status_code}: {error_text}")
                    raise Exception(f"Ollama API error: {error_text[:200]}")
                
                data = response.json()
                content = data.get("message", {}).get("content", "")
                
                logger.debug(f"Ollama response received ({len(content)} chars)")
                return {
                    "content": content,
                    "provider": "ollama",
                    "model": self.ollama_model,
                }
        
        except httpx.TimeoutException:
            logger.error("Ollama timeout after 60s")
            raise Exception("Ollama timeout (60s). Please try with a shorter query.")
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            raise
    
    def _openai_request(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Dict:
        """Make request to OpenAI API"""
        if not self.openai_client:
            raise Exception("OpenAI API not configured. Please set OPENAI_API_KEY in backend/.env")
        
        try:
            # Prepare messages with system prompt
            formatted_messages = [{"role": "system", "content": system_prompt}]
            formatted_messages.extend(messages)
            
            logger.debug(f"Calling OpenAI {self.openai_model} with {len(messages)} messages")
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            content = response.choices[0].message.content
            logger.debug(f"OpenAI response received ({len(content)} chars)")
            
            return {
                "content": content,
                "provider": "openai",
                "model": self.openai_model,
            }
        
        except APITimeoutError as e:
            logger.error(f"OpenAI timeout: {e}")
            raise Exception("OpenAI timeout (30s). Please try with a shorter query.")
        
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit: {e}")
            raise Exception("OpenAI rate limit exceeded. Please wait and try again.")
        
        except APIError as api_error:
            error_msg = str(api_error)
            logger.error(f"OpenAI API Error: {error_msg}")
            
            if "api_key" in error_msg.lower() or "401" in error_msg:
                raise Exception("OpenAI API key invalid")
            elif "quota" in error_msg.lower():
                raise Exception("OpenAI quota exceeded")
            elif "model" in error_msg.lower():
                raise Exception(f"Model '{self.openai_model}' not available")
            else:
                raise Exception(f"OpenAI API error: {error_msg[:150]}")
        
        except Exception as e:
            logger.error(f"Unexpected OpenAI error: {e}", exc_info=True)
            raise
    
    async def get_status(self) -> Dict:
        """Get status of available AI providers"""
        return {
            "configured_provider": self.provider,
            "embedded": {
                "available": self.embedded_available,
                "path": self.embedded_model_path or "not_configured",
                "gpu_layers": self.model_gpu_layers,
            },
            "ollama": {
                "available": self.ollama_available,
                "url": self.ollama_base_url,
                "model": self.ollama_model,
            },
            "openai": {
                "available": self.openai_client is not None,
                "model": self.openai_model,
            },
        }


# Global instance
_hybrid_ai_instance: HybridAIService = None


def get_hybrid_ai() -> HybridAIService:
    """Get or create the global HybridAIService instance"""
    global _hybrid_ai_instance
    if _hybrid_ai_instance is None:
        _hybrid_ai_instance = HybridAIService()
    return _hybrid_ai_instance


# Backwards compatibility: keep original function name
async def generate_ai_response(
    messages: List[Dict[str, str]],
    system_prompt: str = "You are a helpful medical AI assistant. Provide accurate, professional medical information.",
    max_tokens: int = 2000,
    temperature: float = 0.7,
) -> str:
    """
    Generate AI response using hybrid service (backwards compatible with original API).
    
    Returns only the content string for backwards compatibility.
    """
    service = get_hybrid_ai()
    result = await service.generate_response(messages, system_prompt, max_tokens, temperature)
    return result["content"]
