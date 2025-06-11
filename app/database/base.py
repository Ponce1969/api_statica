"""
Base declarativa central para todos los modelos ORM.

Todos los modelos deben heredar de `Base` para ser reconocidos por SQLAlchemy.
"""
from typing import Any, Dict, Optional, List, Type
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    """
    Clase base común para todos los modelos.
    Provee nombre de tabla automático, representación y conversión a dict.
    """

    @declared_attr
    def __tablename__(cls) -> str:
        # Fallback seguro y legible: solo asigna si no está definido explícitamente
        if not hasattr(cls, "__tablename__"):
            return cls.__name__.lower()
        return cls.__tablename__

    def __repr__(self) -> str:
        try:
            columns = [f"{k}={getattr(self, k)!r}" for k in self.__table__.columns.keys()]
            return f"<{self.__class__.__name__}({', '.join(columns)})>"
        except Exception:
            return f"<{self.__class__.__name__} (no table bound)>"

    def to_dict(
        self,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Convierte la instancia a un dict, con opciones para incluir/excluir campos.
        """
        try:
            keys = self.__table__.columns.keys()
            if include:
                keys = [k for k in keys if k in include]
            if exclude:
                keys = [k for k in keys if k not in exclude]
            return {k: getattr(self, k) for k in keys}
        except Exception:
            return {}

    # 🧪 Pro: integración opcional con Pydantic BaseModel
    # Útil si usas modelos Pydantic para respuestas API
    def as_pydantic(self, model: Type[BaseModel]) -> BaseModel:
        """Convierte la instancia ORM en un modelo Pydantic usando model_validate."""
        return model.model_validate(self.to_dict())
