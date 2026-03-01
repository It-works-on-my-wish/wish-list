from app.schemas.user_schema import User
from app.database.supabase_client import supabase

class UserRepository:

    def save(self, user: User) -> User:
        response = supabase.table("users").insert({
            "first_name": str(user.first_name),
            "last_name": str(user.last_name),
            "email": str(user.email)
        }).execute()

        data = response.data[0]

        return User(
            id=data["id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            created_at=data["created_at"]
        )