from typing import List
from uuid import UUID
from app.schemas.category_schema import Category
from app.database.supabase_client import supabase
from postgrest.exceptions import APIError
from fastapi import HTTPException

class CategoryRepository:

    def save(self, category: Category) -> Category:
        
        try:
            response = supabase.table("categories").insert({
                "name": category.name,
                "user_id": str(category.user_id),
                "category_type": category.category_type
            }).execute()
        
        except APIError as e:
            if e.code == "23505":
                raise HTTPException(
                    status_code=400,
                    detail="Category already exists for this user."
                )
            raise


        data = response.data[0]

        return Category(
            name=data["name"],
            user_id=data["user_id"],
            category_type=data["category_type"],
            created_at=data["created_at"]
        )
    
    def find_by_user(self, user_id: UUID) -> List[Category]:
        categories = []

        response = supabase.table("categories") \
                                .select("*") \
                                .eq("user_id", str(user_id)) \
                                .execute()
        categories_raw = response.data

        for category in categories_raw:
            categories.append(
                Category(
                    name=category["name"],
                    user_id=category["user_id"],
                    category_type=category["category_type"],
                    created_at=category["created_at"]
                )
            )
        
        return categories

