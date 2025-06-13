"""
Servicio para la gestión de contactos.

Contiene la lógica de negocio relacionada con contactos, separada del acceso a datos
y de la presentación (API).
"""
from collections.abc import Sequence
from uuid import UUID

from app.domain.exceptions.base import EntityNotFoundError
from app.domain.models.contact import Contact
from app.domain.repositories.base import IContactRepository


class ContactService:
    """Servicio para gestionar la lógica de negocio relacionada con contactos."""
    
    def __init__(self, contact_repository: IContactRepository) -> None:
        self.contact_repository = contact_repository
    
    async def get_contact(self, contact_id: UUID) -> Contact:
        """
        Obtiene un contacto por su ID.
        
        Args:
            contact_id: UUID del contacto a buscar
            
        Returns:
            Contact: El contacto encontrado
            
        Raises:
            EntityNotFoundError: Si no se encuentra ningún contacto con ese ID
        """
        contact = await self.contact_repository.get(contact_id)
        if not contact:
            raise EntityNotFoundError(entity="Contacto", entity_id=contact_id)
        return contact
    
    async def get_contacts(self, email: str | None = None, is_read: bool | None = None):
        """
        Devuelve una lista de ContactResponse (schema), con filtros opcionales por email y estado leído.
        """
        from app.schemas.contact import ContactResponse

        # Lógica de filtrado combinable
        if email is not None and is_read is not None:
            contacts = [c for c in await self.contact_repository.list() if c.email == email and c.is_read == is_read]
        elif email is not None:
            contacts = [c for c in await self.contact_repository.list() if c.email == email]
        elif is_read is not None:
            contacts = [c for c in await self.contact_repository.list() if c.is_read == is_read]
        else:
            contacts = await self.contact_repository.list()
        return [ContactResponse(
            id=c.id,
            full_name=c.full_name,
            email=c.email,
            message=c.message,
            is_read=c.is_read
        ) for c in contacts]
    
    async def get_contacts_by_email(self, email: str) -> Sequence[Contact]:
        """
        Obtiene contactos por email.
        
        Args:
            email: Email a buscar
            
        Returns:
            Sequence[Contact]: Lista de contactos con ese email
        """
        return await self.contact_repository.get_by_email(email)
    
    async def create_contact(self, contact_in):
        """
        Crea un nuevo contacto y retorna el schema de respuesta.
        """
        from uuid import uuid4

        from app.database.models import Contact as ContactORM
        from app.schemas.contact import ContactResponse
        contact_orm = ContactORM(
            id=uuid4(),
            full_name=contact_in.full_name,
            email=contact_in.email,
            message=contact_in.message,
            is_read=contact_in.is_read or False
        )
        created = await self.contact_repository.create(contact_orm)
        return ContactResponse(
            id=created.id,
            full_name=created.full_name,
            email=created.email,
            message=created.message,
            is_read=created.is_read
        )
    
    async def update_contact(self, contact: Contact) -> Contact:
        """
        Actualiza un contacto existente.
        
        Args:
            contact: Contacto con los datos actualizados
            
        Returns:
            Contact: El contacto actualizado
            
        Raises:
            EntityNotFoundError: Si no existe el contacto
        """
        # Verificar que el contacto existe
        existing_contact = await self.contact_repository.get(contact.id)
        if not existing_contact:
            raise EntityNotFoundError(entity="Contacto", entity_id=contact.id)
        
        return await self.contact_repository.update(contact)
    
    async def delete_contact(self, contact_id: UUID) -> None:
        """
        Elimina un contacto.
        
        Args:
            contact_id: ID del contacto a eliminar
            
        Raises:
            EntityNotFoundError: Si no existe el contacto
        """
        contact = await self.contact_repository.get(contact_id)
        if not contact:
            raise EntityNotFoundError(entity="Contacto", entity_id=contact_id)
        
        await self.contact_repository.delete(contact_id)
    
    async def update_contact_message(self, contact_id: UUID, new_message: str) -> Contact:
        """
        Actualiza el mensaje de un contacto.
        
        Args:
            contact_id: ID del contacto a actualizar
            new_message: Nuevo mensaje
            
        Returns:
            Contact: El contacto actualizado
            
        Raises:
            EntityNotFoundError: Si no existe el contacto
        """
        contact = await self.get_contact(contact_id)
        contact.update_message(new_message)
        return await self.contact_repository.update(contact)
