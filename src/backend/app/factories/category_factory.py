from uuid import UUID
from app.schemas.category_schema import Category
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