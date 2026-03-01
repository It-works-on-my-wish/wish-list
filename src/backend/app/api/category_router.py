from fastapi import APIRouter
from uuid import UUID
from app.repositories.category_repository import CategoryRepository
from app.services.category_service import CategoryService

router = APIRouter()

repository = CategoryRepository()
service = CategoryService(repository)


@router.post("/users/{user_id}/initialize-categories")
def initialize_categories(user_id: UUID):
    return service.initialize_default_categories(user_id)

@router.get("/users/{user_id}/list-categories")
def list_user_categories(user_id: UUID):
    return service.list_user_categories(user_id)