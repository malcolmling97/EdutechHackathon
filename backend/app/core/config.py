"""
Core configuration management for the EdutechHackathon backend.

Uses Pydantic Settings for type-safe configuration with environment variable loading.
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Core application settings
    app_name: str = Field(default="EdutechHackathon API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Database configuration
    database_url: str = Field(default="sqlite:///./data/edutech.db", env="DATABASE_URL")
    test_database_url: str = Field(default="sqlite:///./test_data/test_edutech.db", env="TEST_DATABASE_URL")
    
    # Security and authentication
    jwt_secret_key: str = Field(
        default="dev-secret-key-change-in-production-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        env="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")
    
    # AI/ML configuration
    openai_api_key: str = Field(default="your-openai-api-key-here", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=1000, env="OPENAI_MAX_TOKENS")
    
    # File processing and storage
    max_file_size: int = Field(default=26214400, env="MAX_FILE_SIZE")  # 25MB
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    temp_dir: str = Field(default="./temp", env="TEMP_DIR")
    
    # CORS configuration
    cors_origins: str = Field(default="http://localhost:3000,http://127.0.0.1:3000", env="CORS_ORIGINS")
    
    # API configuration
    api_v1_prefix: str = "/api/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"
    
    model_config = SettingsConfigDict(env_file=".env.test" if os.getenv("ENVIRONMENT") == "test" else ".env", env_file_encoding="utf-8", extra="ignore")

    ENVIRONMENT: str = "development"


# Global settings instance
settings = Settings() 