from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str

class UserRead(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    created_at: datetime | None = None

    