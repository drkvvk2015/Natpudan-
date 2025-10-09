# Natpudan AI Medical Assistant - Backend

Backend API server for the Natpudan AI Medical Assistant application.

## Features

- **PDF Upload & Processing**: Upload medical PDF documents and extract knowledge
- **AI-Powered Symptom Analysis**: Analyze patient symptoms with differential diagnosis
- **Drug Interaction Checking**: Check for potential drug interactions
- **Medical Reference Search**: Search medical information database
- **Treatment Suggestions**: Generate evidence-based treatment suggestions
- **Knowledge Base Management**: Store and retrieve medical knowledge

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Running the Server

Start the development server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
- `GET /health` - Check server health status

### PDF Management
- `POST /api/upload-pdf` - Upload a medical PDF document

### AI Analysis
- `POST /api/analyze-symptoms` - Analyze patient symptoms
- `POST /api/check-interactions` - Check drug interactions
- `POST /api/search-medical-info` - Search medical information
- `POST /api/treatment-suggestions` - Get treatment suggestions
- `POST /api/ask-question` - Ask a general medical question

### Knowledge Base
- `GET /api/knowledge-base/stats` - Get knowledge base statistics
- `GET /api/knowledge-base/documents` - List all documents

## Example Usage

### Upload a PDF
```bash
curl -X POST "http://localhost:8000/api/upload-pdf" \
  -F "file=@medical_document.pdf"
```

### Analyze Symptoms
```bash
curl -X POST "http://localhost:8000/api/analyze-symptoms" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "fever, cough, shortness of breath",
    "age": 45,
    "gender": "male"
  }'
```

### Check Drug Interactions
```bash
curl -X POST "http://localhost:8000/api/check-interactions" \
  -H "Content-Type: application/json" \
  -d '{
    "medications": ["warfarin", "aspirin", "ibuprofen"]
  }'
```

## Development

### Project Structure
```
backend/
├── main.py              # FastAPI application
├── ai_service.py        # AI/LLM integration
├── pdf_utils.py         # PDF text extraction
├── knowledge_base.py    # Knowledge storage
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

### Adding New Features

1. Define your endpoint in `main.py`
2. Add AI functionality in `ai_service.py` if needed
3. Update knowledge base methods in `knowledge_base.py` if needed
4. Test using the interactive API docs

## Security Notes

- Never commit your `.env` file or API keys to version control
- The `.env` file is already in `.gitignore`
- Use environment variables for all sensitive configuration
- In production, use proper authentication and authorization
- Consider rate limiting for API endpoints
- Validate and sanitize all user inputs

## Troubleshooting

### "OPENAI_API_KEY not found" error
Make sure you have created a `.env` file and added your OpenAI API key.

### Import errors
Make sure all dependencies are installed: `pip install -r requirements.txt`

### CORS errors
Update the `ALLOWED_ORIGINS` in your `.env` file to include your frontend URL.

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file in the root directory.
