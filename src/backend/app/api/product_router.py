from typing import List
from uuid import UUID

from app.factories.scraper_factory import ScraperFactory, UnsupportedPlatformError
from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import (
    ProductCreate,
    ProductResponse,
    ProductScrapeRequest,
    ProductUpdate,
)
from app.scrapers.scraper_strategy import ScrapingError
from app.services.product_service import ProductService
from fastapi import APIRouter, HTTPException

router = APIRouter()

repository = ProductRepository()
service = ProductService(repository)


@router.post("/users/{user_id}/products", response_model=ProductResponse)
def add_new_product(user_id: UUID, product: ProductCreate):
    """Add a product with manually provided data."""
    try:
        new_prod = service.add_product(user_id, product)
        if not new_prod:
            raise HTTPException(status_code=400, detail="Failed to create product")
        return new_prod
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/products/scrape", response_model=ProductResponse)
def scrape_and_add_product(user_id: UUID, scrape_request: ProductScrapeRequest):
    """
    Add a product by scraping its URL.

    Uses the Factory + Strategy pattern:
    - ScraperFactory inspects the URL domain and creates the right scraper
    - The scraper strategy extracts product data (title, price, image)
    - The product is saved to the database
    """
    try:
        new_prod = service.add_product_from_url(user_id, scrape_request)
        if not new_prod:
            raise HTTPException(
                status_code=400, detail="Failed to create product from URL"
            )
        return new_prod
    except UnsupportedPlatformError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ScrapingError as e:
        raise HTTPException(status_code=502, detail=f"Scraping failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/products", response_model=List[ProductResponse])
def get_user_products(user_id: UUID):
    try:
        products = service.get_user_products(user_id)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product_info(product_id: UUID, product: ProductUpdate):
    try:
        updated = service.update_product_details(product_id, product)
        if not updated:
            raise HTTPException(status_code=404, detail="Product not found")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/products/{product_id}")
def remove_product_endpoint(product_id: UUID):
    try:
        service.remove_product(product_id)
        return {"detail": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# api endpoint to get supported platforms
@router.get("/supported-platforms")
def get_supported_platforms():
    return {"platforms": list(ScraperFactory._DOMAIN_REGISTRY.keys())}
