"""
Configuración específica para tests de integración.
Sobrescribe valores problemáticos de la configuración principal.
"""
import os
from app.core.config import Settings
from pydantic_settings import SettingsConfigDict


class TestSettings(Settings):
    """Configuración específica para tests."""
    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Sobrescribir valores problemáticos
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 días
    
    # Usar la base de datos de Docker que acabamos de levantar
    SQLALCHEMY_DATABASE_URI: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_db_test"
    # Desactivar debug para tests
    DEBUG: bool = False
    
    # Fallback para base de datos si no está disponible PostgreSQL
    if not os.getenv("TEST_DATABASE_URL") and "localhost" not in SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "TEST_DATABASE_URL", 
            "sqlite+aiosqlite:///./test.db"
        )
    
    # Asegurarse de que DATABASE_URL esté definido para compatibilidad
    DATABASE_URL: str = SQLALCHEMY_DATABASE_URI


# Instancia de configuración para pruebas
test_settings = TestSettings()
