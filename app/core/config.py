import os
import secrets

from pydantic import EmailStr, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    
    # JWT settings
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32), min_length=32
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 días
    ALGORITHM: str = "HS256"
    
    # Project info
    PROJECT_NAME: str = "Contacts Management API"
    PROJECT_VERSION: str = "0.1.0"
    DEBUG: bool = True  # Cambia a False en producción
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost", "http://localhost:8000", "http://localhost:3000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(f"Valor inválido para CORS_ORIGINS: {v}")

    # Superuser settings
    FIRST_SUPERUSER: EmailStr = Field(
        default="admin@example.com", 
        description="Email superusuario inicial"
    )
    FIRST_SUPERUSER_PASSWORD: str = Field(default="password123", min_length=8)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

settings = Settings()
