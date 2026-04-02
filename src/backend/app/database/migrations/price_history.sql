CREATE TABLE IF NOT EXISTS public.price_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    price NUMERIC(10, 2) NOT NULL,
    checked_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON public.price_history(product_id);
CREATE INDEX IF NOT EXISTS idx_price_history_checked_at ON public.price_history(checked_at);