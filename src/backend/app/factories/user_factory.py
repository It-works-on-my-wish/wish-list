"""
from uuid import UUID
from app.schemas.user_schema import User

class UserFactory:

    @staticmethod
    def create_user(first_name: str, last_name: str, email: str) -> User:
        return User(
            id=None,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
"""