CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name text not null,
    last_name text not null,
    email text unique not null,
    created_at TIMESTAMP DEFAULT NOW()
);