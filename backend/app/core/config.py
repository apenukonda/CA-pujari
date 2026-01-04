"""
Configuration management for the E-Learning Platform API
Handles environment variables and application settings
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Configuration
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security Configuration
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS Configuration
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and v:
            return [AnyHttpUrl(url.strip()) for url in v.split(",")]
        elif isinstance(v, list):
            return v
        return []
    
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: str
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_CLIENT_EMAIL: str
    FIREBASE_STORAGE_BUCKET: str
    
    # Google Cloud Configuration
    GOOGLE_APPLICATION_CREDENTIALS: str = "firebase-service-account.json"
    
    # Firestore Configuration
    FIRESTORE_PROJECT_ID: str
    FIRESTORE_COLLECTION_USERS: str = "users"
    FIRESTORE_COLLECTION_COURSES: str = "courses"
    FIRESTORE_COLLECTION_WEBINARS: str = "webinars"
    FIRESTORE_COLLECTION_PURCHASES: str = "purchases"
    FIRESTORE_COLLECTION_FEEDBACK: str = "feedback"
    FIRESTORE_COLLECTION_DOUBTS: str = "doubts"
    
    # Payment Gateway Configuration (Stripe)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_CURRENCY: str = "usd"
    
    # Email Configuration (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "noreply@example.com"
    EMAIL_FROM_NAME: str = "E-Learning Platform"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = None
    
    # Rate Limiting Configuration
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_BURST: int = 10
    
    # Admin Configuration
    ADMIN_EMAIL: Optional[str] = None
    ADMIN_UID: Optional[str] = None
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 1440  # 24 hours
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "mp4", "mp3", "doc", "docx", "ppt", "pptx"]
    UPLOAD_FOLDER: str = "uploads"
    
    # Notification Configuration
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    ENABLE_PUSH_NOTIFICATIONS: bool = False
    WEBINAR_REMINDER_HOURS: int = 24
    
    # Analytics Configuration
    ENABLE_ANALYTICS: bool = True
    ANALYTICS_SAMPLE_RATE: float = 0.1
    
    # Monitoring Configuration
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"
    
    def get_firebase_credentials(self) -> dict:
        """Get Firebase credentials dictionary"""
        return {
            "type": "service_account",
            "project_id": self.FIREBASE_PROJECT_ID,
            "private_key_id": "key-id",  # This would be extracted from the key
            "private_key": self.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
            "client_email": self.FIREBASE_CLIENT_EMAIL,
            "client_id": "client-id",  # This would be extracted from the key
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{self.FIREBASE_CLIENT_EMAIL}"
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the application settings"""
    return settings