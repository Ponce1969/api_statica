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
    
    # Desactivar debug para tests
    DEBUG: bool = False
    
    # Configuración de base de datos para pruebas
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "TEST_DATABASE_URL", 
        "sqlite+aiosqlite:///./test.db"
    )
    
    # Asegurarse de que DATABASE_URL esté definido para compatibilidad
    DATABASE_URL: str = SQLALCHEMY_DATABASE_URI


# Instancia de configuración para pruebas
test_settings = TestSettings()
