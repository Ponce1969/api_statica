# Registro de Cambios (CHANGELOG)

Este documento detalla los cambios notables realizados en el proyecto, siguiendo el formato de [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

## [No Publicado]

### Cambios
- **Seguridad**: Refactorización de los módulos de seguridad para seguir mejor las prácticas de Clean Architecture.
  - Movidas las utilidades de seguridad a submódulos específicos en `app/core/security/`
  - Marcado como obsoleto el archivo `app/core/security.py` que será eliminado en la versión 2.0.0
  - Actualizadas las importaciones en todo el proyecto para usar los nuevos submódulos

### Mejoras
- **Documentación**: Mejorada la documentación de los módulos de seguridad para facilitar su uso y mantenimiento.
- **Arquitectura**: Mejorada la organización del código siguiendo los principios de Clean Architecture.

### Notas para Desarrolladores
- Las importaciones de seguridad deben actualizarse para usar los nuevos submódulos:
  ```python
  # Antes:
  from app.core.security import oauth2_scheme
  
  # Después:
  from app.core.security.oauth2_scheme import oauth2_scheme
  ```
- El archivo `app/core/security.py` mostrará advertencias de desuso hasta su eliminación en la versión 2.0.0.
