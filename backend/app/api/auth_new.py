"""Authentication endpoints with database integration and social login support."""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import httpx
import os
from dotenv import load_dotenv

from app.database import get_db
from app.crud import (
    get_user_by_email,
    create_user,
    authenticate_user,
    get_user_by_id,
)
from app.models import User

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

# JWT Configuration from environment
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# OAuth2 Configuration from environment
OAUTH_CONFIG = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
    },
    "microsoft": {
        "client_id": os.getenv("MICROSOFT_CLIENT_ID"),
        "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET"),
        "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "userinfo_url": "https://graph.microsoft.com/v1.0/me",
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "staff"
    license_number: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SocialLoginRequest(BaseModel):
    provider: str  # google, github, microsoft
    code: str
    redirect_uri: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def user_to_dict(user: User) -> Dict[str, Any]:
    """Convert User model to dictionary."""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "license_number": user.license_number,
    }


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with password hashing."""
    # Check if user already exists
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    user = create_user(
        db=db,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        role=request.role,
        license_number=request.license_number,
    )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        user=user_to_dict(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user with email and password."""
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        user=user_to_dict(user)
    )


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return user_to_dict(current_user)


@router.get("/oauth/{provider}/url")
async def get_oauth_url(provider: str, redirect_uri: str):
    """Get OAuth authorization URL for specified provider."""
    if provider not in OAUTH_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    config = OAUTH_CONFIG[provider]
    params = {
        "client_id": config["client_id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "email profile" if provider == "google" else "user:email" if provider == "github" else "openid profile email",
    }
    
    if provider == "microsoft":
        params["response_mode"] = "query"
    
    # Build URL
    url = f"{config['auth_url']}?"
    url += "&".join([f"{k}={v}" for k, v in params.items()])
    
    return {"url": url}


@router.post("/oauth/callback", response_model=TokenResponse)
async def oauth_callback(request: SocialLoginRequest, db: Session = Depends(get_db)):
    """Handle OAuth callback and create/login user."""
    provider = request.provider
    
    if provider not in OAUTH_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    config = OAUTH_CONFIG[provider]
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            config["token_url"],
            data={
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "code": request.code,
                "redirect_uri": request.redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Accept": "application/json"},
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange OAuth code for token"
            )
        
        token_data = token_response.json()
        access_token_oauth = token_data.get("access_token")
        
        # Get user info from provider
        headers = {"Authorization": f"Bearer {access_token_oauth}"}
        if provider == "github":
            headers["Accept"] = "application/json"
        
        userinfo_response = await client.get(
            config["userinfo_url"],
            headers=headers,
        )
        
        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from OAuth provider"
            )
        
        userinfo = userinfo_response.json()
        
        # Extract email and name based on provider
        if provider == "google":
            email = userinfo.get("email")
            name = userinfo.get("name", "")
            oauth_id = userinfo.get("id")
        elif provider == "github":
            email = userinfo.get("email")
            if not email:
                # GitHub may require separate API call for email
                email_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers=headers,
                )
                emails = email_response.json()
                email = next((e["email"] for e in emails if e["primary"]), None)
            name = userinfo.get("name") or userinfo.get("login", "")
            oauth_id = str(userinfo.get("id"))
        elif provider == "microsoft":
            email = userinfo.get("mail") or userinfo.get("userPrincipalName")
            name = userinfo.get("displayName", "")
            oauth_id = userinfo.get("id")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported provider"
            )
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by OAuth provider"
            )
        
        # Check if user exists
        user = get_user_by_email(db, email)
        
        if not user:
            # Create new user for OAuth login
            user = create_user(
                db=db,
                email=email,
                password=None,  # No password for OAuth users
                full_name=name,
                role="staff",
                oauth_provider=provider,
                oauth_id=oauth_id,
            )
        
        # Create JWT access token
        access_token = create_access_token(data={"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            user=user_to_dict(user)
        )
