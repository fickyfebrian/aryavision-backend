from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.recommendation import get_recommendations
from app.utils.response import success_response

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/{product_id}", summary="Get Top N Recommendations for a Product")
async def recommend_products(
    product_id: int, 
    limit: int = Query(10, ge=1, le=50, description="Jumlah maksimal rekomendasi yang dikembalikan"),
    db: Session = Depends(get_db)
):
    """
    Menghasilkan daftar produk rekomendasi berdasarkan produk yang dipilih.
    Rekomendasi dihitung menggunakan pendekatan hybrid:
    1. Mencari produk dalam cluster yang sama (K-Means)
    2. Mengurutkan berdasarkan kemiripan konten (TF-IDF & Cosine Similarity)
    """
    result = get_recommendations(db, product_id, limit)
    
    return success_response(
        data=result,
        message="Recommendations generated successfully"
    )
