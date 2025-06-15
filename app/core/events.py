"""
Manejadores de eventos para la aplicación FastAPI.
Estos eventos se ejecutan durante la inicialización (startup) y finalización (shutdown)
de la aplicación, permitiendo realizar tareas como establecer/cerrar conexiones a la DB.
"""
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from app.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def startup_event() -> None:
    """
    Función que se ejecuta cuando la aplicación inicia.
    Verifica la conexión a la base de datos y permite inicializar servicios externos.
    """
    logger.info("🚀 Aplicación iniciando...")

    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        logger.info("✅ Conexión a la base de datos verificada correctamente")
    except SQLAlchemyError as e:
        logger.error("❌ Error al conectar a la base de datos", exc_info=True)
        raise

    # TODO: Inicializar servicios externos (Redis, S3, etc.)
    # TODO: Verificar licencias, planificaciones o variables críticas


async def shutdown_event() -> None:
    """
    Función que se ejecuta cuando la aplicación se cierra.
    Libera recursos abiertos y cierra servicios externos si es necesario.
    
    Realiza tareas como:
    - Cerrar conexiones a la base de datos
    - Liberar recursos
    - Cerrar servicios externos
    """
    logger.info("🛑 Aplicación cerrando... Liberando recursos.")
    # TODO: Cerrar conexiones Redis, borrar archivos temporales, etc.

    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        logger.info("Conexión a la base de datos verificada correctamente")
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        # No lanzamos la excepción durante el cierre para permitir un apagado limpio
    logger.info("Aplicación cerrando... Liberando recursos.")
