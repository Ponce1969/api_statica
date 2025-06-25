from pydantic import EmailStr, TypeAdapter

email_adapter = TypeAdapter(EmailStr)

class Email:
    def __init__(self, email: str):
        try:
            self._email = email_adapter.validate_python(email.lower())
        except Exception as e:
            raise ValueError(f"Invalid email format: {email}") from e

    @property
    def email(self) -> str:
        return str(self._email)

    def __str__(self) -> str:
        return self.email

    def __repr__(self) -> str:
        return f"Email(email='{self.email}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return NotImplemented
        return self.email == other.email

    def __hash__(self) -> int:
        return hash(self.email)
