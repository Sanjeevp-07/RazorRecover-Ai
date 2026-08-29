from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Central application settings loaded from environment variables.
    All environment variables are declared in one single place.
    """
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    APP_NAME: str = "RazorRecover AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"
    
    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "razorrecover_db"
    
    # Supabase Project Credentials
    SUPABASE_URL: str = "https://uiibmlpcsxhugvmxbyio.supabase.co"
    SUPABASE_ANON_KEY: str = "sb_publishable_o5q8vLDMKPlCR1gffWt9gA_tSn897tt"
    SUPABASE_PROJECT_REF: str = "uiibmlpcsxhugvmxbyio"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/razorrecover_db"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/razorrecover_db"
    
    # Redis & Celery
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # AI Model Strategy Tiers (NVIDIA NIM Free LLM Models)
    AI_MODEL_PRIMARY: str = "meta/llama-3.1-8b-instruct"
    AI_MODEL_COST: str = "meta/llama-3.1-8b-instruct"
    AI_MODEL_ESCALATED: str = "meta/llama-3.1-70b-instruct"
    NVIDIA_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    
    # Razorpay Test Mode Credentials (§10)
    RAZORPAY_KEY_ID: str = "rzp_test_key_placeholder"
    RAZORPAY_KEY_SECRET: str = "rzp_test_secret_placeholder"
    RAZORPAY_WEBHOOK_SECRET: str = "rzp_test_webhook_secret_placeholder"
    
    # Encryption key for merchant secrets at rest
    FERNET_KEY: str = "gAAAAABl...place_valid_fernet_key_here..."
    
    # Auth JWT Configuration (§7)
    JWT_SECRET: str = "dev-jwt-secret-key-change-in-production-min-32"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days persistent session
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30       # 30 days persistent refresh

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

settings = Settings()
