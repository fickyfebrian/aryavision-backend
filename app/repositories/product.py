from typing import Optional, Tuple

from sqlalchemy import func, asc, desc, or_
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
        cluster: Optional[int] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = "asc"
    ) -> Tuple[list[Product], int]:
        query = self.db.query(Product)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(Product.product_name.ilike(search_term))
            
        if cluster is not None:
            query = query.filter(Product.cluster == cluster)
            
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
            
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
            
        if min_rating is not None:
            query = query.filter(Product.rating >= min_rating)
            
        if max_rating is not None:
            if max_rating == 5 and min_rating == 5:
                query = query.filter(Product.rating <= 5)
            else:
                query = query.filter(Product.rating < max_rating)
            
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

    def get_dashboard_statistics(self) -> dict:
        total_products = self.db.query(func.count(Product.id)).scalar() or 0
        total_brands = self.db.query(func.count(func.distinct(Product.brand))).scalar() or 0
        budget_cluster = self.db.query(func.count(Product.id)).filter(Product.cluster == 0).scalar() or 0
        mid_range_cluster = self.db.query(func.count(Product.id)).filter(Product.cluster == 1).scalar() or 0
        premium_cluster = self.db.query(func.count(Product.id)).filter(Product.cluster == 2).scalar() or 0
        
        return {
            "total_products": total_products,
            "total_brands": total_brands,
            "budget_cluster": budget_cluster,
            "mid_range_cluster": mid_range_cluster,
            "premium_cluster": premium_cluster
        }
