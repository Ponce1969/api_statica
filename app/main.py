from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.events import shutdown_event, startup_event
from app.infrastructure.adapters.http.fastapi_middleware import setup_middlewares
from app.infrastructure.adapters.logging.standard_logger import logger_factory


def create_app() -> FastAPI:
    """Función factory para crear la aplicación FastAPI con todas las configuraciones.
    
    Permite una mejor separación de responsabilidades y facilita las pruebas
    al proporcionar un método consistente para crear la aplicación.
    """
    # Inicializar el sistema de logging
    logger = logger_factory.get_logger("app.main")
    logger.info(f"Iniciando aplicación en modo {'DEBUG' if settings.DEBUG else 'PRODUCCIÓN'}")
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="API para gestión de contactos con sistema de autenticación",
        version=settings.PROJECT_VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configuración CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Configurar middlewares personalizados
    setup_middlewares(app)
    logger.debug("Middlewares configurados correctamente")

    # Incluir router de la API v1
    app.include_router(api_router, prefix=settings.API_V1_STR)
    logger.debug(f"Router API v1 configurado en {settings.API_V1_STR}")
    
    # Registrar manejadores de eventos
    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)
    logger.debug("Manejadores de eventos registrados")
    
    # Ruta raíz para comprobar el funcionamiento básico
    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "message": (
                "Sistema de contactos API. "
                "Dirígete a /docs para la documentación"
            )
        }
    
    # Ruta healthcheck para monitoreo
    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok", "version": settings.PROJECT_VERSION}
    
    return app


app = create_app()
