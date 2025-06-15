# Logging global y depuración en el proyecto FastAPI

## ¿Cómo funciona el logging?

El proyecto implementa una configuración global de logging en `main.py` que controla el nivel de detalle de los logs en toda la aplicación, incluidos los repositorios CRUD.

### Configuración automática por entorno
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

## Logging en los repositorios CRUD

En el método `list_filtered` de `BaseRepository`, se registra automáticamente:
- Los filtros aplicados (excluyendo contraseñas u otros datos sensibles)
- Los parámetros de paginación (`skip`, `limit`)
- El nombre del modelo consultado

Solo se loguea esta información si el nivel de logging es `DEBUG`.

Ejemplo de log generado:
```
2025-06-13 21:40:00,123 - app.crud.base - DEBUG - [User] Filtros aplicados: {'email': 'test@example.com'}, skip=0, limit=100
```

## ¿Cómo cambiar el entorno?

El entorno se controla desde la configuración en `app/core/config.py`:

```python
class Settings(BaseSettings):
    ...
    DEBUG: bool = True  # Cambia a False en producción
```

También puedes usar una variable de entorno `DEBUG` si usas `.env`.

## Recomendaciones
- Mantén `DEBUG = True` solo en desarrollo.
- En producción, usa `DEBUG = False` para evitar logs sensibles y mejorar el rendimiento.
- Si necesitas depurar problemas en producción, puedes activar temporalmente el nivel DEBUG, pero recuerda volver a INFO cuando termines.

---

**Resumen:**
- El logging es centralizado, seguro y configurable.
- Facilita la depuración y el monitoreo.
- No impacta el rendimiento en producción.

Si tienes dudas o necesitas agregar logs en otros módulos, consulta este archivo o contacta al responsable del backend.(gompatri@gmail.com)
