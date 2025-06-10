"""
Modelo de dominio para la entidad Contacto.
Este modelo representa el concepto de contacto en el dominio de la aplicación,
independientemente de la persistencia o infraestructura.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.exceptions.base import ValidationError, StructuralValidationError
from app.domain.models.base import AuditableEntity


class Contact(AuditableEntity):
    """Entidad de dominio que representa un contacto en el sistema."""
    
    __slots__ = ("name", "email", "message", "phone", "read", "_id", "created_at", "updated_at")
    
    name: str
    email: str
    message: str
    phone: Optional[str]
    read: bool
    
    def __init__(
        self,
        name: str,
        email: str,
        message: str,
        phone: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        read: bool = False
    ):
        super().__init__(entity_id, created_at, updated_at)
        
        # Validación básica en el constructor
        if not name.strip():
            raise ValueError("El nombre no puede estar vacío")
        if not email or "@" not in email:
            raise ValueError("Email inválido")
        if not message.strip():
            raise ValueError("El mensaje no puede estar vacío")
        
        self.name = name
        self.email = email
        self.message = message
        self.phone = phone
        self.read = read
        
        # Validación completa del objeto
        self.validate()
    
    def update_message(self, new_message: str) -> None:
        """Actualiza el mensaje del contacto."""
        if not new_message.strip():
            raise ValueError("El mensaje no puede estar vacío")
        self.message = new_message
        self.updated_at = datetime.utcnow()
    
    def update_contact_info(self, name: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None) -> None:
        """Actualiza la información de contacto."""
        if name is not None:
            if not name.strip():
                raise ValueError("El nombre no puede estar vacío")
            self.name = name
            
        if email is not None:
            if not email or "@" not in email:
                raise ValueError("Email inválido")
            self.email = email
            
        if phone is not None:  # Permitimos establecer phone en None explícitamente
            self.phone = phone
            
        self.updated_at = datetime.utcnow()
        self.validate()
    
    def mark_as_read(self) -> None:
        """Marca el contacto como leído."""
        if self.read:
            return
        self.read = True
        self.updated_at = datetime.utcnow()
    
    def mark_as_unread(self) -> None:
        """Marca el contacto como no leído."""
        if not self.read:
            return
        self.read = False
        self.updated_at = datetime.utcnow()
    
    def validate(self) -> None:
        """Realiza validaciones completas en el objeto contacto.
        
        Raises:
            StructuralValidationError: Si hay errores estructurales en los datos.
            ValidationError: Si hay errores de validación de reglas de negocio.
        """
        errors = {}
        
        # Validaciones estructurales
        if not self.name or not self.name.strip():
            errors["name"] = "El nombre es requerido y no puede estar vacío"
        
        if not self.email:
            errors["email"] = "El email es requerido"
        elif "@" not in self.email:
            errors["email"] = "El email debe tener un formato válido"
            
        if not self.message or not self.message.strip():
            errors["message"] = "El mensaje es requerido y no puede estar vacío"
        
        # Si hay errores estructurales, lanzar excepción
        if errors:
            raise StructuralValidationError("Error de validación en el contacto", errors)
        
        # Validaciones de reglas de negocio (ejemplos)
        business_errors = {}
        if len(self.message) > 1000:
            business_errors["message"] = "El mensaje no puede exceder los 1000 caracteres"
            
        if self.email.endswith(".test"):
            business_errors["email"] = "No se permiten emails de prueba"
            
        # Si hay errores de reglas de negocio, lanzar excepción
        if business_errors:
            raise ValidationError("Error en reglas de negocio para el contacto", business_errors)
    
    def __eq__(self, other: object) -> bool:
        """Compara si dos contactos son iguales basado en su id."""
        if not isinstance(other, Contact):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Permite usar contactos en sets y como claves de diccionarios."""
        return hash(self.id)
        
    def __str__(self) -> str:
        return f"Contact(id={self.id}, name={self.name}, email={self.email})"
