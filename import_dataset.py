import re
from sqlalchemy import text
from app.database.connection import engine


def clean_price(price_str):
    if not price_str or price_str.strip() == '' or price_str == 'Harga':
        return 0
    # Extract only digits
    digits = re.sub(r'\D', '', price_str)
    return int(digits) if digits else 0

def clean_sold(sold_str):
    if not sold_str or sold_str.strip() == '' or sold_str == 'Popularitas':
        return 0
    
    sold_str = sold_str.lower()
    
    # Extract numbers and potential 'rb' multiplier
    match = re.search(r'([\d\.]+)\s*(rb)?', sold_str)
    if not match:
        return 0
        
    num_part = match.group(1)
    is_rb = match.group(2) == 'rb'
    
    try:
        num = float(num_part)
        if is_rb:
            num *= 1000
        return int(num)
    except ValueError:
        return 0

def clean_rating(rating_str):
    if not rating_str or rating_str.strip() == '' or rating_str == 'Rating':
        return None
    try:
        return float(rating_str)
    except ValueError:
        return None

def extract_brand(name_str):
    if not name_str:
        return None
    # Usually the first word is the brand (e.g., EZVIZ, HIKVISION, DAHUA, TAPO, BARDION)
    first_word = name_str.split(' ')[0].upper()
    return first_word

def run_import():
    try:
        with engine.connect() as conn:
            # 1. Fetch raw data
            result = conn.execute(text("SELECT * FROM raw_products"))
            raw_data = result.mappings().all()
            
            successful_imports = 0
            failed_imports = 0
            
            for row in raw_data:
                product_url = row.get('Link Produk')
                image_url = row.get('Gambar')
                product_name = row.get('Nama')
                price_raw = str(row.get('Harga') or '')
                rating_raw = str(row.get('Rating') or '')
                sold_raw = str(row.get('Popularitas') or '')
                
                # Skip header row if exists
                if product_name == 'Nama' or not product_name:
                    continue
                    
                try:
                    # Preprocess data
                    price = clean_price(price_raw)
                    rating = clean_rating(rating_raw)
                    sold = clean_sold(sold_raw)
                    brand = extract_brand(product_name)
                    
                    # 2. Insert into new table
                    sql = text("""
                        INSERT INTO products 
                        (product_name, product_url, image_url, brand, price, rating, sold) 
                        VALUES (:name, :url, :image, :brand, :price, :rating, :sold)
                    """)
                    conn.execute(sql, {
                        "name": product_name,
                        "url": product_url,
                        "image": image_url,
                        "brand": brand,
                        "price": price,
                        "rating": rating,
                        "sold": sold
                    })
                    successful_imports += 1
                except Exception as e:
                    print(f"Failed to process row: {product_name} - Error: {e}")
                    failed_imports += 1
            
            # Commit changes
            conn.commit()
            
            print(f"Import completed.")
            print(f"Successful imports: {successful_imports}")
            print(f"Failed imports: {failed_imports}")
            
            # Show some sample data from the new table
            print("\n--- Sample Processed Data ---")
            sample_result = conn.execute(text("SELECT id, product_name, brand, price, rating, sold FROM products LIMIT 3"))
            for sample in sample_result.mappings().all():
                print(f"ID: {sample['id']} | Brand: {sample['brand']} | Price: Rp{sample['price']} | Rating: {sample['rating']} | Sold: {sample['sold']}")
                print(f"Name: {sample['product_name']}\n")
                
    except Exception as e:
        print(f"Failed to connect or process database: {e}")

if __name__ == "__main__":
    run_import()
