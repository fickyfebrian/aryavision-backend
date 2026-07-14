from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
import pandas as pd
import math
import io

from app.ml.preprocessing import clean_dataset
from app.ml.feature_engineering import extract_features, extract_cbf_features
from app.ml.scaler import min_max_scaler
from app.ml.kmeans import predict_cluster, load_model
from app.ml.evaluation import calculate_elbow, calculate_silhouette

router = APIRouter(prefix="/lab", tags=["Lab Algoritma"])

@router.post("/process-dataset", summary="Memproses dataset uji (CSV) secara stateless")
async def process_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
        
    content = await file.read()
    try:
        df_raw = pd.read_csv(io.BytesIO(content))
        
        # Normalize column names to lowercase and strip whitespace
        df_raw.columns = df_raw.columns.astype(str).str.lower().str.strip()
        
        # Map alternative/Indonesian names to expected names
        column_mapping = {
            'harga': 'price',
            'terjual': 'sold',
            'nama produk': 'product_name',
            'nama_produk': 'product_name',
            'nama': 'product_name',
            'kategori': 'category'
        }
        df_raw.rename(columns=column_mapping, inplace=True)
        
        # Validate required columns
        required_cols = ['price', 'rating', 'sold']
        missing = [c for c in required_cols if c not in df_raw.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"CSV is missing required columns: {missing}. Pastikan CSV memiliki kolom: price, rating, sold, atau dalam bahasa Indonesia (harga, terjual).")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
        
    # Clean Data
    df_clean, stats = clean_dataset(df_raw)
    
    if df_clean.empty:
        raise HTTPException(status_code=400, detail="Dataset is empty after cleaning.")
    
    # Hitung bounds (min max)
    bounds = {
        "price": {"min": float(df_clean['price'].min()), "max": float(df_clean['price'].max())},
        "rating": {"min": float(df_clean['rating'].min()), "max": float(df_clean['rating'].max())},
        "sales": {"min": float(df_clean['sold'].min()), "max": float(df_clean['sold'].max())}
    }
    
    try:
        model = load_model()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="K-Means model not found in the server. Please train first.")
        
    # K-Means logic
    df_features = extract_features(df_clean)
    df_scaled = min_max_scaler(df_features)
    clusters = predict_cluster(model, df_scaled)
    df_clean['cluster'] = clusters
    
    # Calculate Dynamic Evaluation Metrics for this dataset
    # Hanya lakukan jika jumlah sampel cukup untuk k-means (min 10)
    dynamic_evaluation = None
    if len(df_scaled) >= 10:
        try:
            elbow_data = calculate_elbow(df_scaled, max_k=min(10, len(df_scaled)-1))
            silhouette_data = calculate_silhouette(df_scaled, max_k=min(10, len(df_scaled)-1))
            
            # Find best k based on silhouette
            best_k = 3
            if silhouette_data:
                best_k_entry = max(silhouette_data, key=lambda x: x['score'])
                best_k = best_k_entry['k']
                
            dynamic_evaluation = {
                "recommended_k": best_k,
                "elbow": elbow_data,
                "silhouette": silhouette_data
            }
        except Exception as e:
            # Jika perhitungan metrics gagal (misal data terlalu homogen), skip saja
            pass
    
    # Calculate normalization for display
    df_cbf_features = extract_cbf_features(df_clean)
    df_cbf_scaled = min_max_scaler(df_cbf_features)
    
    # Prepare Normalized Output
    normalized_products = []
    for i, row in df_clean.iterrows():
        scaled_row = df_cbf_scaled.iloc[i]
        normalized_products.append({
            "id": int(row.get('id', i)),
            "product_name": str(row.get('product_name', 'Unknown')),
            "priceNorm": float(scaled_row['price']),
            "ratingNorm": float(scaled_row['rating']),
            "salesNorm": float(scaled_row['sold'])
        })
        
    # Prepare Raw Output
    raw_products_data = []
    for i, r in df_raw.iterrows():
        raw_products_data.append({
            "id": int(r.get('id', i)) if pd.notna(r.get('id')) else i,
            "product_name": str(r.get('product_name', 'Unknown')),
            "price": float(r['price']) if 'price' in r and pd.notna(r['price']) else None,
            "rating": float(r['rating']) if 'rating' in r and pd.notna(r['rating']) else None,
            "sold": int(r['sold']) if 'sold' in r and pd.notna(r['sold']) else None,
            "category": str(r.get('category', 'Uncategorized')) if pd.notna(r.get('category')) else "Uncategorized"
        })
        
    # Prepare Cleaned Output
    cleaned_products_data = []
    for i, r in df_clean.iterrows():
        cleaned_products_data.append({
            "id": int(r.get('id', i)),
            "product_name": str(r.get('product_name', 'Unknown')),
            "price": float(r['price']),
            "rating": float(r['rating']),
            "sold": int(r['sold']),
            "category": str(r.get('category', 'Uncategorized')) if pd.notna(r.get('category')) else "Uncategorized",
            "cluster": int(r['cluster'])
        })
        
    # Prepare Cluster Empirical Stats
    min_prices = df_clean.groupby('cluster')['price'].min()
    max_prices = df_clean.groupby('cluster')['price'].max()
    
    label_map = {0: "Budget", 1: "Mid Range", 2: "Premium"}
    cluster_stats = []
    for cluster_id in sorted(df_clean['cluster'].unique()):
        cluster_id = int(cluster_id)
        cluster_df = df_clean[df_clean['cluster'] == cluster_id]
        
        cluster_stats.append({
            "cluster_id": cluster_id,
            "label": label_map.get(cluster_id, "Unknown"),
            "total_product": int(len(cluster_df)),
            "average_price": float(cluster_df['price'].mean()),
            "min_price": float(min_prices.get(cluster_id, 0.0)),
            "max_price": float(max_prices.get(cluster_id, 0.0)),
            "average_rating": float(cluster_df['rating'].mean()),
            "average_sold": float(cluster_df['sold'].mean())
        })

    return {
        "success": True,
        "message": "Dataset berhasil diproses secara stateless.",
        "data": {
            "stats": stats,
            "bounds": bounds,
            "clusters": cluster_stats,
            "raw_products": raw_products_data,
            "cleaned_products": cleaned_products_data,
            "normalized_products": normalized_products,
            "evaluation": dynamic_evaluation
        }
    }


class CBFCalcRequest(BaseModel):
    target: dict
    alt: dict
    bounds: dict

@router.post("/cbf-calc", summary="Menghitung Cosine Similarity secara rinci")
async def calculate_cbf(payload: CBFCalcRequest):
    def normalize(val, min_val, max_val):
        if max_val == min_val: return 0.0
        return (val - min_val) / (max_val - min_val)
        
    try:
        bounds = payload.bounds
        
        target_norm = [
            round(normalize(payload.target.get('price', 0), bounds['price']['min'], bounds['price']['max']), 4),
            round(normalize(payload.target.get('rating', 0), bounds['rating']['min'], bounds['rating']['max']), 4),
            round(normalize(payload.target.get('sold', 0), bounds['sales']['min'], bounds['sales']['max']), 4)
        ]
        
        alt_norm = [
            round(normalize(payload.alt.get('price', 0), bounds['price']['min'], bounds['price']['max']), 4),
            round(normalize(payload.alt.get('rating', 0), bounds['rating']['min'], bounds['rating']['max']), 4),
            round(normalize(payload.alt.get('sold', 0), bounds['sales']['min'], bounds['sales']['max']), 4)
        ]
        
        dot_product = sum(t * a for t, a in zip(target_norm, alt_norm))
        mag_target = math.sqrt(sum(t * t for t in target_norm))
        mag_alt = math.sqrt(sum(a * a for a in alt_norm))
        
        similarity = 0.0
        if mag_target > 0 and mag_alt > 0:
            similarity = dot_product / (mag_target * mag_alt)
            
        return {
            "success": True,
            "data": {
                "target_norm": target_norm,
                "alt_norm": alt_norm,
                "dot_product": dot_product,
                "magnitude_target": mag_target,
                "magnitude_alt": mag_alt,
                "similarity": similarity
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in CBF calculation: {str(e)}")
