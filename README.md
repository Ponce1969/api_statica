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

```
├── app/
│   ├── main.py                     # Punto de entrada de la aplicación FastAPI
│   ├── core/                       # Configuración y utilidades globales 
│   │   ├── config.py               # Gestión de variables de entorno (.env)
│   │   ├── security.py             # Hashing de contraseñas (Argon2), JWT
│   │   ├── deps.py                 # Inyección de dependencias 
│   │   ├── events.py               # Manejadores de eventos (startup/shutdown)
│   │   └── exceptions.py           # Excepciones personalizadas generales
│   ├── domain/                     # Capa de dominio - Reglas y entidades core
│   │   ├── models/                 # Modelos puros de dominio (sin ORM)
│   │   │   ├── base.py             # Clases base (Entity, ValueObject)
│   │   │   ├── user.py             # Modelo de dominio User
│   │   │   ├── role.py             # Modelo de dominio Role
│   │   │   └── contact.py          # Modelo de dominio Contact
│   │   ├── exceptions/             # Excepciones específicas del dominio
│   │   │   └── base.py             # Excepciones base del dominio
│   │   ├── repositories/           # Interfaces de repositorios (puertos)
│   │   │   └── base.py             # Interfaces abstractas para repositorios
│   │   └── value_objects/          # Objetos de valor inmutables
│   ├── services/                   # Capa de aplicación - Lógica de negocio
│   │   ├── user_service.py         # Servicio para gestión de usuarios
│   │   ├── role_service.py         # Servicio para gestión de roles
│   │   └── contact_service.py      # Servicio para gestión de contactos
│   ├── database/                   # Configuración y modelos de la base de datos
│   │   ├── session.py              # Sesión de SQLAlchemy
│   │   ├── models.py               # Modelos ORM de SQLAlchemy
│   │   └── base.py                 # Declaración de la base de SQLAlchemy
│   ├── crud/                       # Implementaciones concretas de repositorios
│   │   ├── base.py                 # Implementación base de repositorios
│   │   ├── user.py                 # Repositorio de usuarios
│   │   ├── role.py                 # Repositorio de roles
│   │   └── contact.py              # Repositorio de contactos
│   ├── schemas/                    # Modelos Pydantic para validación de datos
│   │   ├── user.py                 # Schemas para usuarios
│   │   ├── role.py                 # Schemas para roles
│   │   ├── contact.py              # Schemas para contactos
│   │   └── token.py                # Schemas para JWT
│   ├── api/                        # Capa de presentación - Endpoints API
│   │   ├── users.py                # Endpoints para usuarios
│   │   ├── roles.py                # Endpoints para roles
│   │   ├── contacts.py             # Endpoints para contactos
│   │   └── auth.py                 # Endpoints para autenticación
```
├── .env.example                    # Ejemplo del archivo de variables de entorno
├── Dockerfile                      # Define la imagen Docker de la API
├── docker-compose.yml              # Orquesta los servicios (API, DB)
├── requirements.txt                # Dependencias de Python
├── venv/                           # Entorno virtual de Python (Ignorado por Git)
└── README.md                       # Este archivo

### Principios de Clean Architecture Aplicados

La implementación sigue una estructura de capas concéntricas donde las dependencias siempre apuntan hacia el centro:

1. **Capa de Dominio (centro)**: Contiene las entidades y reglas de negocio core. No tiene dependencias externas.
   - Entidades puras sin acoplamientos a SQLAlchemy u otras tecnologías
   - Interfaces de repositorios (puertos) que definen contratos
   - Excepciones específicas del dominio

2. **Capa de Aplicación**: Implementa los casos de uso (servicios) de la aplicación.
   - Orquesta entidades de dominio para implementar lógica de negocio
   - Depende del dominio, pero no de infraestructura
   - Principio de inversión de dependencias mediante interfaces

3. **Capa de Infraestructura**: Implementaciones técnicas concretas.
   - Modelos ORM que implementan persistencia
   - Implementaciones concretas de repositorios
   - Configuración de frameworks y bibliotecas

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