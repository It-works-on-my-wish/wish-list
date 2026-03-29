# Backend Setup Instructions

## Prerequisites
- Python 3.10+
- `pip` package manager
- A Supabase account

## Supabase Setup
This project uses Supabase for the database. To set up your local development environment:

1. **Create a Supabase Project**: Go to [Supabase](https://supabase.com) and create a new project.
2. **Get Credentials**: Once the project is created, go to **Project Settings** -> **API**.
3. **Set Environment Variables**: In this `src/backend` directory, create a `.env` file (or update the existing one) with the following variables:
   
   ```env
   SUPABASE_URL="YOUR_SUPABASE_URL"
   SUPABASE_KEY="YOUR_SUPABASE_ANON_KEY"
   ```
   **Note**: `SUPABASE_KEY` should be your Project API anon key.
4. **Database Schema**: Make sure you have set up the necessary tables in the Supabase SQL editor as per the project's data schema requirements.

## Running the Backend locally

1. Navigate to the backend directory:
   ```bash
   cd src/backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   
The API will be available at `http://localhost:8000`. You can view the interactive API documentation at `http://localhost:8000/docs`.
