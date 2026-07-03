from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.product import ProductService
from app.utils.response import success_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

@router.get("/stats", summary="Get dashboard statistics")
async def get_dashboard_stats(
    service: ProductService = Depends(get_product_service)
):
    stats = service.get_dashboard_statistics()
    return success_response(
        data=stats,
        message="Dashboard statistics retrieved successfully"
    )
