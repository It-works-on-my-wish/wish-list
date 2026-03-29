from app.schemas.user_schema import UserCreate, UserRead
from app.database.supabase_client import supabase
from postgrest.exceptions import APIError
from fastapi import HTTPException

class UserRepository:

    def save(self, user: UserCreate) -> UserRead:
        try:
            response = supabase.table("users").insert({
                "first_name": str(user.first_name),
                "last_name": str(user.last_name),
                "email": str(user.email)
            }).execute()

            
        except APIError as e:
            if e.code == "23505":
                raise HTTPException(
                    status_code=400,
                    detail="This e-mail adress is already taken."
                )
            raise

        data = response.data[0]

        return UserRead(
            id=data["id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            created_at=data["created_at"]
        )
