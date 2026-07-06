import os
import joblib
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity
from typing import Tuple, Any

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "similarity_matrix.pkl")
INDEX_MAPPING_PATH = os.path.join(MODEL_DIR, "product_index.pkl")

def train_cbf(df_features: pd.DataFrame, product_ids: list[int]) -> Tuple[Any, dict]:
    """
    Membangun model Content-Based Filtering dari dataframe numerik.
    Menghasilkan:
    1. Cosine Similarity matrix
    2. Product Index mapping (product_id -> matrix index)
    """
    # 1. Hitung Cosine Similarity langsung dari fitur numerik
    sim_matrix = cosine_similarity(df_features, df_features)
    
    # 2. Buat Mapping Index
    # product_id -> index of matrix
    product_index = {product_id: idx for idx, product_id in enumerate(product_ids)}
    
    return sim_matrix, product_index

def save_cbf_models(sim_matrix: Any, product_index: dict) -> None:
    """
    Menyimpan Similarity Matrix dan Product Index ke disk.
    """
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    joblib.dump(sim_matrix, SIMILARITY_PATH)
    joblib.dump(product_index, INDEX_MAPPING_PATH)
    
def load_cbf_models() -> Tuple[Any, dict]:
    """
    Memuat Similarity Matrix dan Product Index dari disk.
    """
    if not os.path.exists(SIMILARITY_PATH) or not os.path.exists(INDEX_MAPPING_PATH):
        raise FileNotFoundError("One or more CBF model files not found. Please train CBF first.")
        
    sim_matrix = joblib.load(SIMILARITY_PATH)
    product_index = joblib.load(INDEX_MAPPING_PATH)
    
    return sim_matrix, product_index
