import pandas as pd

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Membersihkan dataset dari nilai yang tidak valid (contoh: harga negatif, dll).
    """
    cleaned_df = df.copy()
    
    # Pastikan tipe data sesuai (contoh: konversi numerik jika belum)
    numeric_columns = ['price', 'rating', 'sold']
    for col in numeric_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
            
    # Hapus row yang harganya negatif
    if 'price' in cleaned_df.columns:
        cleaned_df = cleaned_df[cleaned_df['price'] >= 0]
        
    return cleaned_df

def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mengisi missing values pada dataset.
    - rating: isi dengan 0 jika null
    - sold: isi dengan 0 jika null
    """
    filled_df = df.copy()
    
    if 'rating' in filled_df.columns:
        filled_df['rating'] = filled_df['rating'].fillna(0)
        
    if 'sold' in filled_df.columns:
        filled_df['sold'] = filled_df['sold'].fillna(0)
        
    # Untuk fitur teks, isi dengan string kosong
    text_columns = ['product_name', 'brand', 'category', 'description']
    for col in text_columns:
        if col in filled_df.columns:
            filled_df[col] = filled_df[col].fillna('')
            
    return filled_df

def remove_duplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghapus data duplikat berdasarkan product_name dan price.
    """
    dedup_df = df.copy()
    if 'product_name' in dedup_df.columns and 'price' in dedup_df.columns:
        dedup_df = dedup_df.drop_duplicates(subset=['product_name', 'price'])
    return dedup_df

def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menjalankan seluruh pipeline preprocessing secara berurutan.
    """
    df = clean_dataset(df)
    df = fill_missing_values(df)
    df = remove_duplicate(df)
    
    # Reset index setelah drop rows
    df = df.reset_index(drop=True)
    return df
