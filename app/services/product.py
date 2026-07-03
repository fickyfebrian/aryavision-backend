from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: Session):
        self.repository = ProductRepository(db)

    def get_products(
        self, 
        page: int = 1, 
        limit: int = 20, 
        search: Optional[str] = None,
        cluster: Optional[int] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = "asc"
    ) -> Tuple[list[Product], int]:
        if page < 1:
            page = 1
        if limit < 1:
            limit = 20
            
        skip = (page - 1) * limit
        return self.repository.find_all(
            skip=skip, 
            limit=limit, 
            search=search,
            cluster=cluster,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            max_rating=max_rating,
            sort_by=sort_by, 
            order=order
        )

    def get_product_by_id(self, product_id: int) -> Product:
        product = self.repository.find_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        return product

    def create_product(self, product_in: ProductCreate) -> Product:
        return self.repository.create(product_in)

    def update_product(self, product_id: int, product_in: ProductUpdate) -> Product:
        product = self.get_product_by_id(product_id)
        return self.repository.update(product, product_in)

    def delete_product(self, product_id: int) -> None:
        product = self.get_product_by_id(product_id)
        self.repository.delete(product)

    def get_dashboard_statistics(self) -> dict:
        return self.repository.get_dashboard_statistics()
