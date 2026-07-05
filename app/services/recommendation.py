from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.product import Product
from app.ml.cbf import load_cbf_models

def get_cluster_label_map(db: Session) -> dict:
    """
    Menghitung ulang label cluster berdasarkan rata-rata harga di database.
    Mengembalikan mapping {cluster_id: 'Label'}
    """
    cluster_avg = db.query(
        Product.cluster, 
        func.avg(Product.price).label('avg_price')
    ).filter(Product.cluster.isnot(None)).group_by(Product.cluster).all()
    
    sorted_clusters = sorted(cluster_avg, key=lambda x: x.avg_price)
    labels = ["Budget", "Mid Range", "Premium"]
    
    cluster_map = {}
    for i, c in enumerate(sorted_clusters):
        if i < len(labels):
            cluster_map[c.cluster] = labels[i]
        else:
            cluster_map[c.cluster] = f"Cluster {c.cluster}"
            
    return cluster_map

def get_recommendations(db: Session, product_id: int, limit: int = 10):
    """
    Menghasilkan rekomendasi top-N berdasarkan hybrid:
    1. Filter berdasarkan cluster (K-Means)
    2. Urutkan berdasarkan kemiripan teks (CBF)
    """
    # 1. Pastikan produk ada
    selected_product = db.query(Product).filter(Product.id == product_id).first()
    if not selected_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )
        
    if selected_product.cluster is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with ID {product_id} does not have a cluster assigned. Please run ML clustering."
        )

    # 2. Load ML Models
    try:
        vectorizer, sim_matrix, product_index = load_cbf_models()
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CBF Models not found. Please train the CBF engine first."
        )
        
    if product_id not in product_index:
        # Fallback for products eliminated during preprocessing (e.g. duplicates)
        match = db.query(Product).filter(
            Product.id.in_(list(product_index.keys())),
            Product.product_name == selected_product.product_name,
            Product.price == selected_product.price
        ).first()
        
        if match:
            target_idx = product_index[match.id]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with ID {product_id} was not included in the CBF training (possibly eliminated during preprocessing)."
            )
    else:
        target_idx = product_index[product_id]
    sim_scores = sim_matrix[target_idx]
    
    # 3. Ambil semua produk di cluster yang sama
    target_cluster = selected_product.cluster
    cluster_products = db.query(Product).filter(Product.cluster == target_cluster).all()
    
    if len(cluster_products) <= 1:
        # Hanya ada dirinya sendiri di cluster ini
        return {
            "selected_product": selected_product,
            "cluster": None,
            "total_recommendation": 0,
            "recommendations": []
        }
        
    # 4. Filter similarity score hanya untuk produk di cluster yang sama
    candidates = []
    for p in cluster_products:
        if p.id != product_id and p.id in product_index:
            idx = product_index[p.id]
            score = sim_scores[idx]
            candidates.append((p, score))
            
    # 5. Urutkan berdasarkan similarity (descending) dan ambil top N
    candidates.sort(key=lambda x: x[1], reverse=True)
    top_candidates = candidates[:limit]
    
    # 6. Format hasil
    cluster_labels = get_cluster_label_map(db)
    cluster_label = cluster_labels.get(target_cluster, str(target_cluster))
    
    recommendations = []
    for p, score in top_candidates:
        recommendations.append({
            "id": p.id,
            "product_name": p.product_name,
            "brand": p.brand,
            "price": p.price,
            "rating": p.rating,
            "sold": p.sold,
            "image_url": p.image_url,
            "product_url": p.product_url,
            "cluster": cluster_label,
            "similarity_score": round(float(score), 4)
        })
        
    # Format selected product
    selected_product_dict = {
        "id": selected_product.id,
        "product_name": selected_product.product_name,
        "brand": selected_product.brand,
        "price": selected_product.price,
        "rating": selected_product.rating,
        "sold": selected_product.sold,
        "image_url": selected_product.image_url,
        "product_url": selected_product.product_url,
        "cluster": cluster_label
    }
        
    return {
        "selected_product": selected_product_dict,
        "cluster": cluster_label,
        "total_recommendation": len(recommendations),
        "recommendations": recommendations
    }
