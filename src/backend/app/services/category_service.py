from uuid import UUID
from typing import List
from app.enums.category_enums import PredefinedCategory
from app.factories.category_factory import CategoryFactory
from app.repositories.category_repository import CategoryRepository
from app.schemas.category_schema import Category, CategoryCustom

class CategoryService:

    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def initialize_default_categories(self, user_id: UUID) -> List[Category]:
        created_categories = []

        # facade pattern for creating pre-defined categories of a user
        for category_type in PredefinedCategory:
            category = CategoryFactory.create_predefined(user_id, category_type)
            saved = self.repository.save(category)
            created_categories.append(saved)

        # return a list of created categories
        return created_categories
    
    def list_user_categories(self, user_id: UUID) -> List[Category]:
        return self.repository.find_by_user(user_id)
    
    def create_new_category(self, user_id: UUID, custom_category: CategoryCustom):
        new_category = CategoryFactory.create_custom(user_id, custom_category)
        return self.repository.save(new_category)

