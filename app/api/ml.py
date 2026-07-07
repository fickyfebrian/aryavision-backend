from collections import Counter
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.admin import Admin
from app.api.deps import get_current_admin

from app.database.connection import get_db
from app.ml.constants import SELECTED_FEATURES
from app.ml.dataset_loader import load_dataset_from_db
from app.ml.feature_engineering import extract_features, extract_cbf_features
from app.ml.preprocessing import prepare_dataset
from app.ml.scaler import min_max_scaler
from app.ml.kmeans import train_model, predict_cluster, save_model, load_model, cluster_summary
from app.ml.evaluation import calculate_elbow, calculate_silhouette

from app.ml.cbf import train_cbf, save_cbf_models
from app.utils.response import success_response, error_response
from app.services.ml_status_service import MLStatusService

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

@router.get("/status", summary="Get Machine Learning Model Status")
async def get_ml_status(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin) # Menambahkan proteksi autentikasi JWT
):
    status_data = MLStatusService.get_status(db)
    
    return success_response(
        data={
            "needs_retrain": status_data.needs_retrain,
            "last_trained_at": status_data.last_trained_at.isoformat() + "Z" if status_data.last_trained_at else None,
            "last_dataset_update": status_data.last_dataset_update.isoformat() + "Z" if status_data.last_dataset_update else None,
            "model_status": status_data.model_status,
            "model_version": status_data.model_version
        },
        message="Berhasil mengambil status Machine Learning"
    )

@router.get("/test", summary="Test ML Pipeline Preparation (Stats)")
async def test_ml_pipeline(db: Session = Depends(get_db)):
    df_raw = load_dataset_from_db(db)
    if df_raw.empty:
        return error_response(message="Dataset is empty.", status_code=status.HTTP_400_BAD_REQUEST)
        
    df_clean, stats = prepare_dataset(df_raw)
    stats["selected_features"] = SELECTED_FEATURES
    
    return success_response(
        data=stats,
        message="Machine Learning pipeline ready"
    )

@router.get("/clustering", summary="Run K-Means Clustering")
async def run_clustering(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin) # Menambahkan proteksi autentikasi JWT
):
    df_raw = load_dataset_from_db(db)
    if df_raw.empty:
        return error_response(message="Dataset is empty.", status_code=status.HTTP_400_BAD_REQUEST)
        
    df_clean, stats = prepare_dataset(df_raw)
    df_features = extract_features(df_clean)
    df_scaled = min_max_scaler(df_features)
    
    model = train_model(df_scaled, n_clusters=3)
    save_model(model)
    
    clusters = predict_cluster(model, df_scaled)
    
    ids = df_clean['id'].tolist()
    
    for product_id, cluster_label in zip(ids, clusters):
        db.query(Product).filter(Product.id == product_id).update({"cluster": cluster_label})
    
    db.commit()
    
    # Synchronize unclustered products (eliminated during preprocessing like duplicates)
    unclustered = db.query(Product).filter(Product.cluster.is_(None)).all()
    for up in unclustered:
        match = db.query(Product).filter(
            Product.cluster.isnot(None),
            Product.product_name == up.product_name,
            Product.price == up.price
        ).first()
        if match:
            up.cluster = match.cluster
    
    db.commit()
    
    distribution = dict(Counter(clusters))
    
    return success_response(
        data={
            "total_product_processed": len(ids),
            "total_clusters": 3,
            "distribution": distribution,
            "preprocessing_stats": stats
        },
        message="Clustering completed successfully and database updated."
    )

@router.get("/clusters", summary="Get Cluster Summaries")
async def get_clusters(db: Session = Depends(get_db)):
    df_raw = load_dataset_from_db(db)
    if df_raw.empty:
        return error_response(message="Dataset is empty.", status_code=status.HTTP_400_BAD_REQUEST)
        
    df_clean, _ = prepare_dataset(df_raw)
    
    try:
        model = load_model()
    except FileNotFoundError:
        return error_response(message="Model not found. Please run /clustering first.", status_code=status.HTTP_404_NOT_FOUND)
        
    df_features = extract_features(df_clean)
    df_scaled = min_max_scaler(df_features)
    clusters = predict_cluster(model, df_scaled)
    
    summary = cluster_summary(df_clean, clusters)
    
    return success_response(
        data=summary,
        message="Cluster summaries retrieved successfully."
    )

@router.get("/evaluation", summary="Evaluate KMeans Model")
async def evaluate_kmeans(db: Session = Depends(get_db)):
    df_raw = load_dataset_from_db(db)
    if df_raw.empty:
        return error_response(message="Dataset is empty.", status_code=status.HTTP_400_BAD_REQUEST)
        
    df_clean, _ = prepare_dataset(df_raw)
    df_features = extract_features(df_clean)
    df_scaled = min_max_scaler(df_features)
    
    elbow = calculate_elbow(df_scaled, max_k=10)
    silhouette = calculate_silhouette(df_scaled, max_k=10)
    
    # Pilih k rekomendasi dari silhoutte tertinggi
    recommended_k = max(silhouette, key=lambda x: x['score'])['k'] if silhouette else 3
    
    return success_response(
        data={
            "recommended_k": recommended_k,
            "elbow": elbow,
            "silhouette": silhouette
        },
        message="KMeans evaluation completed"
    )

@router.get("/cbf/test", summary="Test Content-Based Filtering Engine")
async def test_cbf_engine(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin) # Menambahkan proteksi autentikasi JWT
):
    """
    Test endpoint to build the CBF Engine:
    1. Load DB
    2. Preprocess (clean_dataset)
    3. Text Preprocess (combine & clean text)
    4. Train Numerical Features & Cosine Similarity
    5. Save Models
    """
    df_raw = load_dataset_from_db(db)
    if df_raw.empty:
        return error_response(message="Dataset is empty.", status_code=status.HTTP_400_BAD_REQUEST)
        
    df_clean, _ = prepare_dataset(df_raw)
    
    # Feature Extraction & Scaling
    df_features = extract_cbf_features(df_clean)
    df_scaled = min_max_scaler(df_features)
    
    # Train CBF
    sim_matrix, product_index = train_cbf(df_scaled, df_clean['id'].tolist())
    
    # Save CBF Models
    save_cbf_models(sim_matrix, product_index)
    
    # Menandai bahwa proses retraining secara keseluruhan (termasuk CBF) telah sukses
    MLStatusService.mark_retrain_success(db)
    
    return success_response(
        data={
            "total_products": len(df_clean),
            "similarity_shape": list(sim_matrix.shape)
        },
        message="Content-Based Filtering Engine Ready"
    )

