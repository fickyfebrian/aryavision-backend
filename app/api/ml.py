from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.ml.constants import SELECTED_FEATURES
from app.ml.dataset_loader import load_dataset_from_db
from app.ml.feature_engineering import extract_features
from app.ml.preprocessing import prepare_dataset
from app.ml.scaler import min_max_scaler
from app.utils.response import success_response

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

@router.get("/test", summary="Test ML Pipeline Preparation")
async def test_ml_pipeline(db: Session = Depends(get_db)):
    """
    Endpoint sementara untuk memastikan seluruh pipeline Machine Learning berjalan:
    1. Pengambilan dataset dari DB
    2. Preprocessing
    3. Feature Engineering
    4. Scaling (Min-Max sebagai tes)
    """
    # 1. Dataset Loading
    df_raw = load_dataset_from_db(db)
    shape_before = list(df_raw.shape)
    
    # 2. Preprocessing
    df_clean = prepare_dataset(df_raw)
    
    # 3. Feature Engineering
    df_features = extract_features(df_clean)
    
    # 4. Feature Scaling (Testing min-max scaler)
    df_scaled = min_max_scaler(df_features)
    
    shape_after = list(df_scaled.shape)
    
    response_data = {
        "total_products": len(df_raw),
        "selected_features": SELECTED_FEATURES,
        "shape_before": shape_before,
        "shape_after": shape_after
    }
    
    return success_response(
        data=response_data,
        message="Machine Learning pipeline ready"
    )
