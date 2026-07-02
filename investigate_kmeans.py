import os
import joblib
import pandas as pd
from sqlalchemy import create_engine
from app.core.config import settings

def main():
    # 1. Hubungkan ke database
    engine = create_engine(settings.DATABASE_URL)
    
    # 2. Ambil data
    query = "SELECT id, product_name, price, rating, sold, cluster FROM products WHERE price IS NOT NULL"
    df = pd.read_sql(query, engine)
    
    # 3. Load Model K-Means dan Scaler
    from app.ml.kmeans import load_model, get_ordered_cluster_mapping
    from sklearn.preprocessing import MinMaxScaler
    
    model = load_model()
    
    # Karena scaler tidak disimpan ke disk (hanya fit-transform on the fly di API),
    # kita bisa membuat ulang scaler dan me-fit ke kolom yang sama.
    from app.ml.constants import SELECTED_FEATURES
    scaler = MinMaxScaler()
    scaler.fit(df[SELECTED_FEATURES])
    
    centers_scaled = model.cluster_centers_
    
    mapping = get_ordered_cluster_mapping(model)
    
    import numpy as np
    
    # Invers transformasi centroid untuk mendapatkan nilai aslinya
    # K-Means ditraining HANYA pada 'price' (karena SELECTED_FEATURES = ['price'] setelah update).
    # Namun mari kita pastikan.
    print(f"Scaler features count: {scaler.n_features_in_}")
    
    # Jika scaler hanya punya 1 fitur
    if scaler.n_features_in_ == 1:
        centers_real = scaler.inverse_transform(centers_scaled)
    else:
        # Jika scaler ternyata di-fit pada beberapa fitur, kita buat array dummy
        dummy = np.zeros((3, scaler.n_features_in_))
        dummy[:, 0] = centers_scaled[:, 0]
        centers_real = scaler.inverse_transform(dummy)[:, 0:1]

    print("\n--- 1. NILAI CENTROID & STATISTIK CLUSTER ---")
    for old_id, new_id in mapping.items():
        centroid_real = centers_real[old_id][0]
        cluster_df = df[df['cluster'] == new_id]
        if len(cluster_df) == 0:
            print(f"Cluster {new_id}: Kosong")
            continue
            
        mean_price = cluster_df['price'].mean()
        min_price = cluster_df['price'].min()
        max_price = cluster_df['price'].max()
        count = len(cluster_df)
        
        print(f"Cluster {new_id} ({'Budget' if new_id==0 else 'Mid Range' if new_id==1 else 'Premium'}):")
        print(f"  - KMeans Centroid: Rp {centroid_real:,.2f}")
        print(f"  - Jumlah Data    : {count}")
        print(f"  - Harga Min      : Rp {min_price:,.2f}")
        print(f"  - Harga Max      : Rp {max_price:,.2f}")
    
    print("\n--- 2. 10 HARGA TERTINGGI PADA CLUSTER 1 (MID RANGE) ---")
    mid_range_df = df[df['cluster'] == 1].sort_values(by='price', ascending=False).head(10)
    for idx, row in mid_range_df.iterrows():
        print(f"- {row['product_name'][:50]} : Rp {row['price']:,.2f} | Rating: {row['rating']} | Sold: {row['sold']}")
        
    print("\n--- 3. 10 HARGA TERENDAH PADA CLUSTER 2 (PREMIUM) ---")
    premium_df = df[df['cluster'] == 2].sort_values(by='price', ascending=True).head(10)
    for idx, row in premium_df.iterrows():
        print(f"- {row['product_name'][:50]} : Rp {row['price']:,.2f} | Rating: {row['rating']} | Sold: {row['sold']}")

if __name__ == "__main__":
    main()
