"""
Manejadores de eventos para la aplicación FastAPI.
Estos eventos se ejecutan durante la inicialización (startup) y finalización (shutdown)
de la aplicación, permitiendo realizar tareas como establecer/cerrar conexiones a la DB.
"""
import logging
from typing import Callable

from fastapi import FastAPI

from app.database.session import SessionLocal

logger = logging.getLogger(__name__)


async def startup_event() -> None:
    """
    Función que se ejecuta cuando la aplicación inicia.
    
    Realiza tareas como:
    - Verificar conexión a la base de datos
    - Inicializar servicios externos
    - Configurar logging
    """
    logger.info("Aplicación iniciando...")
    
    # Verificar conexión a la base de datos
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
