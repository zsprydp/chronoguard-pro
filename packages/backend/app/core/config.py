from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "ChronoGuard Pro"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost/chronoguard_db"
    )
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://chronoguard.ai",
    ]
    
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    ML_MODEL_PATH: str = "ml/models/"
    ML_RETRAIN_SCHEDULE: str = "0 2 * * 0"  # Weekly at 2 AM on Sunday
    
    MIN_NO_SHOW_THRESHOLD: float = 0.15
    MAX_OVERBOOK_PERCENTAGE: float = 0.20
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()