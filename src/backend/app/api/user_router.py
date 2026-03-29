from fastapi import APIRouter
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user_schema import UserCreate

router = APIRouter()

repository = UserRepository()
service = UserService(repository)


@router.post("/users")
def create_user(user: UserCreate):
    return service.create_user(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email
    )