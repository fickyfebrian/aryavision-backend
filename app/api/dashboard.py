from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.product import ProductService
from app.utils.response import success_response
from app.api.deps import get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

@router.get("/stats", summary="Get dashboard statistics")
async def get_dashboard_stats(
    service: ProductService = Depends(get_product_service),
    current_admin: Admin = Depends(get_current_admin) # Menambahkan proteksi autentikasi JWT
):
    stats = service.get_dashboard_statistics()
    return success_response(
        data=stats,
        message="Dashboard statistics retrieved successfully"
    )
