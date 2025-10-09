# Natpudan AI Medical Assistant - Architecture Documentation

## Overview

Natpudan is a full-stack AI-powered medical assistant application designed to support physicians with clinical decision-making. It combines a responsive web frontend with a Python-based AI backend.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  index.html │  │   script.js   │  │    styles.css    │  │
│  │             │  │               │  │                  │  │
│  │  - UI       │  │  - Logic      │  │  - Styling       │  │
│  │  - Layout   │  │  - API calls  │  │  - Responsive    │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                    HTTP/REST API (CORS enabled)
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                        Backend Layer                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastAPI Application (main.py)            │  │
│  │                                                        │  │
│  │  - RESTful API endpoints                             │  │
│  │  - Request validation (Pydantic)                     │  │
│  │  - CORS middleware                                   │  │
│  └────────┬──────────────┬──────────────┬────────────────┘  │
│           │              │              │                    │
│  ┌────────▼─────┐ ┌─────▼──────┐ ┌────▼──────────┐        │
│  │  ai_service  │ │ pdf_utils  │ │ knowledge_base │        │
│  │              │ │            │ │                │        │
│  │ - Symptom    │ │ - PDF text │ │ - JSON storage │        │
│  │   analysis   │ │   extract  │ │ - Search       │        │
│  │ - Drug check │ │ - Cleaning │ │ - CRUD ops     │        │
│  │ - Med search │ │ - Chunking │ │                │        │
│  └──────┬───────┘ └────────────┘ └────────────────┘        │
└─────────┼─────────────────────────────────────────────────┘
          │
    ┌─────▼──────┐
    │  OpenAI    │
    │  GPT API   │
    └────────────┘
```

## Component Details

### Frontend Components

#### 1. index.html
**Purpose**: Main application structure and UI layout

**Features**:
- Dashboard with feature cards
- Symptom checker form
- Drug interaction checker
- Medical reference search
- Patient notes management
- PDF upload interface

**Key Elements**:
- Responsive grid layout
- Navigation system
- Form inputs with validation
- Results display areas
- Backend status indicator

#### 2. script.js
**Purpose**: Application logic and interactivity

**Key Functions**:
- `analyzeSymptoms()` - Symptom analysis with AI fallback
- `checkInteractions()` - Drug interaction checking
- `searchMedicalInfo()` - Medical information lookup
- `uploadPDF()` - PDF file upload to backend
- `callBackendAPI()` - Generic API communication
- `checkBackendStatus()` - Backend connectivity check

**Data Structures**:
- `medicalKnowledge` - Local medical database for demo mode
- `patientData` - Local patient notes storage

**Features**:
- Hybrid mode (backend + local fallback)
- LocalStorage for patient data
- Error handling and retry logic
- Loading states and animations

#### 3. styles.css
**Purpose**: Visual design and responsive layout

**Key Styles**:
- Gradient header with navigation
- Card-based dashboard
- Form styling
- Alert components
- Loading animations
- Backend status indicator
- Mobile responsive design

**Design System**:
- Color scheme: Purple gradient (#667eea to #764ba2)
- Border radius: 8-15px for modern look
- Box shadows for depth
- Smooth transitions and animations

#### 4. config.js
**Purpose**: Application configuration

**Settings**:
- `API_URL` - Backend server address
- `USE_BACKEND` - Enable/disable AI features
- `API_TIMEOUT` - Request timeout duration

### Backend Components

#### 1. main.py
**Purpose**: FastAPI application and API endpoints

**Endpoints**:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/api/upload-pdf` | Upload medical PDF |
| POST | `/api/analyze-symptoms` | AI symptom analysis |
| POST | `/api/check-interactions` | Drug interaction check |
| POST | `/api/search-medical-info` | Medical information search |
| POST | `/api/treatment-suggestions` | Treatment recommendations |
| POST | `/api/ask-question` | General medical Q&A |
| GET | `/api/knowledge-base/stats` | KB statistics |
| GET | `/api/knowledge-base/documents` | List documents |

**Features**:
- Pydantic models for request validation
- CORS middleware for cross-origin requests
- Error handling with HTTP exceptions
- Async/await for concurrent operations

#### 2. ai_service.py
**Purpose**: AI/LLM integration with OpenAI

**Class**: `AIService`

**Methods**:
- `analyze_symptoms()` - Differential diagnosis using GPT
- `check_drug_interactions()` - Interaction analysis with AI
- `search_medical_information()` - Medical reference lookup
- `generate_treatment_suggestions()` - Treatment planning

**AI Configuration**:
- Model: GPT-3.5-turbo (configurable)
- Temperature: 0.5-0.7 (balanced creativity)
- Max tokens: 800-1000
- System prompts for medical context

**Features**:
- Context injection from knowledge base
- Specialized system prompts per task
- Error handling and retries
- Token management

#### 3. knowledge_base.py
**Purpose**: Medical knowledge storage and retrieval

**Class**: `KnowledgeBase`

**Methods**:
- `add_document()` - Store medical document
- `search_knowledge()` - Search by keywords
- `get_all_documents()` - List all documents
- `get_document_by_id()` - Retrieve specific document
- `delete_document()` - Remove document
- `get_statistics()` - KB metrics

**Storage**:
- Format: JSON file
- Structure: List of documents with metadata
- Search: Keyword matching (can be enhanced with embeddings)

**Features**:
- Persistent storage
- Metadata tracking
- Timestamp management
- Simple search algorithm

#### 4. pdf_utils.py
**Purpose**: PDF processing utilities

**Functions**:
- `extract_text_from_pdf()` - Extract from file path
- `extract_text_from_pdf_bytes()` - Extract from bytes
- `chunk_text()` - Split text with overlap
- `clean_medical_text()` - Normalize text

**Features**:
- PyMuPDF integration
- Text cleaning and normalization
- Chunking for context windows
- Error handling

## Data Flow

### 1. Symptom Analysis Flow

```
User Input (symptoms, age, gender)
    ↓
Frontend (script.js)
    ↓
API Request: POST /api/analyze-symptoms
    ↓
Backend (main.py)
    ↓
Search Knowledge Base (knowledge_base.py)
    ↓
AI Analysis (ai_service.py)
    ↓
OpenAI GPT API
    ↓
AI Response
    ↓
Return JSON Response
    ↓
Frontend Display Results
```

### 2. PDF Upload Flow

```
User Selects PDF File
    ↓
Frontend (script.js)
    ↓
FormData Upload: POST /api/upload-pdf
    ↓
Backend (main.py)
    ↓
Extract Text (pdf_utils.py)
    ↓
Clean Text
    ↓
Store in Knowledge Base (knowledge_base.py)
    ↓
Save to JSON File
    ↓
Return Success Response
    ↓
Frontend Display Confirmation
```

### 3. Medical Search Flow

```
User Search Query
    ↓
Frontend (script.js)
    ↓
API Request: POST /api/search-medical-info
    ↓
Backend (main.py)
    ↓
Search Knowledge Base
    ↓
Get Relevant Context
    ↓
AI Search (ai_service.py)
    ↓
OpenAI GPT API with Context
    ↓
AI Response
    ↓
Return JSON Response
    ↓
Frontend Display Information
```

## Technology Stack

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with Grid and Flexbox
- **JavaScript (ES6+)** - Logic and interactivity
- **Font Awesome** - Icons
- **LocalStorage API** - Patient data storage

### Backend
- **Python 3.8+** - Programming language
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **PyMuPDF (fitz)** - PDF processing
- **OpenAI Python SDK** - AI integration
- **python-dotenv** - Environment management

## Security Considerations

### Current Implementation
- CORS configuration for cross-origin requests
- Environment-based configuration
- Input validation with Pydantic
- Local patient data storage

### Production Requirements
- ✓ HTTPS/TLS encryption
- ✓ User authentication (OAuth2/JWT)
- ✓ API rate limiting
- ✓ Database encryption
- ✓ HIPAA compliance measures
- ✓ Audit logging
- ✓ Role-based access control
- ✓ Secure API key management

## Deployment Considerations

### Frontend Deployment
- Static file hosting (Netlify, Vercel, GitHub Pages)
- CDN for global distribution
- Environment-specific configs

### Backend Deployment
- Cloud platforms (AWS, GCP, Azure)
- Docker containerization
- Load balancing
- Auto-scaling
- Database migration from JSON to PostgreSQL/MongoDB
- Redis caching for knowledge base
- Monitoring and logging

## Scalability

### Current Limitations
- JSON file storage (not suitable for large scale)
- Simple keyword search (no embeddings)
- Single-server deployment
- Synchronous processing

### Scalability Improvements
1. **Database**: PostgreSQL + Vector DB (Pinecone, Weaviate)
2. **Caching**: Redis for frequently accessed data
3. **Search**: Elasticsearch for full-text search
4. **Embeddings**: Add sentence embeddings for semantic search
5. **Queue**: Celery for background processing
6. **CDN**: CloudFront for static assets
7. **Load Balancer**: Nginx for multiple backend instances

## Extension Points

### Add New Features
1. Create new endpoint in `main.py`
2. Add business logic in appropriate module
3. Update frontend with new UI and API call
4. Test with `test_api.py`

### Integrate New AI Models
1. Add new method in `ai_service.py`
2. Configure model parameters
3. Update system prompts
4. Test with various inputs

### Add New Medical Knowledge
1. Upload PDFs through UI
2. Or directly add to `knowledge_base.json`
3. Or expand `medicalKnowledge` in `script.js` for demo

## Testing

### Manual Testing
- Browser testing across Chrome, Firefox, Safari
- API testing with curl or Postman
- Test script: `python backend/test_api.py`

### Automated Testing (Future)
- Unit tests with pytest
- Integration tests for API endpoints
- Frontend tests with Jest
- E2E tests with Playwright

## Monitoring and Logging

### Current
- Console logging in frontend
- Print statements in backend
- Basic error messages

### Production (Recommended)
- Application Performance Monitoring (APM)
- Structured logging (JSON format)
- Error tracking (Sentry)
- Usage analytics
- Health checks and alerts

## Contributing

To contribute:
1. Understand the architecture
2. Follow existing patterns
3. Test thoroughly
4. Document changes
5. Submit pull request

## License

GPL-3.0 - See LICENSE file
