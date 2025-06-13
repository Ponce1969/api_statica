"""
Manejadores de eventos para la aplicación FastAPI.
Estos eventos se ejecutan durante la inicialización (startup) y finalización (shutdown)
de la aplicación, permitiendo realizar tareas como establecer/cerrar conexiones a la DB.
"""
"""
Manejadores de eventos para la aplicación FastAPI.
Se ejecutan durante startup y shutdown para tareas como conexión a la DB o liberar recursos.
"""
import logging
from sqlalchemy.exc import SQLAlchemyError

from app.database.session import SessionLocal

logger = logging.getLogger(__name__)


async def startup_event() -> None:
    """
    Función que se ejecuta cuando la aplicación inicia.
    Verifica la conexión a la base de datos y permite inicializar servicios externos.
    """
    logger.info("🚀 Aplicación iniciando...")

    try:
        with SessionLocal() as db:
            db.execute("SELECT 1")
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
    """
    logger.info("🛑 Aplicación cerrando... Liberando recursos.")
    # TODO: Cerrar conexiones Redis, borrar archivos temporales, etc.

    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Conexión a la base de datos verificada correctamente")
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        raise


async def shutdown_event() -> None:
    """
    Función que se ejecuta cuando la aplicación se cierra.
    
    Realiza tareas como:
    - Cerrar conexiones a la base de datos
    - Liberar recursos
    - Enviar notificaciones de cierre
    """
    logger.info("Aplicación cerrando... Liberando recursos.")
