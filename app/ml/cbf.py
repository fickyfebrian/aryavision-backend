import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Tuple, Any

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
TFIDF_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
SIMILARITY_PATH = os.path.join(MODEL_DIR, "similarity_matrix.pkl")
INDEX_MAPPING_PATH = os.path.join(MODEL_DIR, "product_index.pkl")

def train_cbf(df: pd.DataFrame) -> Tuple[TfidfVectorizer, Any, dict]:
    """
    Membangun model Content-Based Filtering dari dataframe teks bersih.
    Menghasilkan:
    1. TfidfVectorizer object
    2. Cosine Similarity matrix
    3. Product Index mapping (product_id -> matrix index)
    """
    # Pastikan dataframe memiliki kolom clean_text dan id
    if 'clean_text' not in df.columns or 'id' not in df.columns:
        raise ValueError("DataFrame must contain 'clean_text' and 'id' columns.")
        
    texts = df['clean_text'].tolist()
    product_ids = df['id'].tolist()
    
    # 1. Bangun TF-IDF
    vectorizer = TfidfVectorizer(max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # 2. Hitung Cosine Similarity
    sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # 3. Buat Mapping Index
    # product_id -> index of matrix
    product_index = {product_id: idx for idx, product_id in enumerate(product_ids)}
    
    return vectorizer, sim_matrix, product_index

def save_cbf_models(vectorizer: TfidfVectorizer, sim_matrix: Any, product_index: dict) -> None:
    """
    Menyimpan model TF-IDF, Similarity Matrix, dan Product Index ke disk.
    """
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    joblib.dump(vectorizer, TFIDF_PATH)
    joblib.dump(sim_matrix, SIMILARITY_PATH)
    joblib.dump(product_index, INDEX_MAPPING_PATH)
    
def load_cbf_models() -> Tuple[TfidfVectorizer, Any, dict]:
    """
    Memuat model TF-IDF, Similarity Matrix, dan Product Index dari disk.
    """
    if not os.path.exists(TFIDF_PATH) or not os.path.exists(SIMILARITY_PATH) or not os.path.exists(INDEX_MAPPING_PATH):
        raise FileNotFoundError("One or more CBF model files not found. Please train CBF first.")
        
    vectorizer = joblib.load(TFIDF_PATH)
    sim_matrix = joblib.load(SIMILARITY_PATH)
    product_index = joblib.load(INDEX_MAPPING_PATH)
    
    return vectorizer, sim_matrix, product_index
