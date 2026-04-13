from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class NotificationBase(BaseModel):
    product_id: Optional[UUID] = None
    message: str
    is_read: bool = False


class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
