import pandas as pd
import string
import re

def combine_text_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menggabungkan informasi produk menjadi satu dokumen teks.
    Hanya menggabungkan kolom product_name, brand, category, description jika ada/tidak null.
    """
    df_text = df.copy()
    
    # Definisikan kolom teks
    text_columns = ['product_name', 'brand', 'category', 'description']
    
    # Isi NaN dengan string kosong
    for col in text_columns:
        if col in df_text.columns:
            df_text[col] = df_text[col].fillna('')
            
    # Gabungkan kolom menjadi satu string yang dipisahkan dengan spasi
    def combine_row(row):
        words = []
        for col in text_columns:
            if col in row.index and isinstance(row[col], str) and row[col].strip():
                words.append(row[col].strip())
        return " ".join(words)
        
    df_text['combined_text'] = df_text.apply(combine_row, axis=1)
    
    return df_text

def clean_text(text: str) -> str:
    """
    Membersihkan teks:
    - lowercase
    - remove punctuation
    - remove extra whitespace
    """
    if not isinstance(text, str):
        return ""
        
    # 1. Lowercase
    text = text.lower()
    
    # 2. Remove punctuation
    # Mengganti tanda baca dengan spasi agar tidak menggabungkan kata
    text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    
    # 3. Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def preprocess_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Wrapper untuk menggabungkan teks dan membersihkannya.
    """
    df_combined = combine_text_features(df)
    df_combined['clean_text'] = df_combined['combined_text'].apply(clean_text)
    return df_combined
