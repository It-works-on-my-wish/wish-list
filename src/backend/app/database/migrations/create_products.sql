-- Migration to create the Products table
CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES public.categories(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    url TEXT,
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low')),
    check_frequency TEXT DEFAULT 'daily' CHECK (check_frequency IN ('hourly', 'daily', 'weekly')),
    auto_track BOOLEAN DEFAULT TRUE,
    current_price NUMERIC(10, 2),
    target_price NUMERIC(10, 2),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for fetching a user's products quickly
CREATE INDEX IF NOT EXISTS idx_products_user_id ON public.products(user_id);
-- Index for filtering by category
CREATE INDEX IF NOT EXISTS idx_products_category_id ON public.products(category_id);
