from app.core.security.hashing import Hasher
from app.crud.contact import ContactRepository as ContactRepositoryImpl
from app.crud.role import RoleRepository as RoleRepositoryImpl
from app.crud.user import UserRepository as UserRepositoryImpl
from app.services.auth_service import AuthService
from app.services.contact_service import ContactService
from app.services.role_service import RoleService
from app.services.user_service import UserService

# Repositorios

def get_user_repository() -> UserRepositoryImpl:
    return UserRepositoryImpl()

def get_role_repository() -> RoleRepositoryImpl:
    return RoleRepositoryImpl()

def get_contact_repository() -> ContactRepositoryImpl:
    return ContactRepositoryImpl()

# Hasher

def get_hasher() -> Hasher:
    return Hasher()

# Servicios

def get_user_service() -> UserService:
    return UserService(
        user_repository=get_user_repository(),
        hasher=get_hasher(),
    )

def get_role_service() -> RoleService:
    return RoleService(
        role_repository=get_role_repository(),
    )

def get_contact_service() -> ContactService:
    return ContactService(
        contact_repository=get_contact_repository(),
    )

def get_auth_service() -> AuthService:
    return AuthService(
        user_repository=get_user_repository(),
        hasher=get_hasher(),
    )

    user_repository = UserRepositoryImpl()
    hasher = Hasher()
    return AuthService(user_repository=user_repository, hasher=hasher)
