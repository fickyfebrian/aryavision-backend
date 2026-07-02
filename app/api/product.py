from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product import ProductService
from app.utils.response import error_response, paginated_response, success_response

router = APIRouter(prefix="/products", tags=["Products"])


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)


@router.get("", summary="Get all products with pagination, search, and sorting")
async def get_products(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by product name"),
    cluster: Optional[int] = Query(None, description="Filter by cluster ID"),
    min_price: Optional[int] = Query(None, description="Minimum price filter"),
    max_price: Optional[int] = Query(None, description="Maximum price filter"),
    min_rating: Optional[float] = Query(None, description="Minimum rating filter"),
    max_rating: Optional[float] = Query(None, description="Maximum rating filter"),
    sort: Optional[str] = Query(None, description="Sort column (e.g. price, rating, sold, created_at)"),
    order: Optional[str] = Query("asc", description="Sort order (asc or desc)"),
    service: ProductService = Depends(get_product_service)
):
    items, total = service.get_products(
        page=page, 
        limit=limit, 
        search=search, 
        cluster=cluster,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        max_rating=max_rating,
        sort_by=sort, 
        order=order
    )
    
    # We must serialize the SQLAlchemy models to dicts using Pydantic schema
    items_dict = [ProductResponse.model_validate(item).model_dump(mode='json') for item in items]
    
    return paginated_response(
        items=items_dict,
        total_items=total,
        page=page,
        limit=limit,
        message="Products retrieved successfully"
    )


@router.get("/{product_id}", summary="Get a product by ID")
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    product = service.get_product_by_id(product_id)
    product_dict = ProductResponse.model_validate(product).model_dump(mode='json')
    return success_response(data=product_dict, message="Product retrieved successfully")


@router.post("", summary="Create a new product", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    product = service.create_product(product_in)
    product_dict = ProductResponse.model_validate(product).model_dump(mode='json')
    return success_response(data=product_dict, message="Product created successfully", status_code=status.HTTP_201_CREATED)


@router.put("/{product_id}", summary="Update a product")
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    service: ProductService = Depends(get_product_service)
):
    product = service.update_product(product_id, product_in)
    product_dict = ProductResponse.model_validate(product).model_dump(mode='json')
    return success_response(data=product_dict, message="Product updated successfully")


@router.delete("/{product_id}", summary="Delete a product")
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    service.delete_product(product_id)
    return success_response(message="Product deleted successfully")
