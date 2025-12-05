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
import logging
from dotenv import load_dotenv

from app.database import get_db
from app.crud import (
    get_user_by_email,
    create_user,
    authenticate_user,
    get_user_by_id,
)
from app.models import User

# Load environment once at startup - not at import time
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"Failed to load .env file: {e}")
    pass  # Continue with environment variables

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

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
    role: str = "staff"  # Default to staff, but allow selection


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
        # Alias for frontend variations expecting user_type
        "user_type": user.role.value,
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
        logger.debug(f"Token decoded successfully, user_id: {user_id}")
        if user_id is None:
            logger.error("Token payload missing 'sub' field")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}"
        )
    
    user = get_user_by_id(db, user_id)
    if user is None:
        logger.error(f"User not found in database: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with password hashing."""
    try:
        logger.info(f"Registration attempt for email: {request.email}")
        
        # Check if user already exists
        existing_user = get_user_by_email(db, request.email)
        if existing_user:
            logger.warning(f"Registration failed: Email {request.email} already registered")
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
        
        logger.info(f"User created successfully: {user.email} (ID: {user.id})")
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            user=user_to_dict(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error for {request.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user with email and password."""
    try:
        logger.info(f"Login attempt for email: {request.email}")
        
        user = authenticate_user(db, request.email, request.password)
        if not user:
            logger.warning(f"Login failed for {request.email}: Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        logger.info(f"Login successful for {user.email} (ID: {user.id})")
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            user=user_to_dict(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {request.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return user_to_dict(current_user)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client-side token removal, server can track if needed)."""
    logger.info(f"User logout: {current_user.email}")
    return {
        "message": "Logged out successfully",
        "user_id": current_user.id
    }


@router.get("/oauth/{provider}/url")
async def get_oauth_url(provider: str, redirect_uri: str):
    """Get OAuth authorization URL for specified provider."""
    logger.info(f"OAuth URL requested for provider: {provider}")
    
    if provider not in OAUTH_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    config = OAUTH_CONFIG[provider]
    
    # Check if OAuth credentials are configured
    if not config["client_id"] or not config["client_secret"]:
        logger.warning(f"OAuth credentials not configured for {provider}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{provider.capitalize()} login is not configured. Please contact administrator or use email/password login."
        )
    
    # Generate state parameter for security
    import secrets
    state = secrets.token_urlsafe(32)
    
    # Build parameters based on provider
    if provider == "google":
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
    elif provider == "github":
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "scope": "user:email read:user",
            "state": state
        }
    elif provider == "microsoft":
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "response_mode": "query",
            "scope": "openid profile email",
            "state": state
        }
    else:
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "email profile",
            "state": state
        }
    
    # Build URL with proper encoding
    from urllib.parse import urlencode
    url = f"{config['auth_url']}?{urlencode(params)}"
    
    logger.info(f"OAuth URL generated for {provider}")
    return {"auth_url": url, "state": state}


@router.post("/oauth/callback", response_model=TokenResponse)
async def oauth_callback(request: SocialLoginRequest, db: Session = Depends(get_db)):
    """Handle OAuth callback and create/login user."""
    try:
        provider = request.provider
        logger.info(f"OAuth callback received for provider: {provider}")
        
        if provider not in OAUTH_CONFIG:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}"
            )
        
        config = OAUTH_CONFIG[provider]
        
        # Exchange code for access token
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Prepare token exchange data
            token_data = {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "code": request.code,
                "redirect_uri": request.redirect_uri,
                "grant_type": "authorization_code",
            }
            
            # Set proper headers based on provider
            if provider == "github":
                headers = {"Accept": "application/json"}
            else:
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            
            logger.info(f"Exchanging authorization code for access token with {provider}")
            token_response = await client.post(
                config["token_url"],
                data=token_data,
                headers=headers,
            )
            
            if token_response.status_code != 200:
                error_detail = token_response.text
                logger.error(f"OAuth token exchange failed for {provider}: {error_detail}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange OAuth code for token: {error_detail[:200]}"
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
                # Create new user for OAuth login with selected role
                user = create_user(
                    db=db,
                    email=email,
                    password=None,  # No password for OAuth users
                    full_name=name,
                    role=request.role,  # Use role from request
                    oauth_provider=provider,
                    oauth_id=oauth_id,
                )
            
            # Create JWT access token
            access_token = create_access_token(data={"sub": str(user.id)})
            
            logger.info(f"OAuth login successful for {email} via {provider}")
            return TokenResponse(
                access_token=access_token,
                user=user_to_dict(user)
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth authentication failed: {str(e)}"
        )


# Password Reset Models
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# Password Reset Endpoints
@router.post("/forgot-password")
async def request_password_reset(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """Request a password reset token. In production, this would send an email."""
    try:
        logger.info(f"Password reset requested for: {request.email}")
        
        user = get_user_by_email(db, request.email)
        
        if not user:
            # Don't reveal if user exists for security
            logger.info(f"Password reset: User not found for {request.email}")
            return {"message": "If the email exists, a password reset link will be sent."}
        
        # Generate password reset token (valid for 1 hour)
        reset_token_data = {
            "sub": user.id,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        reset_token = jwt.encode(reset_token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        # In production, send this token via email
        # For now, return it directly (development only)
        reset_link = f"http://127.0.0.1:5173/reset-password?token={reset_token}"
        
        logger.info(f"Password reset token generated for {user.email}")
        print(f"Password Reset Link for {user.email}: {reset_link}")
        
        return {
            "message": "Password reset instructions sent to email.",
            "reset_token": reset_token,  # Remove this in production
            "reset_link": reset_link  # Remove this in production
        }
    except Exception as e:
        logger.error(f"Password reset error for {request.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password using the reset token."""
    try:
        # Verify and decode the reset token
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Get user from database
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        from app.crud import update_user_password
        update_user_password(db, user.id, request.new_password)
        
        return {"message": "Password successfully reset. You can now login with your new password."}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one."
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
