from uuid import UUID
from app.schemas.category_schema import Category, CategoryCustom
from app.enums.category_enums import PredefinedCategory

class CategoryFactory:

    @staticmethod
    def create_predefined(user_id: UUID, category_type: PredefinedCategory) -> Category:
        return Category(
            id=None,
            name=category_type.value,
            user_id=user_id,
            category_type=category_type.name
        )
    
    @staticmethod
    def create_custom(user_id: UUID, custom_category: CategoryCustom) -> Category:
        return Category(
            id=None,
            name=custom_category.name,
            user_id=user_id,
            category_type=custom_category.category_type
        )