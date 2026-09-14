"""
AgentOps Observatory - Configuration (Phase 2 & 10)
Local-first defaults with environment overrides for PostgreSQL, Redis, Ollama, and Auth.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AgentOps Observatory"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security & Auth
    SECRET_KEY: str = "agentops-observatory-super-secure-production-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    API_KEY_HEADER: str = "X-AgentOps-API-Key"
    ADMIN_API_KEY: str = "agy-adm-prod-live-key-9999"
    WEBHOOK_SIGNING_SECRET: str = "n8n-agentops-hmac-secret-signature"
    
    # Database
    # Local-first SQLite default; seamlessly switches to postgresql+asyncpg:// when provided
    DATABASE_URL: str = "sqlite+aiosqlite:///./agentops_observatory.db"
    
    # Redis (Optional caching / rate limiting)
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS: bool = False
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 1200
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173", "*"]
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
