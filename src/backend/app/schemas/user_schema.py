from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    created_at: datetime | None = None