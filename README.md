# Nombre del Proyecto API

API de FastAPI para la gestión de usuarios, roles y contactos, diseñada para una página web estática con React.

## Visión General

Esta API proporciona los servicios backend para una aplicación web estática. Los usuarios pueden dejar sus datos de contacto para ser considerados para trabajos, y los administradores pueden gestionar usuarios y roles. La API está construida con un enfoque en la modularidad y la escalabilidad, utilizando FastAPI, PostgreSQL, SQLAlchemy y JWT.

## Requisitos

* Python 3.12+
* UV (instalable mediante `pip install uv`)
* PostgreSQL (o Docker para ejecutar PostgreSQL en contenedor)

## Arquitectura

La API sigue una arquitectura limpia (Clean Architecture) basada en principios SOLID para garantizar la separación de preocupaciones, facilitando el mantenimiento, la escalabilidad y la testabilidad.

* **Separación de responsabilidades:** Cada componente tiene una función específica (Principio de Responsabilidad Única)
* **Modularidad:** Estructura por capas que facilita el mantenimiento y testeo
* **Escalabilidad:** Preparada para crecer con el versionado de API y nuevos módulos
* **Desacoplamiento:** Componentes independientes que interactúan a través de interfaces (Principio de Inversión de Dependencias)
* **Independencia de frameworks:** Las reglas de negocio no dependen de frameworks o bibliotecas externas

### Estructura de Directorios

📦 app
├── 📄 main.py                     # Punto de entrada actualizado con logging y middleware
├── 📂 core                        # Configuración y utilidades globales
│   ├── 📄 config.py
│   ├── 📄 deps.py
│   ├── 📄 events.py
│   ├── 📄 exceptions.py
│   └── 📂 security
│       ├── 📄 jwt.py
│       └── 📄 hashing.py
├── 📂 domain                      # Capa de dominio puro
│   ├── 📂 exceptions
│   │   └── 📄 domain_exceptions.py
│   ├── 📂 models
│   │   └── 📄 user.py
│   ├── 📂 repositories
│   │   └── 📄 user_repository.py
│   ├── 📂 value_objects
│   │   └── 📄 email.py
│   └── 📂 interfaces              # ✅ NUEVA ESTRUCTURA
│       ├── 📂 http
│       │   └── 📄 protocols.py    # Protocolos para middleware HTTP
│       └── 📂 logging
│           └── 📄 protocols.py    # Protocolos para logging
├── 📂 infrastructure              # Implementaciones de infraestructura
│   ├── 📂 email
│   │   └── 📄 smtp_email.py
│   └── 📂 adapters                # ✅ NUEVA ESTRUCTURA
│       ├── 📂 http
│       │   └── 📄 fastapi_middleware.py  # Middleware para FastAPI
│       └── 📂 logging
│           └── 📄 standard_logger.py     # Logger basado en biblioteca estándar
├── 📂 database
│   ├── 📄 base.py
│   ├── 📄 models.py
│   └── 📄 session.py
├── 📂 crud
│   ├── 📄 base.py
│   ├── 📄 user.py
│   ├── 📄 role.py
│   └── 📄 contact.py
├── 📂 schemas
│   ├── 📄 user.py
│   ├── 📄 role.py
│   ├── 📄 contact.py
│   └── 📄 token.py
├── 📂 services
│   ├── 📄 user_service.py
│   ├── 📄 role_service.py
│   ├── 📄 contact_service.py
│   └── 📄 auth_service.py
└── 📂 api
    └── 📂 v1
        ├── 📄 api.py
        └── 📂 endpoints
            ├── 📄 users.py
            ├── 📄 roles.py
            ├── 📄 contacts.py
            └── 📄 auth.py


### Principios de Clean Architecture Aplicados

La implementación sigue una estructura de capas concéntricas donde las dependencias siempre apuntan hacia el centro:

1. **Capa de Dominio (centro)**: Contiene las entidades y reglas de negocio core. No tiene dependencias externas.
   - Entidades puras sin acoplamientos a SQLAlchemy u otras tecnologías
   - Interfaces de repositorios (puertos) que definen contratos
   - Excepciones específicas del dominio
   - Interfaces (protocolos) para servicios externos como logging y middleware

2. **Capa de Aplicación**: Implementa los casos de uso (servicios) de la aplicación.
   - Orquesta entidades de dominio para implementar lógica de negocio
   - Depende del dominio, pero no de infraestructura
   - Principio de inversión de dependencias mediante interfaces

3. **Capa de Infraestructura**: Implementaciones técnicas concretas.
   - Modelos ORM que implementan persistencia
   - Implementaciones concretas de repositorios
   - Adaptadores concretos para interfaces de dominio (logging, middleware)
   - Configuración de frameworks y bibliotecas

### Sistema de Logging y Middleware

La aplicación implementa un sistema profesional de logging y middleware siguiendo los principios de Clean Architecture y el patrón de puertos y adaptadores:

#### Arquitectura de Logging

1. **Interfaces (Puertos)**:
   - Definidos en `app/domain/interfaces/logging/protocols.py`
   - Incluye `LoggerProtocol` y `LoggerFactoryProtocol` para abstraer la implementación concreta
   - Define niveles de log mediante un enum `LogLevel`

2. **Adaptadores**:
   - Implementados en `app/infrastructure/adapters/logging/standard_logger.py`
   - `StandardLoggerFactory` configura el sistema de logging global
   - `SensitiveDataFilter` protege datos sensibles en los logs (passwords, tokens, etc.)
   - Control de verbosidad para bibliotecas externas (SQLAlchemy, SMTP)

3. **Características**:
   - Configuración diferenciada para entornos de desarrollo y producción
   - Enmascaramiento automático de datos sensibles
   - Control granular de niveles de log por componente
   - Integración transparente con bibliotecas externas

#### Arquitectura de Middleware

1. **Interfaces (Puertos)**:
   - Definidos en `app/domain/interfaces/http/protocols.py`
   - Incluye `RequestProtocol`, `ResponseProtocol` y `MiddlewareProtocol`
   - Define contratos para procesamiento de solicitudes HTTP

2. **Adaptadores**:
   - Implementados en `app/infrastructure/adapters/http/fastapi_middleware.py`
   - `RequestLoggingMiddleware` para monitoreo y logging de solicitudes HTTP
   - `FastAPIMiddlewareFactory` para configuración y gestión de middlewares
   - Implementa correctamente el método `dispatch` requerido por Starlette/FastAPI

3. **Características**:
   - Generación de ID único para cada solicitud (UUID v4)
   - Medición precisa de tiempos de respuesta en milisegundos
   - Detección y alertas de respuestas lentas (configurable)
   - Headers de diagnóstico (X-Request-ID, X-Process-Time)
   - Exclusión configurable de rutas ("/docs", "/redoc", "/openapi.json", "/metrics", "/health")
   - Compatibilidad total con Swagger UI y ReDoc

#### Integración en la Aplicación

Los sistemas de logging y middleware se integran en `main.py` durante la creación de la aplicación FastAPI:

```python
# Configuración de logging centralizada
logging_config.setup_logging(settings.LOG_LEVEL)

# Configuración de middlewares
setup_middlewares(app)
```

Esta integración proporciona una configuración centralizada y coherente con los principios de Clean Architecture, facilitando el monitoreo, depuración y mantenimiento de la aplicación.

4. **Capa de Presentación**: Adaptadores para interactuar con el mundo exterior.
   - Endpoints REST de FastAPI
   - Conversión entre DTOs y modelos de dominio

### Beneficios de esta Arquitectura

* **Testabilidad**: Cada componente puede probarse de forma aislada mediante mocks
* **Mantenibilidad**: Los cambios en una capa no afectan a las demás
* **Independencia tecnológica**: Podríamos cambiar FastAPI por otro framework o SQLAlchemy por otro ORM
* **Extensibilidad**: Fácil agregar nuevas funcionalidades sin modificar código existente
* **Claridad conceptual**: Estructura que refleja el modelo mental del negocio

### Tecnologías y Herramientas Utilizadas

* **Python 3.12:** Versión actualizada del lenguaje con mejoras de rendimiento y nuevas funcionalidades.
* **UV:** Gestor de dependencias ultrarrápido y moderno para Python, reemplazo mejorado de pip.
* **FastAPI:** Framework web asíncrono de alto rendimiento.
* **Pydantic:** Validación de datos y gestión de configuraciones.
* **SQLAlchemy:** ORM para interactuar con la base de datos PostgreSQL.
* **PostgreSQL:** Base de datos relacional robusta y escalable.
* **`psycopg2-binary` (o `asyncpg`):** Driver para PostgreSQL.
* **`python-dotenv`:** Gestión de variables de entorno.
* **`passlib[argon2]`:** Hashing seguro de contraseñas con Argon2.
* **`python-jose`:** Implementación de JSON Web Tokens (JWT) para autenticación.
* **Uvicorn:** Servidor ASGI para ejecutar la aplicación FastAPI.
* **Docker & Docker Compose:** Contenedorización y orquestación de la aplicación y la base de datos.
* **Pytest:** Framework para pruebas.

### Lógica de Negocio Principal

* **Gestión de Usuarios:**
    * Creación, lectura, actualización y eliminación de usuarios (CRUD).
    * Asignación de roles a usuarios.
    * Hashing de contraseñas con Argon2 para seguridad.
* **Autenticación de Usuarios:**
    * Login basado en email y contraseña.
    * Generación y validación de tokens JWT para acceder a recursos protegidos.
    * Protección de rutas según el rol del usuario (administrador, empleador, candidato).
* **Gestión de Roles:**
    * CRUD básico para roles.
    * Definición de roles como "admin", "empleador", "candidato".
* **Gestión de Contactos:**
    * Registro de contactos de personas interesadas (nombre, email, mensaje).
    * Mecanismo para que los administradores marquen los contactos como "leídos".

### Esquema de Base de Datos

A continuación se detalla la estructura de la base de datos para facilitar el entendimiento del modelo de datos, especialmente útil para nuevos desarrolladores.

#### Tabla: users
```
+-------------+-------------+-------------------------------+
| Columna      | Tipo        | Descripción                   |
+-------------+-------------+-------------------------------+
| id           | UUID        | Identificador único           |
| email        | VARCHAR     | Email (único)                 |
| hashed_pwd   | VARCHAR     | Contraseña hasheada (Argon2)  |
| full_name    | VARCHAR     | Nombre completo               |
| is_active    | BOOLEAN     | Estado del usuario            |
| created_at   | TIMESTAMP   | Fecha de creación             |
| updated_at   | TIMESTAMP   | Fecha de última actualización |
+-------------+-------------+-------------------------------+
```

#### Tabla: roles
```
+-------------+-------------+-------------------------------+
| Columna      | Tipo        | Descripción                   |
+-------------+-------------+-------------------------------+
| id           | UUID        | Identificador único           |
| name         | VARCHAR     | Nombre del rol (único)        |
| description  | TEXT        | Descripción del rol           |
| created_at   | TIMESTAMP   | Fecha de creación             |
+-------------+-------------+-------------------------------+

---

## Logging Global y Depuración

### ¿Cómo funciona el logging?

El proyecto implementa una configuración global de logging en `main.py` que controla el nivel de detalle de los logs en toda la aplicación, incluidos los repositorios CRUD.

#### Configuración automática por entorno
- **Desarrollo:** Si el atributo `DEBUG` en `settings` es `True`, el nivel de logging es `DEBUG`. Esto muestra información detallada y es ideal para depuración.
- **Producción:** Si `DEBUG` es `False`, el nivel de logging es `INFO`. Solo se muestran mensajes importantes, evitando ruido innecesario y protegiendo información sensible.

La configuración se realiza así en `main.py`:

```python
import logging
from app.core.config import settings

logging.basicConfig(
    level=logging.DEBUG if getattr(settings, 'DEBUG', False) else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```

### Logging en los repositorios CRUD

En el método `list_filtered` de `BaseRepository`, se registra automáticamente:
- Los filtros aplicados (excluyendo contraseñas u otros datos sensibles)
- Los parámetros de paginación (`skip`, `limit`)
- El nombre del modelo consultado

Solo se loguea esta información si el nivel de logging es `DEBUG`.

Ejemplo de log generado:
```
2025-06-13 21:40:00,123 - app.crud.base - DEBUG - [User] Filtros aplicados: {'email': 'test@example.com'}, skip=0, limit=100
```

### ¿Cómo cambiar el entorno?

El entorno se controla desde la configuración en `app/core/config.py`:

```python
class Settings(BaseSettings):
    ...
    DEBUG: bool = True  # Cambia a False en producción
```

También puedes usar una variable de entorno `DEBUG` si usas `.env`.

### Recomendaciones
- Mantén `DEBUG = True` solo en desarrollo.
- En producción, usa `DEBUG = False` para evitar logs sensibles y mejorar el rendimiento.
- Si necesitas depurar problemas en producción, puedes activar temporalmente el nivel DEBUG, pero recuerda volver a INFO cuando termines.

---

**Resumen:**
- El logging es centralizado, seguro y configurable.
- Facilita la depuración y el monitoreo.
- No impacta el rendimiento en producción.

Si tienes dudas o necesitas agregar logs en otros módulos, consulta este archivo o contacta al responsable del backend.
```

#### Tabla: user_roles (Relación muchos a muchos)
```
+-------------+-------------+-------------------------------+
| Columna      | Tipo        | Descripción                   |
+-------------+-------------+-------------------------------+
| user_id      | UUID        | FK a users.id                 |
| role_id      | UUID        | FK a roles.id                 |
| assigned_at  | TIMESTAMP   | Fecha de asignación del rol   |
+-------------+-------------+-------------------------------+
```

#### Tabla: contacts
```
+-------------+-------------+-------------------------------+
| Columna      | Tipo        | Descripción                   |
+-------------+-------------+-------------------------------+
| id           | UUID        | Identificador único           |
| name         | VARCHAR     | Nombre del contacto           |
| email        | VARCHAR     | Email del contacto            |
| phone        | VARCHAR     | Teléfono del contacto (opcional)|
| message      | TEXT        | Mensaje o consulta            |
| is_read      | BOOLEAN     | Si fue leído por un admin     |
| created_at   | TIMESTAMP   | Fecha de creación             |
| updated_at   | TIMESTAMP   | Fecha de última actualización |
+-------------+-------------+-------------------------------+
```

### Cómo Levantar el Proyecto

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <nombre_del_proyecto>
    ```

2.  **Crear y configurar el archivo `.env`:**
    Copia el archivo de ejemplo y rellena tus propias variables de entorno.
    ```bash
    cp .env.example .env
    # Edita el archivo .env con tus credenciales de PostgreSQL y una SECRET_KEY segura.
    ```

3.  **Levantar los servicios con Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```
    Esto construirá la imagen de la API, creará el volumen de persistencia para PostgreSQL y levantará ambos contenedores.

4.  **Acceder a la API:**
    * La API estará disponible en: `http://localhost:8000`
    * Documentación interactiva (Swagger UI): `http://localhost:8000/docs`
    * Documentación alternativa (ReDoc): `http://localhost:8000/redoc`

### Desarrollo Local (Alternativa sin Docker para la API)

Si prefieres desarrollar la API sin el contenedor Docker para la API (manteniendo la DB en Docker):

1.  **Crear y activar el entorno virtual con UV:**
    ```bash
    # Crear el entorno virtual
    uv venv .venv
    
    # Activar el entorno
    # Linux/macOS:
    source .venv/bin/activate
    # Windows:
    .venv\Scripts\activate
    ```

2.  **Instalar dependencias con UV:**
    ```bash
    uv pip install -r requirements.txt
    ```
    UV instala las dependencias significativamente más rápido que pip convencional.

3.  **Ejecutar las migraciones de la base de datos (si aplicable, ej. con Alembic):**
    (Nota: Se recomienda usar una herramienta de migración de DB como Alembic para gestionar los cambios de esquema en PostgreSQL, aunque no se incluyó en la propuesta inicial para mantener la simplicidad. Si el proyecto crece, es una adición valiosa.)

4.  **Ejecutar la API:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    El `--reload` es útil para el desarrollo, ya que reinicia el servidor automáticamente al detectar cambios en el código.

### Pruebas

Las pruebas están organizadas por tipo para facilitar su ejecución y mantenimiento:

#### Configuración del Entorno para Pruebas (`.env.test`)

Para asegurar un entorno de pruebas aislado y consistente, se utiliza el archivo `.env.test`. Este archivo debe contener las variables de entorno específicas para la ejecución de los tests.

**Configuración de `DATABASE_URL` para Tests Locales:**

Si ejecutas los tests directamente en tu máquina local (no dentro de un contenedor Docker para la API), es crucial que la `DATABASE_URL` en `.env.test` apunte a `localhost` (o la IP de tu host) en lugar de `db` (que es el nombre del servicio de Docker Compose para la base de datos). Asegúrate de que el puerto de PostgreSQL esté correctamente mapeado (e.g., `5432`).

Ejemplo de `.env.test` para desarrollo local:

```dotenv
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/test_db"
DEBUG=True
SECRET_KEY="your_test_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080
```

**Instalación de Dependencias de Test:**

Asegúrate de instalar las dependencias de test usando `uv`:

```bash
uv pip install "[test]"
```

#### Ejecución de Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar solo pruebas unitarias
pytest tests/unit

# Ejecutar solo pruebas de integración 
pytest tests/integration

# Ejecutar solo pruebas de extremo a extremo
pytest tests/e2e
```

### Contribución

Se aceptan contribuciones. Por favor, crea una rama feature y envía un pull request.