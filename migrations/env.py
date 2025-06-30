import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# Importamos la configuración y modelos de nuestra aplicación
from app.database.base import Base
from app.core.config import settings

# Importamos explícitamente todos los modelos para que Alembic los detecte
# Esto asegura que los modelos estén disponibles para autogenerate
from app.database.models import *

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Usar db_url si está disponible, sino la configuración por defecto con reemplazos
    db_url = config.get_main_option("db_url") or settings.SQLALCHEMY_DATABASE_URI
    url = db_url.replace("postgresql+asyncpg", "postgresql").replace("localhost", "127.0.0.1")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' mode but async."""
    # Configuramos el engine para SQLAlchemy asíncrono
    config_section = config.get_section(config.config_ini_section)
    url = settings.SQLALCHEMY_DATABASE_URI
    config_section["sqlalchemy.url"] = url

    connectable = AsyncEngine(
        engine_from_config(
            config_section,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Usar db_url si está disponible, sino la configuración por defecto con reemplazos
    db_url = config.get_main_option("db_url") or settings.SQLALCHEMY_DATABASE_URI
    config.set_main_option("sqlalchemy.url", db_url.replace("postgresql+asyncpg", "postgresql").replace("localhost", "127.0.0.1"))
    asyncio.run(run_async_migrations())


# Añadimos configuración al inicio para que Alembic sepa dónde está la URL
db_url = context.get_x_argument(as_dictionary=True).get("db_url")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)
else:
    # Configuración por defecto
    config.set_main_option("sqlalchemy.url", str(settings.SQLALCHEMY_DATABASE_URI).replace("localhost", "127.0.0.1"))

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
