"""
Production configuration with validation and environment-specific settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Optional
import secrets

# Load environment variables
load_dotenv()


class Settings:
    """Production-ready application settings"""
    
    # Environment
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # API Configuration
    APP_NAME: str = "Physician AI Assistant"
    APP_VERSION: str = "1.0.0"
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    API_PREFIX: str = "/api"
    
    # Security
    SECRET_KEY: str = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        'CORS_ORIGINS', 
        'http://localhost:3000,http://localhost:3001'
    ).split(',')
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL', 
        'sqlite:///./physician_ai.db'
    )
    DATABASE_POOL_SIZE: int = int(os.getenv('DATABASE_POOL_SIZE', '10'))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv('DATABASE_MAX_OVERFLOW', '20'))
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o')
    OPENAI_EMBEDDING_MODEL: str = os.getenv(
        'OPENAI_EMBEDDING_MODEL', 
        'text-embedding-3-small'
    )
    OPENAI_TEMPERATURE: float = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
    OPENAI_MAX_TOKENS: int = int(os.getenv('OPENAI_MAX_TOKENS', '800'))
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_CALLS: int = int(os.getenv('RATE_LIMIT_CALLS', '100'))
    RATE_LIMIT_PERIOD: int = int(os.getenv('RATE_LIMIT_PERIOD', '60'))
    
    # File Upload
    MAX_UPLOAD_SIZE: int = int(os.getenv('MAX_UPLOAD_SIZE', str(10 * 1024 * 1024)))  # 10 MB
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = ['.pdf', '.txt', '.doc', '.docx']
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / 'data'
    MEDICAL_BOOKS_DIR: Path = DATA_DIR / 'medical_books'
    KNOWLEDGE_BASE_DIR: Path = DATA_DIR / 'knowledge_base'
    LOGS_DIR: Path = BASE_DIR / 'logs'
    
    # Knowledge Base
    CHUNK_SIZE: int = int(os.getenv('CHUNK_SIZE', '500'))
    CHUNK_OVERLAP: int = int(os.getenv('CHUNK_OVERLAP', '50'))
    TOP_K_RESULTS: int = int(os.getenv('TOP_K_RESULTS', '5'))
    
    # Caching
    CACHE_ENABLED: bool = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv('ENABLE_METRICS', 'True').lower() == 'true'
    SENTRY_DSN: Optional[str] = os.getenv('SENTRY_DSN')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE: str = 'physician_ai.log'
    
    @classmethod
    def validate(cls):
        """Validate critical configuration and create necessary directories"""
        errors = []
        warnings = []
        
        # Check critical API keys
        if not cls.OPENAI_API_KEY:
            warnings.append("OPENAI_API_KEY not set. AI features will be limited.")
        
        # Validate SECRET_KEY for production
        if cls.ENVIRONMENT == 'production':
            if cls.SECRET_KEY == 'your-secret-key-change-in-production':
                errors.append("SECRET_KEY must be changed in production!")
            
            if cls.DEBUG:
                errors.append("DEBUG must be False in production!")
            
            if 'localhost' in ','.join(cls.CORS_ORIGINS):
                warnings.append("localhost in CORS_ORIGINS for production environment")
        
        # Create directories
        for directory in [cls.DATA_DIR, cls.MEDICAL_BOOKS_DIR, 
                         cls.KNOWLEDGE_BASE_DIR, cls.LOGS_DIR]:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Failed to create directory {directory}: {e}")
        
        # Print validation results
        if warnings:
            print("\n[WARNING]  Configuration Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        if errors:
            print("\n[ERROR] Configuration Errors:")
            for error in errors:
                print(f"  - {error}")
            raise ValueError("Configuration validation failed. Please fix the errors above.")
        
        print("\n[OK] Configuration validated successfully")
        return True
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL with proper formatting"""
        url = cls.DATABASE_URL
        
        # For SQLite, ensure proper path
        if url.startswith('sqlite'):
            if not url.startswith('sqlite:///'):
                url = f"sqlite:///./{url.replace('sqlite://', '')}"
        
        return url
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENVIRONMENT == 'production'
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.ENVIRONMENT == 'development'


# Create settings instance
settings = Settings()
