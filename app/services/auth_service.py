from app.core.security.hashing import Hasher
from app.core.security.jwt import create_access_token
from app.domain.exceptions.base import ValidationError
from app.domain.models.user import User
from app.domain.repositories.base import IUserRepository


class AuthService:
    def __init__(self, user_repository: IUserRepository, hasher: Hasher):
        self.user_repository = user_repository
        self.hasher = hasher

    async def authenticate_user(self, email: str, password: str):
        user = await self.user_repository.get_by_email(email)
        if not user or not self.hasher.verify_password(password, user.hashed_password):
            raise ValidationError("Credenciales incorrectas")
        return user

    def generate_token(self, user: User):
        return create_access_token(subject=str(user.id))
