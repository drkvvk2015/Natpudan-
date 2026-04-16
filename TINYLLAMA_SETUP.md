# TINYLLAMA SETUP GUIDE

This guide explains how to use TinyLLama as an embedded AI model in the Natpudan medical assistant, with fallback to Ollama or OpenAI.

## Benefits of TinyLLama

✅ **Fully Local** - No internet required, runs on your machine  
✅ **Lightweight** - 1.1GB model size, ~2GB RAM usage  
✅ **Fast** - CPU-compatible, instant responses on modern hardware  
✅ **Private** - Medical data never leaves your computer  
✅ **Free** - No API costs, no rate limits  
✅ **Production Ready** - Medical-grade inference with llama-cpp-python  

## Setup Instructions

### 1. Install llama-cpp-python

```bash
cd backend
pip install llama-cpp-python==0.2.94
```

**Optional GPU Support:**
```bash
# For NVIDIA GPU acceleration (if you have CUDA 12.x installed)
pip install llama-cpp-python[cuda]

# For AMD GPU (ROCm)
pip install llama-cpp-python[rocm]

# For Apple Metal GPU
pip install llama-cpp-python[metal]
```

### 2. Download TinyLLama Model

TinyLLama is only ~1.1GB. Choose your preferred option:

**Option A: Automated Download (Easiest)**
```bash
# Create models directory
mkdir -p models
cd models

# Download TinyLLama via Ollama (will convert to GGUF)
ollama pull tinyllama
ollama show tinyllama --modelfile  # Get model path

# Or download directly from HuggingFace
python -c "
from huggingface_hub import hf_hub_download
model = hf_hub_download(
    repo_id='TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF',
    filename='tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf'
)
print(f'Downloaded to: {model}')
"
cd ..
```

**Option B: Manual Download**
- Visit: https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF
- Download `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` (~750MB)
- Place in `backend/models/` directory

### 3. Configure Backend `.env`

Edit `backend/.env` and add:

```ini
# AI Provider Configuration
AI_PROVIDER=auto

# Embedded Model Configuration (TinyLLama)
EMBEDDED_MODEL_PATH=models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
MODEL_GPU_LAYERS=0  # Increase to use GPU offloading (e.g., 20 for RTX, 10 for AMD)

# Ollama Configuration (fallback)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# OpenAI Configuration (final fallback)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
```

**Configuration Options:**
- `AI_PROVIDER`: How to select AI
  - `"embedded"` - Use TinyLLama only
  - `"ollama"` - Use Ollama only
  - `"openai"` - Use OpenAI only
  - `"auto"` - Try embedded first, then Ollama, then OpenAI (recommended)

- `MODEL_GPU_LAYERS`: GPU acceleration levels
  - `0` - CPU only (default, slowest but most compatible)
  - `10-20` - Partial GPU offload (fast, good balance)
  - `33` - Full GPU offload (fastest, requires good GPU)

### 4. Verify Installation

Start the backend and check AI provider status:

```bash
cd backend
python -m uvicorn app.main:app --reload

# In another terminal, check status
curl http://localhost:8000/health/ai-provider
```

Response example:
```json
{
  "status": "healthy",
  "ai_service": {
    "configured_provider": "auto",
    "embedded": {
      "available": true,
      "path": "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
      "gpu_layers": 0
    },
    "ollama": {
      "available": false,
      "url": "http://localhost:11434"
    },
    "openai": {
      "available": false,
      "model": "gpt-4o"
    }
  }
}
```

## Usage

### Example 1: Chat with TinyLLama

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are symptoms of diabetes?"}'
```

The response will show which provider was used:
```json
{
  "response": "...",
  "provider": "embedded",
  "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
}
```

### Example 2: Switch Providers (Dev Testing)

```bash
# Temporarily switch providers via environment
export AI_PROVIDER=openai  # Use OpenAI for this session
python -m uvicorn app.main:app --reload

# Or modify .env and restart backend
```

## Performance Benchmarks

### TinyLLama (Embedded - CPU)
- Model size: 1.1B parameters
- Memory: ~2GB RAM
- Speed: 50-100 tokens/second (CPU)
- Latency: 200-500ms for typical queries
- Quality: Good for medical summaries, acceptable for diagnosis

### Mistral (Ollama)
- Model size: 7B parameters
- Memory: ~5GB RAM
- Speed: 20-50 tokens/second (CPU), 100+ (GPU)
- Latency: 500ms-2s
- Quality: Better accuracy, better for detailed analysis

### GPT-4 (OpenAI)
- Model size: Cloud
- Memory: None
- Speed: 50-200 tokens/second (network dependent)
- Latency: 500ms-5s (API + network)
- Quality: Best, most accurate medical information

## Troubleshooting

### Issue: "Embedded model not found"
**Solution:**
```bash
# Check model exists
ls -la backend/models/tinyllama*.gguf

# If missing, download it
python -c "
from huggingface_hub import hf_hub_download
model = hf_hub_download(
    repo_id='TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF',
    filename='tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf'
)
"
```

### Issue: "Permission denied" when loading model
**Solution:**
```bash
# Make model readable
chmod 644 backend/models/tinyllama*.gguf
```

### Issue: Slow response times (>5 seconds)
**Solutions:**
1. Use GPU acceleration: set `MODEL_GPU_LAYERS=10+` and install CUDA/ROCm
2. Switch to Ollama with same model for better optimization
3. Use OpenAI for critical medical responses
4. Reduce max_tokens in requests

### Issue: "CUDA out of memory" with GPU
**Solution:**
```ini
# Reduce GPU layers or use smaller quantization
MODEL_GPU_LAYERS=10  # Start low, increase gradually
```

## Switching AI Providers

### At Runtime (Development)

```python
import os
os.environ["AI_PROVIDER"] = "ollama"  # Switch provider
from app.utils.hybrid_ai_service import get_hybrid_ai
service = get_hybrid_ai()
```

### In a Specific Request

```python
from app.utils.hybrid_ai_service import HybridAIService

# Create service with specific provider
service = HybridAIService()
response = await service.generate_response(
    messages=[{"role": "user", "content": "..."}],
    system_prompt="Medical assistant"
)
```

## Production Deployment

### Docker with TinyLLama

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .

RUN pip install -r requirements.txt

# Download model at build time
RUN python -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF',
    filename='tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
    cache_dir='/app/models'
)
"

COPY backend/ .
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Resource Requirements

**Minimum:**
- CPU: Dual-core @ 2GHz
- RAM: 4GB (2-3GB for model, 1GB for app)
- Disk: 3GB (for model + dependencies)

**Recommended:**
- CPU: Quad-core @ 3GHz
- RAM: 8GB
- Disk: 10GB SSD
- GPU: Optional (NVIDIA RTX 3060 or better for 8+ tokens/sec)

## When to Use Which Provider

| Provider | Use Case |
|----------|----------|
| **TinyLLama** | Development, demos, privacy-required deployments, resource-constrained |
| **Ollama** | Local production, better accuracy needed, can install larger models |
| **OpenAI** | Critical medical decisions, highest accuracy, requiring enterprise SLA |

## Additional Resources

- TinyLLama Model: https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0
- GGUF Quantizations: https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF
- llama-cpp-python: https://github.com/abetlen/llama-cpp-python
- Ollama: https://ollama.ai

## Questions?

Check the main README.md for overall project setup and troubleshooting guides.
