from collections import Counter
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.models.product import Product

from app.database.connection import get_db
from app.ml.constants import SELECTED_FEATURES
from app.ml.dataset_loader import load_dataset_from_db
from app.ml.feature_engineering import extract_features
from app.ml.preprocessing import prepare_dataset
from app.ml.scaler import min_max_scaler
from app.ml.kmeans import train_model, predict_cluster, save_model, load_model, cluster_summary
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

@router.get("/clustering", summary="Run K-Means Clustering")
async def run_clustering(db: Session = Depends(get_db)):
    """
    Menjalankan proses clustering pada seluruh produk.
    1. Ambil dataset & preprocess
    2. Scaling
    3. Latih model KMeans
    4. Simpan model
    5. Update tabel products dengan hasil cluster
    """
    df_raw = load_dataset_from_db(db)
    if df_raw.empty:
        return error_response(message="Dataset is empty.", status_code=status.HTTP_400_BAD_REQUEST)
        
    df_clean = prepare_dataset(df_raw)
    df_features = extract_features(df_clean)
    df_scaled = min_max_scaler(df_features)
    
    # Latih model
    model = train_model(df_scaled, n_clusters=3)
    save_model(model)
    
    # Prediksi
    clusters = predict_cluster(model, df_scaled)
    
    # Update DB
    # df_clean masih memiliki kolom 'id' dari tabel products
    ids = df_clean['id'].tolist()
    
    # Batch update
    for product_id, cluster_label in zip(ids, clusters):
        db.query(Product).filter(Product.id == product_id).update({"cluster": cluster_label})
    
    db.commit()
    
    distribution = dict(Counter(clusters))
    
    return success_response(
        data={
            "total_product_processed": len(ids),
            "total_clusters": 3,
            "distribution": distribution
        },
        message="Clustering completed successfully and database updated."
    )

@router.get("/clusters", summary="Get Cluster Summaries")
async def get_clusters(db: Session = Depends(get_db)):
    """
    Mendapatkan ringkasan statistik dari masing-masing cluster.
    """
    df_raw = load_dataset_from_db(db)
    if df_raw.empty:
        return error_response(message="Dataset is empty.", status_code=status.HTTP_400_BAD_REQUEST)
        
    df_clean = prepare_dataset(df_raw)
    
    # Karena kita ingin summary, kita perlu memprediksi ulang atau mengambil dari DB.
    # Spesifikasi meminta ringkasan cluster. Kita bisa predik ulang dengan model yang disimpan.
    try:
        model = load_model()
    except FileNotFoundError:
        return error_response(message="Model not found. Please run /clustering first.", status_code=status.HTTP_404_NOT_FOUND)
        
    df_features = extract_features(df_clean)
    df_scaled = min_max_scaler(df_features)
    clusters = predict_cluster(model, df_scaled)
    
    # Buat summary menggunakan df_clean agar nilai average price dsb tidak menggunakan nilai scaler
    summary = cluster_summary(df_clean, clusters)
    
    return success_response(
        data=summary,
        message="Cluster summaries retrieved successfully."
    )

