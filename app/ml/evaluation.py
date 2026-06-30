import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import warnings

def calculate_elbow(df_scaled: pd.DataFrame, max_k: int = 10) -> list[dict]:
    """
    Menghitung inertia untuk metode Elbow dengan variasi K = 2 sampai max_k.
    """
    elbow_data = []
    # Mengabaikan warning memory leak KMeans di Windows untuk dataset kecil
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for k in range(2, max_k + 1):
            model = KMeans(n_clusters=k, random_state=42, n_init="auto")
            model.fit(df_scaled)
            elbow_data.append({
                "k": k,
                "inertia": float(model.inertia_)
            })
    return elbow_data

def calculate_silhouette(df_scaled: pd.DataFrame, max_k: int = 10) -> list[dict]:
    """
    Menghitung Silhouette Score untuk variasi K = 2 sampai max_k.
    """
    silhouette_data = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for k in range(2, max_k + 1):
            model = KMeans(n_clusters=k, random_state=42, n_init="auto")
            labels = model.fit_predict(df_scaled)
            score = silhouette_score(df_scaled, labels)
            silhouette_data.append({
                "k": k,
                "score": float(score)
            })
    return silhouette_data
