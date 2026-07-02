from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    product_name: str = Field(..., min_length=1, description="Nama produk wajib diisi")
    product_url: Optional[str] = None
    image_url: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    price: int = Field(default=0, ge=0, description="Harga tidak boleh negatif")
    rating: Optional[float] = Field(default=None, ge=0, le=5, description="Rating hanya boleh 0 sampai 5")
    sold: Optional[int] = Field(default=0, ge=0, description="Sold minimal 0")
    description: Optional[str] = None
    cluster: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1)
    product_url: Optional[str] = None
    image_url: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    rating: Optional[float] = Field(None, ge=0, le=5)
    sold: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginationInfo(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    pagination: PaginationInfo
