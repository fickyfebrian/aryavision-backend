import pandas as pd
from typing import Tuple

def clean_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Menjalankan seluruh pipeline preprocessing secara berurutan dan mengembalikan
    dataframe bersih beserta statistik penghapusan data.
    
    Langkah:
    1. Hapus duplicate product
    2. Hapus data dengan price <= 0 (atau null)
    3. Isi data rating yang kosong dengan 0
    4. Isi data sold yang kosong dengan 0
    """
    stats = {
        "total_before": len(df),
        "duplicate_removed": 0,
        "rating_removed": 0,
        "sold_removed": 0,
        "price_removed": 0,
        "total_after": 0
    }
    
    current_df = df.copy()
    
    # 1. Pastikan tipe data numerik
    numeric_columns = ['price', 'rating', 'sold']
    for col in numeric_columns:
        if col in current_df.columns:
            current_df[col] = pd.to_numeric(current_df[col], errors='coerce')
            
    # 2. Hapus duplikat berdasarkan product_name dan price
    initial_len = len(current_df)
    if 'product_name' in current_df.columns and 'price' in current_df.columns:
        current_df = current_df.drop_duplicates(subset=['product_name', 'price'])
    stats["duplicate_removed"] = initial_len - len(current_df)
    
    # 3. Hapus price <= 0 atau null
    initial_len = len(current_df)
    if 'price' in current_df.columns:
        current_df = current_df[current_df['price'] > 0]
    stats["price_removed"] = initial_len - len(current_df)
    
    # 4. Isi rating yang kosong atau negatif dengan 0
    initial_len = len(current_df)
    if 'rating' in current_df.columns:
        current_df['rating'] = current_df['rating'].fillna(0)
        current_df.loc[current_df['rating'] < 0, 'rating'] = 0
    stats["rating_removed"] = 0
    
    # 5. Isi sold yang kosong atau negatif dengan 0
    initial_len = len(current_df)
    if 'sold' in current_df.columns:
        current_df['sold'] = current_df['sold'].fillna(0)
        current_df.loc[current_df['sold'] < 0, 'sold'] = 0
    stats["sold_removed"] = 0
    
    # Reset index
    current_df = current_df.reset_index(drop=True)
    stats["total_after"] = len(current_df)
    
    return current_df, stats

def prepare_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Wrapper untuk clean_dataset agar konsisten dengan struktur sebelumnya.
    """
    return clean_dataset(df)
