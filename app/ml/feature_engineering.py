import pandas as pd
from app.ml.constants import SELECTED_FEATURES, CBF_FEATURES

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mengekstrak fitur yang relevan untuk proses Machine Learning.
    Hanya mengembalikan kolom-kolom yang didefinisikan pada SELECTED_FEATURES.
    """
    # Pastikan semua fitur yang dibutuhkan ada pada dataframe
    missing_features = [f for f in SELECTED_FEATURES if f not in df.columns]
    if missing_features:
        raise ValueError(f"Missing features in dataset: {missing_features}")
        
    features_df = df[SELECTED_FEATURES].copy()
    return features_df

def extract_cbf_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mengekstrak fitur yang relevan untuk proses Content-Based Filtering.
    """
    missing_features = [f for f in CBF_FEATURES if f not in df.columns]
    if missing_features:
        raise ValueError(f"Missing features in dataset: {missing_features}")
        
    features_df = df[CBF_FEATURES].copy()
    return features_df
