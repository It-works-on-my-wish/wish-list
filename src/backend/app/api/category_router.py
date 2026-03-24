from fastapi import APIRouter
from uuid import UUID
from typing import List
from app.repositories.category_repository import CategoryRepository
from app.services.category_service import CategoryService
from app.schemas.category_schema import CategoryCustom
from app.schemas.category_response import CategoryResponse


router = APIRouter()

repository = CategoryRepository()
service = CategoryService(repository)

@router.get("/users/{user_id}/categories", response_model=List[CategoryResponse])
def list_user_categories(user_id: UUID):
    categories = service.list_user_categories(user_id)
    if not categories:
        categories = service.initialize_default_categories(user_id)
    return categories

@router.post("/users/{user_id}/categories/init", response_model=List[CategoryResponse])
def initialize_categories(user_id: UUID):
    return service.initialize_default_categories(user_id)

@router.post("/users/{user_id}/categories", response_model=CategoryResponse)
def add_new_category(user_id: UUID, custom_category: CategoryCustom):
    return service.create_new_category(user_id, custom_category)