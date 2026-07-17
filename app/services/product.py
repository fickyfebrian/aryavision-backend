from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.utils.supabase import delete_image_from_supabase

from app.services.ml_status_service import MLStatusService


class ProductService:
    def __init__(self, db: Session):
        self.db = db
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
        new_product = self.repository.create(product_in)
        # Menandai model perlu dilatih ulang karena penambahan produk baru
        MLStatusService.mark_needs_retrain(self.db)
        return new_product

    def update_product(self, product_id: int, product_in: ProductUpdate) -> Product:
        product = self.get_product_by_id(product_id)
        
        # Mengecek apakah ada perubahan pada field numerik yang mempengaruhi algoritma ML
        update_data = product_in.dict(exclude_unset=True)
        needs_retrain = False
        for field in ["price", "rating", "sold"]:
            if field in update_data and getattr(product, field) != update_data[field]:
                needs_retrain = True
                break
        # Delete old image if changed
        if product_in.image_url is not None and product_in.image_url != product.image_url:
            delete_image_from_supabase(product.image_url)
                
        updated_product = self.repository.update(product, product_in)
        
        if needs_retrain:
            # Menandai model perlu dilatih ulang karena data numerik berubah
            MLStatusService.mark_needs_retrain(self.db)
            
        return updated_product

    def delete_product(self, product_id: int) -> None:
        product = self.get_product_by_id(product_id)
        image_url = product.image_url
        
        self.repository.delete(product)
        
        # Hapus foto dari Supabase jika ada
        if image_url:
            delete_image_from_supabase(image_url)
            
        # Menandai model perlu dilatih ulang karena produk dihapus
        MLStatusService.mark_needs_retrain(self.db)

    def get_dashboard_statistics(self) -> dict:
        return self.repository.get_dashboard_statistics()
