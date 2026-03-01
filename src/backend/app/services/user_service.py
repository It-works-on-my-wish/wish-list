from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import User

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, first_name: str, last_name: str, email: str):
        user = User(
            first_name=first_name, 
            last_name=last_name, 
            email=email
        )
        return self.repository.save(user)