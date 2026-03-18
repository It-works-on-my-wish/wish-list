-- Migration to add purchase state to products
ALTER TABLE IF EXISTS public.products
ADD COLUMN IF NOT EXISTS purchase_state TEXT
DEFAULT 'pending'
CHECK (purchase_state IN ('pending', 'purchased'));

-- Optional index for filtering products by purchase state
CREATE INDEX IF NOT EXISTS idx_products_purchase_state ON public.products(purchase_state);
