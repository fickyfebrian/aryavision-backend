from typing import Optional, Tuple

from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = "asc"
    ) -> Tuple[list[Product], int]:
        query = self.db.query(Product)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(Product.product_name.ilike(search_term))
            
        if sort_by:
            # Prevent SQL injection by validating the sort column
            valid_sort_columns = ["price", "rating", "sold", "created_at"]
            if sort_by in valid_sort_columns:
                sort_col = getattr(Product, sort_by)
                if order == "desc":
                    query = query.order_by(desc(sort_col))
                else:
                    query = query.order_by(asc(sort_col))
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        
        return items, total

    def find_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def create(self, product_in: ProductCreate) -> Product:
        product = Product(**product_in.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, db_product: Product, product_in: ProductUpdate) -> Product:
        update_data = product_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
            
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete(self, db_product: Product) -> None:
        self.db.delete(db_product)
        self.db.commit()
