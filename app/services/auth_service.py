
from app.core.security.hashing import verify_password
from app.core.security.jwt import create_access_token
from app.domain.exceptions.base import ValidationError
from app.domain.models.user import User
from app.domain.repositories.base import IUserRepository


class AuthService:
    def __init__(self, user_repository: IUserRepository) -> None:
        self.user_repository = user_repository

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise ValidationError("Credenciales incorrectas")
        
        hashed_password = await self.user_repository.get_hashed_password_by_email(email)
        if not hashed_password or not verify_password(password, hashed_password):
            raise ValidationError("Credenciales incorrectas")
        return user

    def generate_token(self, user: User) -> dict[str, str]:
        access_token = create_access_token({"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
