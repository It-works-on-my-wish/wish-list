from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from typing import List

router = APIRouter()

repository = ProductRepository()
service = ProductService(repository)

@router.post("/users/{user_id}/products", response_model=ProductResponse)
def add_new_product(user_id: UUID, product: ProductCreate):
    try:
        new_prod = service.add_product(user_id, product)
        if not new_prod:
            raise HTTPException(status_code=400, detail="Failed to create product")
        return new_prod
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/products/{product_id}")
def remove_product_endpoint(product_id: UUID):
    try:
        service.remove_product(product_id)
        return {"detail": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
