from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional
from uuid import UUID
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    url: Optional[HttpUrl] = None
    category_id: Optional[UUID] = None
    priority: str = "medium"
    check_frequency: str = "daily"
    auto_track: bool = True
    current_price: Optional[float] = None
    target_price: Optional[float] = None
    purchase_state: Literal["pending", "purchased"] = "pending"

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    category_id: Optional[UUID] = None
    priority: Optional[str] = None
    check_frequency: Optional[str] = None
    auto_track: Optional[bool] = None
    target_price: Optional[float] = None
    purchase_state: Optional[Literal["pending", "purchased"]] = None
