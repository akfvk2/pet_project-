from typing import Annotated
from fastapi import Depends
from src.mappers.product_mapper import ProductMapper
from src.repositories.product import ProductRepository


ProductMapperDep = Annotated[ProductMapper, Depends(ProductMapper)]
ProductRepositoryDep = Annotated[ProductRepository, Depends(ProductRepository)]