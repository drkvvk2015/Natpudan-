# PowerShell script to create Physician AI Assistant project structure

Write-Host "Creating Physician AI Assistant Project Structure..." -ForegroundColor Green

# Create directory structure
$directories = @(
    "backend/app/models",
    "backend/app/services",
    "backend/app/api",
    "backend/app/database",
    "data/medical_books",
    "data/knowledge_base",
    "data/icd_codes"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Write-Host "Created directory: $dir" -ForegroundColor Cyan
}

# Create __init__.py files for Python packages
$initFiles = @(
    "backend/app/__init__.py",
    "backend/app/models/__init__.py",
    "backend/app/services/__init__.py",
    "backend/app/api/__init__.py",
    "backend/app/database/__init__.py"
)

foreach ($file in $initFiles) {
    New-Item -ItemType File -Force -Path $file | Out-Null
    Write-Host "Created: $file" -ForegroundColor Yellow
}

# Create requirements.txt
$requirementsContent = @"
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
PyMuPDF==1.23.8
nltk==3.8.1
scikit-learn==1.3.2
sentence-transformers==2.2.2
chromadb==0.4.15
openai==1.3.5
sqlalchemy==2.0.23
psycopg2-binary==2.9.7
python-dotenv==1.0.0
pydantic==2.5.0
requests==2.31.0
pandas==2.1.3
numpy==1.25.2
websockets==12.0
aiofiles==23.2.1
"@

Set-Content -Path "backend/requirements.txt" -Value $requirementsContent
Write-Host "Created: backend/requirements.txt" -ForegroundColor Yellow

# Create .env.example
$envContent = @"
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# LLM Settings
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=800

# Database
DATABASE_URL=postgresql://localhost/physician_ai

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Text Chunking
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# CORS (comma-separated list)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Security
SECRET_KEY=change-this-to-a-random-secret-key-in-production
"@

Set-Content -Path "backend/.env.example" -Value $envContent
Write-Host "Created: backend/.env.example" -ForegroundColor Yellow

# Create .gitignore
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Environment variables
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data
data/medical_books/*.pdf
data/knowledge_base/chroma_db/

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Node (for frontend)
node_modules/
build/
dist/
"@

Set-Content -Path ".gitignore" -Value $gitignoreContent
Write-Host "Created: .gitignore" -ForegroundColor Yellow

# Create README for medical_books
$readmeContent = @"
# Medical Books Directory

Place your medical PDF textbooks here.

The AI assistant will automatically:
1. Detect new PDFs in this directory
2. Extract and process the content
3. Add the knowledge to the searchable database
4. Use this information to answer medical queries

Supported formats: PDF

## Example books to add:
- Harrison's Principles of Internal Medicine
- Oxford Handbook of Clinical Medicine
- The Washington Manual of Medical Therapeutics
- Pharmacology textbooks
- Specialty-specific references

The system will continuously monitor this folder and learn from new books automatically.
"@

Set-Content -Path "data/medical_books/README.md" -Value $readmeContent
Write-Host "Created: data/medical_books/README.md" -ForegroundColor Yellow

Write-Host "`nProject structure created successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Copy the service files (knowledge_base.py, llm_service.py, etc.) into backend/app/services/"
Write-Host "2. Copy .env.example to .env and add your OpenAI API key"
Write-Host "3. Run: cd backend && python -m venv venv && .\venv\Scripts\activate"
Write-Host "4. Run: pip install -r requirements.txt"
Write-Host "5. Place medical PDF books in data/medical_books/"