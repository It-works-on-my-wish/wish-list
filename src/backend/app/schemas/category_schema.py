from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class Category(BaseModel):
    name: str
    user_id: UUID
    category_type: str
    created_at: datetime | None = None

class CategoryCustom(BaseModel):
    name:str
    category_type: str