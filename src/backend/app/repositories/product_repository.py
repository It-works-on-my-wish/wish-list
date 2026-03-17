from app.database.supabase_client import supabase
from app.schemas.product_schema import ProductCreate, ProductUpdate
from uuid import UUID

class ProductRepository:
    def __init__(self):
        self.table_name = "products"

    def create_product(self, user_id: UUID, product_data: ProductCreate):
        # Convert schema to dict and stringify complex types for supabase JSON compat
        data = product_data.dict(exclude_unset=True)
        data["user_id"] = str(user_id)
        if data.get("category_id"):
            data["category_id"] = str(data["category_id"])
        if data.get("url"):
            data["url"] = str(data["url"])
            
        response = supabase.table(self.table_name).insert(data).execute()
        return response.data[0] if response.data else None

    def get_products_by_user(self, user_id: UUID):
        response = supabase.table(self.table_name).select("*").eq("user_id", str(user_id)).execute()
        return response.data

    def update_product(self, product_id: UUID, product_data: ProductUpdate):
        data = product_data.dict(exclude_unset=True)
        if data.get("category_id"):
            data["category_id"] = str(data["category_id"])
        if data.get("url"):
            data["url"] = str(data["url"])
            
        response = supabase.table(self.table_name).update(data).eq("id", str(product_id)).execute()
        return response.data[0] if response.data else None

    def delete_product(self, product_id: UUID):
        response = supabase.table(self.table_name).delete().eq("id", str(product_id)).execute()
        return response.data
