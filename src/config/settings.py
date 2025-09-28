# Production Environment Configuration

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Production settings with environment variable support"""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8002, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    
    # Database Configuration
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    redis_url: Optional[str] = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    jwt_secret: str = Field(default="your-jwt-secret-change-in-production", env="JWT_SECRET")
    cors_origins: list = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    # API Configuration
    api_rate_limit: int = Field(default=100, env="API_RATE_LIMIT")
    max_request_size: int = Field(default=10 * 1024 * 1024, env="MAX_REQUEST_SIZE")  # 10MB
    
    # AI Model Configuration
    ollama_url: str = Field(default="http://localhost:11434", env="OLLAMA_URL")
    mlx_enabled: bool = Field(default=True, env="MLX_ENABLED")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # File Storage
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Environment-specific configurations
if settings.environment == "production":
    # Production-specific settings
    settings.debug = False
    settings.cors_origins = [
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ]
elif settings.environment == "staging":
    # Staging-specific settings
    settings.debug = True
    settings.cors_origins = [
        "https://staging.yourdomain.com",
        "http://localhost:3000"
    ]
else:
    # Development settings
    settings.debug = True
    settings.cors_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000"
    ]
