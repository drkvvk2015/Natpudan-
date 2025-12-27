# Medical AI Chat - Quick Start Guide

## Overview

The Natpudan Medical AI Chat is a fully-featured medical conversation interface with evidence-based knowledge synthesis, drug interaction checking, and ICD-10 code lookup.

## ✨ Features

- **Medical Chat Assistant**: Evidence-based responses synthesized from knowledge base with clickable citations
- **Drug Interaction Checker**: Check interactions between multiple medications with severity levels
- **ICD-10 Code Search**: Quickly find relevant diagnostic codes
- **Streaming Responses**: Real-time response streaming with SSE
- **Knowledge Base Integration**: Automatic context retrieval and source citations
- **Role-Based Access**: Staff, Doctor, and Admin roles with progressive access
- **Conversation History**: Full chat history with message persistence

## 🚀 Getting Started

### 1. Configure Environment

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and set:
```
OPENAI_API_KEY=sk-proj-your-actual-key-here
DATABASE_URL=sqlite:///./natpudan.db
SECRET_KEY=your-random-secret-key
```

Get your OpenAI key: https://platform.openai.com/api-keys

### 2. Validate Environment

```bash
cd backend
python validate_env.py
```

Expected output:
```
✅ ENVIRONMENT READY FOR DEVELOPMENT
```

### 3. Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Expected output:
```
[INFO] [STARTED] Application started
[INFO] [OK] Database initialized
[INFO] [OK] OpenAI API configured
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 5. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will start on: http://localhost:5173

## 🧪 Testing

### Run Smoke Tests

```bash
cd backend
python test_chat_smoke.py
```

This tests:
- ✅ Backend health
- ✅ User registration & login
- ✅ Chat message sending
- ✅ Drug interaction checking
- ✅ ICD-10 code search
- ✅ Knowledge base integration

### Manual Testing

1. **Open application**: http://localhost:5173
2. **Register**: Email: test@example.com, Password: Test123!
3. **Navigate to Chat**: Click "Chat" in sidebar
4. **Try quick-start prompts**:
   - "Define fever"
   - "Treatment for pneumonia"
   - Use "Check Drug Interaction" button for warfarin + aspirin
   - Use "Search ICD-10 Codes" for common diagnoses

## 📊 API Endpoints

### Chat API

**Send Message**
```bash
POST /api/chat/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Define fever",
  "conversation_id": 1  # optional, creates new if omitted
}

Response:
{
  "message": {
    "role": "assistant",
    "content": "# Fever\n\n...",
    "created_at": "2025-12-27T..."
  },
  "conversation_id": 1
}
```

**Get Conversations**
```bash
GET /api/chat/history
Authorization: Bearer <token>

Response:
[
  {
    "id": 1,
    "title": "Define fever",
    "created_at": "2025-12-27T...",
    "updated_at": "2025-12-27T...",
    "message_count": 2
  }
]
```

**Get Conversation Details**
```bash
GET /api/chat/history/{conversation_id}
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "title": "Define fever",
  "messages": [
    {
      "role": "user",
      "content": "Define fever",
      "created_at": "2025-12-27T..."
    },
    {
      "role": "assistant",
      "content": "# Fever\n\n...",
      "created_at": "2025-12-27T..."
    }
  ]
}
```

### Medical Helper APIs

**Check Drug Interactions**
```bash
POST /api/prescription/check-interactions
Authorization: Bearer <token>

{
  "medications": ["warfarin", "aspirin"]
}

Response:
{
  "total_interactions": 1,
  "high_risk_warning": false,
  "interactions": [
    {
      "drug1": "warfarin",
      "drug2": "aspirin",
      "severity": "moderate",
      "description": "..."
    }
  ]
}
```

**Search ICD-10 Codes**
```bash
GET /api/medical/icd/search?query=diabetes&max_results=5

Response:
[
  {
    "code": "E10",
    "description": "Type 1 diabetes mellitus"
  },
  ...
]
```

## 🏗️ Architecture

### Backend

```
backend/
├── app/
│   ├── main.py              # FastAPI app, routers
│   ├── api/
│   │   ├── chat_new.py      # Chat endpoints with KB synthesis
│   │   ├── chat_streaming.py # Streaming endpoint (SSE)
│   │   └── auth_new.py      # Authentication
│   ├── services/
│   │   ├── vector_knowledge_base.py  # FAISS + embeddings
│   │   ├── drug_interactions.py      # Drug checker
│   │   ├── icd10_service.py          # ICD-10 lookup
│   │   └── enhanced_knowledge_base.py # Advanced KB
│   ├── models.py            # SQLAlchemy ORM
│   ├── database.py          # Session management
│   └── utils/
│       └── ai_service.py    # OpenAI integration
├── .env                     # Configuration (create from .env.example)
└── requirements.txt         # Python dependencies
```

### Frontend

```
frontend/
├── src/
│   ├── pages/
│   │   └── ChatPage.tsx     # Chat page layout
│   ├── components/
│   │   ├── ChatWindow.tsx   # Chat UI with drug/ICD helpers
│   │   └── ChatHistory.tsx  # Conversation list
│   ├── services/
│   │   └── api.ts           # API client
│   └── context/
│       └── AuthContext.tsx  # Auth state
├── package.json             # Dependencies (includes react-markdown)
└── .env.local               # Configuration (create from .env.example)
```

## 🔑 Key Features Implementation

### 1. Medical AI Synthesis

The chat endpoint automatically:
1. Receives user query
2. Searches knowledge base for relevant content (top 5 results)
3. Constructs medical prompt with retrieved context
4. Calls OpenAI for synthesis
5. Returns response with markdown-formatted citations

**Backend Code**: `backend/app/api/chat_new.py` lines ~113-180

### 2. Drug Interaction Checking

**UI**: Quick-action button in `ChatWindow.tsx`
**Backend**: `POST /api/prescription/check-interactions`
**Service**: `backend/app/services/drug_interactions.py`

Checks for interaction severity: HIGH, MODERATE, LOW

### 3. ICD-10 Code Search

**UI**: Quick-action button in `ChatWindow.tsx`
**Backend**: `GET /api/medical/icd/search`
**Service**: `backend/app/services/icd10_service.py`

Searches local ICD-10 database for diagnostic codes

### 4. Markdown Rendering

**Frontend**: `ChatWindow.tsx` uses `react-markdown` with `remark-gfm`
**Features**: Headers, lists, links, tables in responses
**Backend**: Responses include markdown formatting with inline citations

### 5. Streaming (Optional)

**Endpoint**: `POST /api/chat/message/stream`
**Format**: Server-Sent Events (SSE)
**Client**: Can be wired in `ChatWindow.tsx` for real-time updates

## ⚙️ Configuration Options

### Backend Environment Variables

```
# Required
OPENAI_API_KEY=sk-proj-...        # OpenAI API key
SECRET_KEY=your-secret-key        # JWT secret
DATABASE_URL=sqlite:///natpudan.db # Database

# Optional - Medical AI
OPENAI_MODEL=gpt-4o               # LLM model
MEDICAL_AI_TEMPERATURE=0.7        # Response variety
MEDICAL_AI_MAX_TOKENS=2000        # Response length

# Optional - Knowledge Base
ENABLE_KNOWLEDGE_BASE=true        # KB feature
KB_CACHE_DIR=backend/cache/...    # KB cache location
VECTOR_SEARCH_TOP_K=5             # KB results per query

# Optional - Features
REDIS_URL=                        # Background jobs
SENTRY_DSN=                       # Error tracking
LOG_LEVEL=INFO                    # Logging level
```

### Frontend Environment Variables

```
VITE_API_BASE_URL=http://127.0.0.1:8000  # Backend URL
VITE_ENABLE_CHAT_STREAMING=true          # Streaming
VITE_ENABLE_DRUG_CHECKER=true            # Drug helper
VITE_ENABLE_DIAGNOSIS=true               # Diagnosis helper
```

## 📝 Common Workflows

### Workflow 1: New Medical Question

1. User enters question in chat: "What causes chest pain?"
2. Backend searches knowledge base → finds 5 relevant articles
3. Backend calls OpenAI with consolidated prompt
4. OpenAI synthesizes response with citations
5. Frontend renders markdown with links to full articles
6. User can click source links to read full content

### Workflow 2: Drug Safety Check

1. User clicks "Check Drug Interaction"
2. Dialog opens → user enters 2+ drugs
3. Backend checks interaction database
4. Results added to chat as system message
5. User can follow up with questions about interactions

### Workflow 3: Diagnosis Lookup

1. User clicks "Search ICD-10 Codes"
2. Dialog opens → user enters symptom/diagnosis
3. Backend searches ICD-10 database
4. Top 5 matching codes added to chat
5. User can use codes in treatment plans

## 🐛 Troubleshooting

### "OpenAI API key not configured"

**Fix**: Add to `backend/.env`:
```
OPENAI_API_KEY=sk-proj-your-actual-key
```

Get key: https://platform.openai.com/api-keys

### "Backend connection refused"

**Fix**: Ensure backend is running:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### "Knowledge base not available"

**Fix**: Load knowledge base files to `backend/data/knowledge_base/`
Then restart backend.

### "Drug interaction check returns 500 error"

**Fix**: Check backend logs for `DrugInteractionChecker` initialization.
May need to install additional dependencies.

### "Chat markdown not rendering"

**Fix**: Ensure frontend dependencies installed:
```bash
cd frontend
npm install react-markdown remark-gfm
```

## 📚 Further Reading

- **Backend Architecture**: See `CURRENT_STATUS.md`
- **Knowledge Base**: See `KB_OPTIMIZATION_QUICK_REFERENCE.md`
- **API Documentation**: http://localhost:8000/docs (auto-generated)
- **OpenAI Integration**: `backend/app/utils/ai_service.py`

## 🚀 Production Deployment

### Pre-Production Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Update `SECRET_KEY` to random 32+ char string
- [ ] Switch `DATABASE_URL` to PostgreSQL
- [ ] Configure `CORS_ORIGINS` to your domain
- [ ] Enable `SENTRY_DSN` for error tracking
- [ ] Test all endpoints with `test_chat_smoke.py`
- [ ] Set `LOG_LEVEL=WARNING` to reduce logs

### Deployment Options

1. **Docker**: Use provided `docker-compose.yml`
2. **Azure**: Deploy with provided Azure setup scripts
3. **Traditional**: Run with Gunicorn + Nginx
4. **Serverless**: Deploy to AWS Lambda / Azure Functions

See `HOW_TO_RUN_FULL_APP.md` for detailed deployment guides.

## 📞 Support

For issues or questions:
1. Check logs: `backend/logs/app.log`
2. Run smoke tests: `python test_chat_smoke.py`
3. Validate environment: `python validate_env.py`
4. Check API docs: http://localhost:8000/docs

---

**Happy diagnosing! 🏥**
