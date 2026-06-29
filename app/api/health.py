"""
Health Check Router.

Endpoint untuk mengecek status aplikasi dan koneksi database.
Berguna untuk monitoring dan memastikan semua komponen berjalan normal.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.database.connection import check_database_connection
from app.utils.response import error_response, success_response

router = APIRouter(prefix="/health", tags=["Health Check"])


@router.get("/", summary="Check application health")
async def health_check():
    """
    Mengecek status aplikasi secara keseluruhan.
    Mengembalikan status app dan koneksi database.
    """
    db_connected = check_database_connection()

    health_data = {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy" if db_connected else "degraded",
        "database": "connected" if db_connected else "disconnected",
    }

    if db_connected:
        return success_response(data=health_data, message="Application is healthy")
    else:
        return error_response(
            message="Database connection failed",
            status_code=503,
            errors=health_data,
        )
