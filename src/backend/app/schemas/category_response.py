from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    user_id: UUID
    category_type: str
    created_at: datetime