# Natpudan AI Medical Assistant

A production-ready FastAPI + React application for medical professionals with AI-powered features, role-based access control (RBAC), and comprehensive patient management capabilities.

## [EMOJI] Features

-  **AI Chat Assistant** - OpenAI GPT-4 integration for medical consultations
- [EMOJI] **Discharge Summary** - AI-powered generation with voice typing support
- [EMOJI] **Role-Based Access Control** - Staff, Doctor, and Admin roles
-  **Secure Authentication** - JWT + OAuth2 (Google, GitHub, Microsoft)
-  **Database Persistence** - SQLAlchemy with SQLite/PostgreSQL
- [EMOJI] **Patient Management** - Intake forms, medical history, treatment plans
- [EMOJI] **Analytics Dashboard** - Demographics, disease trends, treatment outcomes
-  **FHIR Integration** - Healthcare data interoperability
-  **Medical Timeline** - Comprehensive patient event tracking

## [EMOJI] Quick Start

### Prerequisites

- Python 3.10+ (tested with Python 3.14)
- Node.js 18+
- Git

### Backend Setup (FastAPI)

```powershell
# 1. Clone repository
git clone https://github.com/drkvvk2015/Natpudan-.git
cd Natpudan-

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-db.txt

# 4. Create .env file (copy from .env.example if available)
# Or create manually with required environment variables (see below)

# 5. Run backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup (React + Vite)

```powershell
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## RBAC

- Staff: patient data entry, chat.
- Doctor: chat, diagnosis, knowledge base, analytics, FHIR.
- Admin: full access.

##  Environment Variables

Create a `backend/.env` file with the following variables:

### Required

```env
# Database (SQLite for development)
DATABASE_URL=sqlite:///./natpudan.db

# JWT Authentication
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OpenAI Integration (Required for AI features)
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Application URLs
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

### Optional (OAuth Providers)

```env
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
```

### Generate SECRET_KEY

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Get OpenAI API Key

1. Visit <https://platform.openai.com/api-keys>
2. Create a new API key
3. Add to `.env` file
4. Monitor usage at <https://platform.openai.com/usage>

##  Security Features

- **Password Security**: Bcrypt hashing for secure password storage
- **JWT Authentication**: Secure token-based authentication
- **OAuth2 Integration**: Social login with Google, GitHub, Microsoft
- **Database Security**: SQL injection protection via SQLAlchemy ORM
- **Environment Variables**: Sensitive credentials stored in `.env` (never committed)
- **CORS Configuration**: Controlled cross-origin access
- **Dependencies**: Regularly updated via Dependabot alerts

### Security Best Practices

- Never commit `.env` files to version control
- Rotate API keys regularly
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Review GitHub Security tab for vulnerabilities

##  Architecture

### Backend (FastAPI)

- **Database**: SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)
- **Models**: User, Conversation, Message, DischargeSummary
- **Authentication**: JWT + OAuth2 with bcrypt password hashing
- **AI Integration**: OpenAI GPT-4 for medical assistance
- **API Structure**:
  - `/api/auth/*` - Authentication endpoints
  - `/api/chat/*` - AI chat with conversation history
  - `/api/discharge-summary/*` - Discharge summary CRUD + AI generation
  - `/api/medical/*` - Medical features (diagnosis, knowledge base)
  - `/api/treatment/*` - Treatment plan management
  - `/api/analytics/*` - Analytics dashboard
  - `/api/fhir/*` - FHIR integration

### Frontend (React + TypeScript)

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 7
- **UI Library**: Material-UI (MUI) v5
- **Routing**: React Router v6
- **State Management**: React Context API
- **API Client**: Axios
- **Features**:
  - Responsive design
  - Voice typing (Web Speech API)
  - Real-time AI chat
  - OAuth social login
  - Professional medical forms

##  User Roles

### Staff Role

- Patient data entry
- Basic chat access
- View patient records

### Doctor Role

- Full chat access with AI
- Diagnosis assistance
- Discharge summary generation
- Treatment plan creation
- Knowledge base access
- Analytics viewing

### Admin Role

- All doctor permissions
- User management
- System configuration
- Full analytics access

##  API Testing

### Using curl

```powershell
# Register new user
curl -X POST http://127.0.0.1:8001/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"doctor@test.com\",\"password\":\"SecurePass123!\",\"full_name\":\"Dr. Test\",\"role\":\"doctor\",\"license_number\":\"MD12345\"}'

# Login
curl -X POST http://127.0.0.1:8001/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"doctor@test.com\",\"password\":\"SecurePass123!\"}'

# Chat (requires token)
curl -X POST http://127.0.0.1:8001/api/chat/message `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_TOKEN_HERE" `
  -d '{\"message\":\"What are the symptoms of pneumonia?\"}'
```

## [EMOJI] Database

### SQLite (Development)

Database file: `backend/natpudan.db`

View with DB Browser for SQLite: <https://sqlitebrowser.org/>

### PostgreSQL (Production)

Update `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/natpudan_db
```

### Database Migrations

```powershell
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

##  Logo Usage

Professional logo system with medical cross + AI circuit design:

- **Icon**: `frontend/public/logo-icon.svg` (80x80px)
- **Full Logo**: `frontend/public/logo-full.svg` (400x100px with text)
- **React Component**: `frontend/src/components/NatpudanLogo.tsx`

See `LOGO_USAGE.md` for detailed branding guidelines.

## [EMOJI] Troubleshooting

### Backend won't start

```powershell
# Check if all dependencies are installed
cd backend
pip install -r requirements.txt
pip install -r requirements-db.txt

# Check if .env file exists with required variables
cat .env

# Check if port 8001 is available
netstat -an | findstr :8001
```

### Frontend won't start

```powershell
# Reinstall dependencies
cd frontend
Remove-Item -Recurse -Force node_modules
npm install

# Clear cache
npm cache clean --force
```

### Database errors

```powershell
# Delete and recreate database
cd backend
Remove-Item natpudan.db
# Restart backend - database will auto-initialize
```

### OpenAI API errors

- Verify API key is correct in `.env`
- Check API quota at <https://platform.openai.com/usage>
- Ensure proper billing setup

##  Documentation

- API Docs: <http://127.0.0.1:8001/docs> (Swagger UI)
- ReDoc: <http://127.0.0.1:8001/redoc>
- Logo Guidelines: `LOGO_USAGE.md`

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## [EMOJI] License

See `LICENSE` file for details.

##  Acknowledgments

- OpenAI GPT-4 for AI capabilities
- FastAPI framework
- React and Material-UI teams
- Medical professionals for domain expertise

##  Support

For issues and questions:

- GitHub Issues: <https://github.com/drkvvk2015/Natpudan-/issues>
- Check existing documentation and troubleshooting guide first

---

**Note**: This application is for educational and professional use. Always verify AI-generated medical information with qualified healthcare professionals.
