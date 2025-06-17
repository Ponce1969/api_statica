"""
Base declarativa central para todos los modelos ORM.

Todos los modelos deben heredar de `Base` para ser reconocidos por SQLAlchemy.
"""
import uuid  # Added for default value of id
from typing import Any

from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import UUID as PG_UUID  # Added for UUID type
from sqlalchemy.orm import (  # Added Mapped, mapped_column
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)


class Base(DeclarativeBase):
    """
    Clase base común para todos los modelos.
    Provee nombre de tabla automático, representación, conversión a dict y una columna 'id' UUID por defecto.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Identificador único universal para la entidad."
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Define el nombre de la tabla automáticamente si no se especifica en el modelo.
        Usa el nombre de la clase en minúsculas como fallback.
        """
        if "__tablename__" in cls.__dict__:
            return cls.__tablename__
        return cls.__name__.lower()

    def __repr__(self) -> str:
        try:
            columns = [f"{k}={getattr(self, k)!r}" for k in self.__table__.columns.keys()]
            return f"<{self.__class__.__name__}({', '.join(columns)})>"
        except Exception:
            return f"<{self.__class__.__name__} (no table bound)>"

    def to_dict(self, include: list[str] | None = None, exclude: list[str] | None = None) -> dict[str, Any]:
        """
        Convierte la instancia ORM en un diccionario solo con columnas reales.
        Args:
            include: Lista de campos a incluir (opcional).
            exclude: Lista de campos a excluir (opcional).
        Returns:
            Diccionario con los valores de las columnas.
        """
        from sqlalchemy import inspect
        try:
            keys = [c.key for c in inspect(self).mapper.column_attrs]
            if include:
                keys = [k for k in keys if k in include]
            if exclude:
                keys = [k for k in keys if k not in exclude]
            return {k: getattr(self, k) for k in keys}
        except Exception:
            return {}

    # 🧪 Pro: integración opcional con Pydantic BaseModel
    # Útil si usas modelos Pydantic para respuestas API
    def as_pydantic(self, model: type[BaseModel], strict: bool = False) -> BaseModel:
        """
        Convierte la instancia ORM en un modelo Pydantic.
        Args:
            model: Clase del modelo Pydantic.
            strict: Si es True, exige que todos los campos requeridos estén presentes.
        Returns:
            Instancia del modelo Pydantic validada.
        """
        data = self.to_dict()
        return model.model_validate(data, strict=strict)
