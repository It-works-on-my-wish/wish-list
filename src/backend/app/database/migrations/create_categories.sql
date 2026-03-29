CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    user_id UUID NOT NULL,
    category_type text not null,
    created_at TIMESTAMP DEFAULT NOW(),

    unique (user_id, category_type),

    -- if the user is deleted, the category also gets deleted (cascade)
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE 
);
