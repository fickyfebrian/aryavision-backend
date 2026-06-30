import os
import joblib
import pandas as pd
from sklearn.cluster import KMeans

from app.ml.constants import SELECTED_FEATURES

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "kmeans_model.pkl")

def train_model(df_features: pd.DataFrame, n_clusters: int = 3) -> KMeans:
    """
    Melatih model KMeans dengan konfigurasi random_state=42 dan n_init="auto".
    """
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    model.fit(df_features)
    return model

def predict_cluster(model: KMeans, df_features: pd.DataFrame) -> list[int]:
    """
    Melakukan prediksi cluster berdasarkan model yang telah dilatih.
    """
    return model.predict(df_features).tolist()

def save_model(model: KMeans) -> None:
    """
    Menyimpan model ke dalam file .pkl.
    """
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    joblib.dump(model, MODEL_PATH)

def load_model() -> KMeans:
    """
    Memuat model dari file .pkl.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    return joblib.load(MODEL_PATH)

def evaluate_cluster(df_features: pd.DataFrame, clusters: list[int]) -> float:
    """
    (Opsional) Menghitung metrik evaluasi seperti Silhouette Score jika dibutuhkan nanti.
    Untuk saat ini, bisa direturn 0.0 atau metrik inertias dari model.
    """
    return 0.0

def cluster_summary(df_original: pd.DataFrame, clusters: list[int]) -> list[dict]:
    """
    Menghasilkan ringkasan cluster (rata-rata harga, rating, sold).
    df_original harus memiliki kolom dari SELECTED_FEATURES.
    """
    df = df_original.copy()
    df['cluster'] = clusters
    
    # Hitung rata-rata tiap fitur untuk tiap cluster
    summary_df = df.groupby('cluster')[SELECTED_FEATURES].mean().reset_index()
    
    # Beri label otomatis berdasarkan urutan harga rata-rata
    # Harga terendah = Budget, Menengah = Mid Range, Tertinggi = Premium
    summary_df = summary_df.sort_values(by='price', ascending=True).reset_index(drop=True)
    labels = ["Budget", "Mid Range", "Premium"]
    
    # Jika jumlah cluster kurang dari 3, pangkas labels
    if len(summary_df) < 3:
        labels = labels[:len(summary_df)]
        
    summary_df['label'] = labels
    
    # Convert ke dict
    results = []
    for _, row in summary_df.iterrows():
        cluster_id = int(row['cluster'])
        results.append({
            "cluster_id": cluster_id,
            "label": str(row['label']),
            "total_product": int(len(df[df['cluster'] == cluster_id])),
            "average_price": float(row['price']),
            "average_rating": float(row['rating']),
            "average_sold": float(row['sold'])
        })
        
    # Kembalikan dengan mengurutkan berdasarkan cluster_id
    results = sorted(results, key=lambda x: x['cluster_id'])
    return results
