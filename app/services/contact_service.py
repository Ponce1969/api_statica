"""
Servicio para la gestión de contactos.

Contiene la lógica de negocio relacionada con contactos, separada del acceso a datos
y de la presentación (API).
"""
from collections.abc import Sequence
from uuid import UUID

from app.domain.exceptions.base import EntityNotFoundError
from app.domain.models.contact import Contact
from app.domain.repositories.base import ContactRepository


class ContactService:
    """Servicio para gestionar la lógica de negocio relacionada con contactos."""
    
    def __init__(self, contact_repository: ContactRepository) -> None:
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
    
    async def get_contacts(self) -> Sequence[Contact]:
        """
        Obtiene la lista de todos los contactos.
        
        Returns:
            Sequence[Contact]: Lista de contactos
        """
        return await self.contact_repository.list()
    
    async def get_contacts_by_email(self, email: str) -> Sequence[Contact]:
        """
        Obtiene contactos por email.
        
        Args:
            email: Email a buscar
            
        Returns:
            Sequence[Contact]: Lista de contactos con ese email
        """
        return await self.contact_repository.get_by_email(email)
    
    async def create_contact(self, contact: Contact) -> Contact:
        """
        Crea un nuevo contacto.
        
        Args:
            contact: Contacto a crear
            
        Returns:
            Contact: El contacto creado
        """
        return await self.contact_repository.create(contact)
    
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
