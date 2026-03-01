import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv() # load the env variables from .env file

# use the .env files as if they come from the real environment directly
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

"""
if not all(supabase_url, supabase_key):
    raise EnvironmentError("One or more of Supabase env variables are missing.")
"""

supabase: Client = create_client(supabase_url, supabase_key)