"""
Configuración específica para tests de integración.
Sobrescribe valores problemáticos de la configuración principal.
"""
from app.core.config import Settings


class TestSettings(Settings):
    """Configuración específica para tests."""
    # Sobrescribir valores problemáticos
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 días
    
    # Usar la base de datos de Docker que acabamos de levantar
    SQLALCHEMY_DATABASE_URI: str = "postgresql+asyncpg://postgres:postgres@localhost/fastapi_db_test"
    
    # Desactivar debug para tests
    DEBUG: bool = False


# Instancia de configuración para tests
test_settings = TestSettings()
