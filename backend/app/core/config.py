"""Application configuration with environment-based settings."""

import os
from pathlib import Path
from typing import List, Optional
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Natpudan Medical AI"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_JSON: bool = os.getenv("LOG_JSON", "false").lower() == "true"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    JWT_SECRET_KEY: Optional[str] = os.getenv("JWT_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )  # 24 hours

    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
    ).split(",")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./natpudan.db")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))

    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_EMBEDDING_MODEL: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0"))

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_CALLS: int = int(os.getenv("RATE_LIMIT_CALLS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

    # File Upload
    MAX_UPLOAD_SIZE: int = int(
        os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024))
    )  # 10MB

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    KB_DIR: Path = DATA_DIR / "knowledge_base"
    LOGS_DIR: Path = BASE_DIR / "logs"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate SECRET_KEY
        if not self.SECRET_KEY:
            if self.is_production:
                raise ValueError("SECRET_KEY must be set in production")
            # Generate for development
            import secrets
            self.SECRET_KEY = secrets.token_urlsafe(32)

    def get_final_secret_key(self) -> str:
        """Get the JWT secret key, falling back to SECRET_KEY."""
        return self.JWT_SECRET_KEY or self.SECRET_KEY

    def get_database_url(self) -> str:
        """Return the configured database URL."""
        return self.DATABASE_URL

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
