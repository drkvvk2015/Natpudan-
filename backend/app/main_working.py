"""
WORKING BACKEND - Minimal, no import conflicts
Registers routes BEFORE startup to avoid conflicts
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import time
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Simple app
app = FastAPI(title="Natpudan AI", version="1.0.0")

START_TIME = time.time()

# CORS - allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Config
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "staff"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# Database import (lazy)
def get_db():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def user_to_dict(user) -> dict:
    """Convert user to dict"""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
    }

# Startup
@app.on_event("startup")
async def startup():
    """Initialize database"""
    try:
        from app.database import init_db
        print("="*60)
        print("[STARTING] STARTING NATPUDAN AI BACKEND")
        print("="*60)
        init_db()
        print("[OK] Database initialized")
        print("[OK] Server ready on http://127.0.0.1:8001")
        print("="*60)
    except Exception as e:
        print(f"[ERROR] Startup error: {e}")
        print("[WARNING]  Continuing without database...")

# Health endpoint
@app.get("/health")
@app.get("/api/health")
def health():
    """Health check"""
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }

# Root
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "message": "Natpudan AI Backend",
        "version": "1.0.0",
        "health_endpoint": "/health",
        "docs": "/docs"
    }

# Auth endpoints
@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint"""
    try:
        from app.crud import authenticate_user
        
        user = authenticate_user(db, request.email, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        token = create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=token,
            user=user_to_dict(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register endpoint"""
    try:
        from app.crud import get_user_by_email, create_user
        
        # Check if user exists
        existing = get_user_by_email(db, request.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user = create_user(
            db=db,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=request.role
        )
        
        token = create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=token,
            user=user_to_dict(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Register error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Import and register routers BEFORE app starts (not during startup event)
# TEMPORARILY DISABLED ALL ROUTERS TO TEST MINIMAL BACKEND
try:
    print("[PACKAGE] No additional routers loaded - testing minimal backend")
    # from app.api import chat_new, discharge, treatment, timeline, analytics, fhir
    # from app.api.knowledge_base import router as kb_router
    
    # app.include_router(chat_new.router, prefix="/api")
    # app.include_router(discharge.router, prefix="/api")
    # app.include_router(kb_router, prefix="/api/medical/knowledge", tags=["knowledge-base"])
    # app.include_router(treatment.router, prefix="/api")
    # app.include_router(timeline.router, prefix="/api")
    # app.include_router(analytics.router, prefix="/api")
    # app.include_router(fhir.router, prefix="/api")
    
    print("[OK] Minimal backend ready (auth + health only)")
except Exception as e:
    print(f"[WARNING]  Router loading error: {e}")
    import traceback
    traceback.print_exc()
    print("[WARNING]  Core auth endpoints still available")

print("[OK] Main module loaded successfully")
