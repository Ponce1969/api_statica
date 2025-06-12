from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.role_service import RoleService
from app.services.contact_service import ContactService
from app.domain.repositories.base import IUserRepository, IRoleRepository, IContactRepository
from app.crud.user import UserRepository as UserRepositoryImpl
from app.crud.role import RoleRepository as RoleRepositoryImpl
from app.crud.contact import ContactRepository as ContactRepositoryImpl
from app.core.security.hashing import Hasher

def get_user_service():
    user_repository = UserRepositoryImpl()
    hasher = Hasher()
    return UserService(user_repository=user_repository, hasher=hasher)

def get_role_service():
    role_repository = RoleRepositoryImpl()
    return RoleService(role_repository=role_repository)

def get_contact_service():
    contact_repository = ContactRepositoryImpl()
    return ContactService(contact_repository=contact_repository)

def get_auth_service():
    user_repository = UserRepositoryImpl()
    hasher = Hasher()
    return AuthService(user_repository=user_repository, hasher=hasher)
