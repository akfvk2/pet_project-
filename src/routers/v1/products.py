from fastapi import APIRouter, status
from src.schemas import products
from src.services.product_service import ProductService
from uuid import UUID
from fastapi import Depends
from typing import Annotated


router = APIRouter()

ProductServiceDep = Annotated[ProductService, Depends(ProductService)]

@router.post("/", response_model=products.ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(product_in: products.ProductCreate, service: ProductServiceDep):
    return await service.create(product_in)

@router.get("/{product_id}", response_model=products.ProductRead)
async def read_products(product_id: UUID, service: ProductServiceDep):
    return await service.get_by_id(product_id)

@router.put("/{product_id}", response_model=products.ProductRead)
async def update_product(product_id: UUID, product_in: products.ProductUpdate, service: ProductServiceDep):
    return await service.update(product_id, product_in)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: UUID, service: ProductServiceDep):
    return await service.delete(product_id)