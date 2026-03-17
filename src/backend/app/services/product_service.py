from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import ProductCreate, ProductUpdate
from uuid import UUID

class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def add_product(self, user_id: UUID, product_data: ProductCreate):
        # Additional business logic would go here if fetching external data immediately etc.
        return self.repository.create_product(user_id, product_data)

    def get_user_products(self, user_id: UUID):
        return self.repository.get_products_by_user(user_id)

    def update_product_details(self, product_id: UUID, product_data: ProductUpdate):
        return self.repository.update_product(product_id, product_data)
        
    def remove_product(self, product_id: UUID):
        return self.repository.delete_product(product_id)
