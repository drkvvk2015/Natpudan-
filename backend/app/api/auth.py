"""Authentication endpoints with social login support."""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import secrets
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

# JWT Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production, load from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# OAuth2 Configuration - Load from environment variables
OAUTH_CONFIG = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
    },
    "microsoft": {
        "client_id": os.getenv("MICROSOFT_CLIENT_ID", ""),
        "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET", ""),
        "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "userinfo_url": "https://graph.microsoft.com/v1.0/me",
    }
}

# In-memory user store (replace with database in production)
users_db: Dict[str, Dict[str, Any]] = {}

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


def hash_password(password: str) -> str:
    """Simple password hashing (use bcrypt in production)."""
    return f"hashed_{password}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password (use bcrypt in production)."""
    return hashed_password == f"hashed_{plain_password}"


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """Register a new user."""
    if request.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_data = {
        "email": request.email,
        "full_name": request.full_name,
        "role": request.role,
        "password": hash_password(request.password),
        "created_at": datetime.utcnow().isoformat(),
        "auth_provider": "local"
    }
    
    if request.license_number:
        user_data["license_number"] = request.license_number
    
    users_db[request.email] = user_data
    
    token_data = {"sub": request.email, "role": request.role}
    access_token = create_access_token(token_data)
    
    user_response = {k: v for k, v in user_data.items() if k != "password"}
    
    return {
        "access_token": access_token,
        "user": user_response
    }


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login with email and password."""
    user = users_db.get(request.email)
    
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = {"sub": request.email, "role": user["role"]}
    access_token = create_access_token(token_data)
    
    user_response = {k: v for k, v in user.items() if k != "password"}
    
    return {
        "access_token": access_token,
        "user": user_response
    }


@router.get("/oauth/{provider}/url")
async def get_oauth_url(provider: str, redirect_uri: str):
    """Get OAuth authorization URL for a provider."""
    if provider not in OAUTH_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )
    
    config = OAUTH_CONFIG[provider]
    
    # Build authorization URL
    params = {
        "client_id": config["client_id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile" if provider == "microsoft" else "email profile",
    }
    
    if provider == "google":
        params["scope"] = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
    elif provider == "github":
        params["scope"] = "user:email"
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    auth_url = f"{config['auth_url']}?{query_string}"
    
    return {"auth_url": auth_url, "provider": provider}


@router.post("/oauth/callback", response_model=TokenResponse)
async def oauth_callback(request: SocialLoginRequest):
    """Handle OAuth callback and create/login user."""
    provider = request.provider
    
    if provider not in OAUTH_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}"
        )
    
    config = OAUTH_CONFIG[provider]
    
    try:
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
                headers={"Accept": "application/json"}
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            token_data = token_response.json()
            access_token_oauth = token_data.get("access_token")
            
            if not access_token_oauth:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No access token in response"
                )
            
            # Get user info
            headers = {"Authorization": f"Bearer {access_token_oauth}"}
            if provider == "github":
                headers["Accept"] = "application/vnd.github.v3+json"
            
            userinfo_response = await client.get(
                config["userinfo_url"],
                headers=headers
            )
            
            if userinfo_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch user info"
                )
            
            user_info = userinfo_response.json()
            
            # Extract email and name based on provider
            if provider == "google":
                email = user_info.get("email")
                name = user_info.get("name")
            elif provider == "github":
                email = user_info.get("email")
                if not email:
                    # GitHub might require additional API call for email
                    email_response = await client.get(
                        "https://api.github.com/user/emails",
                        headers=headers
                    )
                    emails = email_response.json()
                    primary_email = next((e for e in emails if e.get("primary")), None)
                    email = primary_email.get("email") if primary_email else None
                name = user_info.get("name") or user_info.get("login")
            elif provider == "microsoft":
                email = user_info.get("mail") or user_info.get("userPrincipalName")
                name = user_info.get("displayName")
            else:
                email = user_info.get("email")
                name = user_info.get("name")
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not retrieve email from provider"
                )
            
            # Create or update user
            if email in users_db:
                user = users_db[email]
            else:
                user = {
                    "email": email,
                    "full_name": name or email.split("@")[0],
                    "role": "staff",  # Default role for social login
                    "created_at": datetime.utcnow().isoformat(),
                    "auth_provider": provider,
                }
                users_db[email] = user
            
            # Create JWT token
            token_data_jwt = {"sub": email, "role": user["role"]}
            access_token_jwt = create_access_token(token_data_jwt)
            
            user_response = {k: v for k, v in user.items() if k != "password"}
            
            return {
                "access_token": access_token_jwt,
                "user": user_response
            }
    
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth provider error: {str(e)}"
        )


@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = users_db.get(email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_response = {k: v for k, v in user.items() if k != "password"}
        return user_response
    
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
