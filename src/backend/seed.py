import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Missing Supabase credentials. .env file might be missing or broken.")
    exit(1)

supabase: Client = create_client(url, key)
user_id = "123e4567-e89b-12d3-a456-426614174000"

try:
    response = supabase.table("users").upsert({
        "id": user_id,
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com"
    }).execute()
    print("Test user seeded successfully:", response.data)
except Exception as e:
    print("Error seeding user. The `users` table might not be created:", e)
