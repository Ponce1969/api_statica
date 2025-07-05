import os
import tempfile
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from contextlib import asynccontextmanager

import asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app as fastapi_app
from app.core.config import settings
from app.database.base import Base
from app.database.session import get_async_session

# El engine ahora usará settings.SQLALCHEMY_DATABASE_URI que es configurado
# por el tests/conftest.py global para apuntar a PostgreSQL.

# Crear un motor para pruebas
# @pytest.fixture(scope="session") # Comentado temporalmente según discusión
# def event_loop():
#     """Crea una instancia del bucle de eventos para la sesión de pruebas."""
#     policy = asyncio.WindowsSelectorEventLoopPolicy()
#     loop = policy.new_event_loop()
#     yield loop
#     loop.close()

@pytest.fixture(scope="session")
def engine(): # Ya no depende de TEST_SQLALCHEMY_DATABASE_URL local
    """Crea una instancia del motor de base de datos para pruebas (PostgreSQL)."""
    return create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI, # Usar la URI global de settings
        echo=False, # O True para debug SQL
        poolclass=NullPool
        # connect_args ya no es necesario para PostgreSQL
    )

# Crear tablas una vez al inicio de la sesión de pruebas
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database(engine): # engine ahora es el de PostgreSQL
    """Configura la base de datos antes de cada prueba."""
    # Limpiar y crear esquemas antes de cada prueba
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield  # Aquí se ejecuta la prueba
    
    # Limpiar después de la prueba
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # No eliminamos el archivo aquí, lo haremos al final de la sesión
    
    # Forzar la recolección de basura para liberar conexiones
    import gc
    gc.collect()

# Configurar la sesión de base de datos
@pytest_asyncio.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Crea una sesión de base de datos para cada prueba con transacciones aisladas."""
    # Crear una nueva conexión para esta sesión
    connection = await engine.connect()
    
    # Iniciar una transacción anidada (SAVEPOINT)
    transaction = await connection.begin_nested()
    
    # Configurar la sesión con la conexión
    session = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        class_=AsyncSession,
        future=True
    )()
    
    # Conectar eventos para manejar SAVEPOINT
    from sqlalchemy import event
    @event.listens_for(session.sync_session, 'after_transaction_end')
    def restart_savepoint(session, transaction):
        if connection.closed:
            return
        if not connection.in_nested_transaction():
            connection.sync_connection.begin_nested()
    
    try:
        yield session
        # Hacer commit al final si no hubo errores
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        # Cerrar la sesión y la conexión
        await session.close()
        if connection.invalidated:
            await connection.close()
        else:
            if connection.in_transaction():
                await transaction.rollback()
            await connection.close()

# El fixture db_session_e2e ha sido eliminado.

# Anular la dependencia de la sesión de base de datos (mantener por compatibilidad)
@pytest_asyncio.fixture(scope="function")
async def override_get_db(db_session: AsyncSession):
    """Fixture para inyectar la sesión de base de datos en la aplicación."""
    async def _get_db():
        try:
            yield db_session
        finally:
            # No cerramos la sesión aquí, se maneja en el fixture db_session
            pass
    
    # Aplicar el override solo para esta prueba
    app = fastapi_app
    original_override = app.dependency_overrides.get(get_async_session)
    app.dependency_overrides[get_async_session] = _get_db
    
    try:
        yield
    finally:
        # Restaurar el override original
        if original_override is None:
            app.dependency_overrides.pop(get_async_session, None)
        else:
            app.dependency_overrides[get_async_session] = original_override

# Cliente de prueba HTTP
@pytest_asyncio.fixture(scope="function")
async def client_e2e(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]: # Cambiado a db_session
    """Fixture para el cliente de prueba HTTP E2E con soporte para async."""
    # Importar get_db de app.core.deps que es la dependencia real usada por los endpoints
    from app.core.deps import get_db
    from app.database.session import get_async_session, AsyncSessionLocal
    import sqlalchemy.ext.asyncio
    from app.core import config
    
    # Configurar el cliente para usar ASGITransport
    from httpx import ASGITransport
    
    # Guardar configuraciones originales
    app = fastapi_app
    original_get_db_override = app.dependency_overrides.get(get_db)
    original_get_async_session_override = app.dependency_overrides.get(get_async_session)
    # original_db_url = config.settings.SQLALCHEMY_DATABASE_URI # Ya no es necesario guardar/restaurar
    
    # Ya no se modifica config.settings.SQLALCHEMY_DATABASE_URI a SQLite.
    # Debe usar la configuración de PostgreSQL de tests/conftest.py global.
    
    # Definir la función que devolverá nuestra sesión de prueba
    async def _get_test_db():
        try:
            yield db_session # Usar db_session aquí
        finally:
            pass  # La sesión se cierra en el fixture db_session
    
    # Aplicar el override para ambas dependencias
    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_async_session] = _get_test_db
    
    # Crear el cliente con la aplicación
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
        timeout=30.0
    ) as client:
        try:
            yield client
        finally:
            # Restaurar los overrides originales
            if original_get_db_override is None:
                app.dependency_overrides.pop(get_db, None)
            else:
                app.dependency_overrides[get_db] = original_get_db_override
                
            if original_get_async_session_override is None:
                app.dependency_overrides.pop(get_async_session, None)
            else:
                app.dependency_overrides[get_async_session] = original_get_async_session_override
            
            # Ya no es necesario restaurar config.settings.SQLALCHEMY_DATABASE_URI
            
            # Limpiar cualquier estado después de la prueba
            await client.aclose()

# Crear un usuario de prueba
@pytest_asyncio.fixture(scope="function")
async def create_test_user(db_session: AsyncSession):
    """Fixture para crear un usuario de prueba en la base de datos."""
    from app.core.security.hashing import Argon2PasswordHasher # Importar la clase concreta
    from app.services.user_service import UserService
    from app.crud.user import UserRepository
    from app.schemas.user import UserCreate
    import uuid

    # Fixture para el hasher
    user_repo = UserRepository(db_session) # Necesario para el user_service
    hasher_instance = Argon2PasswordHasher()
    service = UserService(user_repository=user_repo, hasher=hasher_instance)
    
    test_email = f"test_user_e2e_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "testpassword123"
    
    user_in = UserCreate(
        email=test_email,
        full_name="Test User E2E",
        password=test_password
    )

    created_user_response = await service.create_user_with_hashed_password(user_in)

    # Hacer commit para asegurar que el usuario se guarde y se puedan obtener IDs, etc.
    await db_session.commit()
    # Si necesitas el objeto ORM refrescado (ej. para User.id si el servicio no lo devuelve explícitamente en UserResponse)
    # podrías necesitar buscarlo y refrescarlo, pero UserResponse ya debería tener el ID.

    return {
        "email": created_user_response.email,
        "password": test_password, # Devolver la contraseña original en texto plano
        "user_id": str(created_user_response.id),
        "full_name": created_user_response.full_name,
        "is_active": created_user_response.is_active,
        "is_superuser": created_user_response.is_superuser
    }

@pytest_asyncio.fixture(scope="function")
async def create_test_superuser(db_session: AsyncSession):
    """Fixture para crear un superusuario de prueba directamente en la base de datos."""
    from app.crud.user import UserRepository
    from app.domain.models.user import User # Modelo de Dominio
    from app.core.security.hashing import Argon2PasswordHasher # Usar el mismo hasher
    import uuid

    user_repo = UserRepository(db=db_session)
    hasher_instance = Argon2PasswordHasher()

    test_email = f"test_superuser_e2e_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "supertestpassword123"
    hashed_password = hasher_instance.get_password_hash(test_password)

    # Crear la entidad de dominio User
    user_domain_entity = User(
        email=test_email,
        full_name="Test Superuser E2E",
        is_active=True,
        is_superuser=True  # Establecer como superusuario
    )

    # Usar el método create del repositorio
    # Este método espera la entidad de dominio y la contraseña ya hasheada
    created_user_domain = await user_repo.create(
        entity=user_domain_entity,
        hashed_password=hashed_password
    )
    
    # Hacer commit para asegurar que el usuario se guarde
    await db_session.commit()
    
    # El user_repo.create devuelve la entidad de dominio, que ya tiene el ID
    # Si necesitaras refrescar desde el ORM por alguna razón, tendrías que obtener el ORM
    # user_orm = await db_session.get(UserORM, created_user_domain.id) # UserORM es tu modelo SQLAlchemy
    # await db_session.refresh(user_orm)
    # Pero para este caso, la entidad de dominio devuelta por user_repo.create debería ser suficiente.

    return {
        "email": created_user_domain.email,
        "password": test_password, # Contraseña en texto plano para el test
        "user_id": str(created_user_domain.id), # El ID viene de la entidad de dominio
        "full_name": created_user_domain.full_name,
        "is_active": created_user_domain.is_active,
        "is_superuser": created_user_domain.is_superuser
    }

