# 🏥 Physician AI Assistant

An advanced AI-powered clinical assistant designed to support healthcare professionals in their daily practice. The system continuously learns from medical textbooks, assists with history taking, diagnosis, treatment planning, and prescription writing.

## 🌟 Key Features

### 1. **Continuous Learning from Medical Literature**
- Automatically processes and learns from medical PDF textbooks
- Semantic search across entire medical knowledge base
- Real-time knowledge updates as new books are added

### 2. **Intelligent Clinical Support**
- **History Taking**: Structured patient history collection with guided questions
- **Physical Examination**: Step-by-step examination guidance
- **Differential Diagnosis**: AI-powered diagnostic reasoning with ICD-10 codes
- **Treatment Planning**: Evidence-based treatment recommendations
- **Prescription Writing**: Smart prescription generation with safety checks

### 3. **Drug Safety**
- Comprehensive drug interaction checker
- Dosing calculations (age, weight, renal function adjusted)
- Side effect warnings and contraindications
- Alternative medication suggestions

### 4. **Real-time Chat Interface**
- WebSocket-based conversational AI
- Context-aware medical conversations
- Multi-turn dialogue with memory

### 5. **Medical Documentation**
- Automated clinical note generation
- ICD-10 code mapping
- Prescription management
- Patient record keeping

## 🏗️ Architecture

```
physician-ai-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application
│   │   ├── config.py                  # Configuration
│   │   ├── models/                    # Database models
│   │   │   ├── medical_models.py      # Patient, Prescription, etc.
│   │   │   └── chat_models.py         # Chat sessions
│   │   ├── services/                  # Core AI services
│   │   │   ├── knowledge_base.py      # PDF processing & semantic search
│   │   │   ├── llm_service.py         # LLM integration (OpenAI/local)
│   │   │   ├── medical_assistant.py   # Main AI assistant
│   │   │   ├── drug_checker.py        # Drug interactions & dosing
│   │   │   ├── icd_mapper.py          # ICD-10 diagnosis mapping
│   │   │   └── pdf_processor.py       # PDF text extraction
│   │   ├── api/                       # REST API endpoints
│   │   │   ├── chat.py                # Chat endpoints
│   │   │   ├── upload.py              # PDF upload
│   │   │   ├── medical.py             # Medical queries
│   │   │   └── prescription.py        # Prescription management
│   │   └── database/                  # Database setup
│   │       ├── connection.py          # DB connection
│   │       └── schemas.py             # Table creation
│   ├── data/                          # Data storage
│   │   ├── medical_books/             # PDF textbooks (auto-processed)
│   │   ├── knowledge_base/            # Vector database
│   │   └── icd_codes/                 # ICD-10 codes
│   ├── requirements.txt               # Python dependencies
│   ├── run.py                         # Application entry point
│   └── .env                           # Environment variables
├── frontend/                          # React frontend (TODO)
└── setup.ps1                          # Automated setup script
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** installed
- **OpenAI API Key** (optional but recommended for full features)
- **Windows PowerShell** (for automated setup)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/drkvvk2015/Natpudan-.git
   cd "Natpudan-/Natpudan AI project"
   ```

2. **Run the automated setup script**
   ```powershell
   .\setup.ps1
   ```

   This script will:
   - Create virtual environment
   - Install all dependencies
   - Set up database
   - Create data directories
   - Download required NLP models

3. **Configure environment variables**
   ```powershell
   cd backend
   # Edit .env file and add your OpenAI API key
   notepad .env
   ```

   Required configuration in `.env`:
   ```bash
   OPENAI_API_KEY=your-api-key-here
   LLM_MODEL=gpt-4-turbo-preview
   DATABASE_URL=sqlite:///./physician_ai.db
   ```

4. **Add medical textbooks (Optional)**
   ```powershell
   # Place PDF medical books in:
   backend/data/medical_books/
   
   # The system will automatically:
   # - Detect new PDFs
   # - Extract and process content
   # - Add to searchable knowledge base
   ```

5. **Start the backend server**
   ```powershell
   cd backend
   python run.py
   ```

   The API will be available at:
   - **API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

## 📖 Usage

### 1. API Endpoints

#### Health Check
```bash
GET /health
```

#### WebSocket Chat
```javascript
ws://localhost:8000/ws/{user_id}

// Send message
{
  "content": "Patient presenting with chest pain and shortness of breath",
  "type": "diagnosis"
}

// Receive response
{
  "content": "Based on the symptoms...",
  "type": "diagnosis",
  "metadata": {
    "icd_codes": [...],
    "differential_diagnoses": [...]
  }
}
```

#### Upload Medical Book
```bash
POST /api/upload/pdf
Content-Type: multipart/form-data

file: <pdf-file>
```

#### Medical Query
```bash
POST /api/medical/query
{
  "query": "What are the treatment options for Type 2 Diabetes?",
  "patient_context": {...}
}
```

#### Generate Prescription
```bash
POST /api/prescription/generate
{
  "patient_id": "P12345",
  "diagnosis": "Hypertension",
  "medications": [...]
}
```

### 2. Using the Knowledge Base

The system automatically monitors `backend/data/medical_books/` for new PDFs:

```python
from app.services.knowledge_base import KnowledgeBase

# Initialize
kb = KnowledgeBase()
await kb.initialize()

# Search medical knowledge
results = await kb.search("treatment of pneumonia", top_k=5)

# Get condition information
conditions = await kb.search_conditions(
    symptoms=["fever", "cough", "dyspnea"]
)

# Get treatment info
treatment = await kb.get_treatment_info("diabetes")
```

### 3. Using the Medical Assistant

```python
from app.services.medical_assistant import MedicalAssistant

assistant = MedicalAssistant(knowledge_base)
await assistant.initialize()

# Process clinical query
response = await assistant.process_message(
    message="65 year old male with crushing chest pain",
    user_id="doctor123",
    message_type="diagnosis"
)

# Generate differential diagnosis
diagnosis = await assistant._handle_diagnosis(
    message="Patient symptoms...",
    context={...}
)
```

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-key-here
LLM_MODEL=gpt-4-turbo-preview  # or gpt-3.5-turbo
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=800

# Database
DATABASE_URL=sqlite:///./physician_ai.db
# For PostgreSQL: postgresql://user:password@localhost/dbname

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
# Medical alternative: microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Switching to Local LLM (No API Key Required)

To run without OpenAI API key using local models:

1. Install additional dependencies:
   ```bash
   pip install llama-cpp-python transformers torch
   ```

2. Download a local model (e.g., Llama-2 or Mistral)

3. Update config to use `LocalLLMService`

## 📊 Features in Detail

### PDF Knowledge Extraction

The system uses advanced PDF processing to extract and structure medical knowledge:

- **Text Extraction**: PyMuPDF for accurate text extraction
- **Chunking**: Intelligent text chunking with overlap for context preservation
- **Embeddings**: Sentence transformers for semantic understanding
- **Vector Storage**: ChromaDB for fast semantic search
- **Automatic Updates**: Monitors folder for new PDFs

### Drug Interaction Checker

Comprehensive drug safety analysis:

- **Interaction Detection**: Checks all drug pairs for interactions
- **Severity Levels**: High, Medium, Low risk categorization
- **Dosing Calculations**: Age, weight, renal function adjusted
- **Alternative Suggestions**: Recommends safer alternatives
- **Patient-Specific**: Considers allergies, comorbidities

### ICD-10 Mapping

Automatic diagnosis coding:

- **Symptom-to-Code**: Maps clinical presentations to ICD codes
- **Multiple Codes**: Supports comorbidities and complications
- **Confidence Scores**: Indicates mapping certainty
- **Latest Standards**: Uses current ICD-10-CM codes

## 🧪 Testing

Run tests (coming soon):
```bash
pytest tests/
```

## 📈 Performance Optimization

- **Caching**: LLM responses cached for common queries
- **Batch Processing**: PDFs processed in background
- **Async Operations**: Non-blocking I/O throughout
- **Connection Pooling**: Efficient database connections

## ⚠️ Important Medical Disclaimers

**THIS IS A CLINICAL SUPPORT TOOL - NOT A REPLACEMENT FOR MEDICAL JUDGMENT**

- All AI suggestions require validation by licensed healthcare professionals
- Always perform thorough clinical examination and correlation
- Use current medical literature and guidelines
- Consider patient-specific factors not known to the AI
- Maintain appropriate clinical oversight for all decisions
- This tool is for healthcare professional use only

## 🔒 Security & Privacy

- Patient data stored locally in secure database
- No patient data sent to external APIs without explicit configuration
- Encryption recommended for production deployments
- Follow HIPAA/GDPR compliance requirements for clinical use
- Regular security audits recommended

## 🛣️ Roadmap

- [ ] **Frontend Development**: React-based UI with chat interface
- [ ] **Voice Input**: Speech-to-text for hands-free operation
- [ ] **Image Analysis**: X-ray, CT, MRI interpretation
- [ ] **Clinical Guidelines**: Built-in access to major guidelines
- [ ] **Telemedicine Integration**: Video consultation features
- [ ] **Mobile App**: iOS/Android applications
- [ ] **Multi-language**: Support for multiple languages
- [ ] **Offline Mode**: Full functionality without internet

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the GPL v3.0 License - see LICENSE file for details.

## 📞 Support

For questions or issues:
- **GitHub Issues**: [Create an issue](https://github.com/drkvvk2015/Natpudan-/issues)
- **Email**: Contact repository owner

## 🙏 Acknowledgments

- OpenAI for GPT models
- Medical community for knowledge sharing
- Open source contributors

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Status**: Active Development

**Built with ❤️ for healthcare professionals worldwide**
