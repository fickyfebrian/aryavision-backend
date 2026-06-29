import re
import pymysql

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
    conn = pymysql.connect(
        host='localhost', 
        user='root', 
        password='', 
        database='skripsi_cctv', 
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with conn.cursor() as cursor:
            # 1. Fetch raw data
            cursor.execute("SELECT * FROM produk")
            raw_data = cursor.fetchall()
            
            successful_imports = 0
            failed_imports = 0
            
            for row in raw_data:
                product_url = row.get('COL 1')
                image_url = row.get('COL 2')
                product_name = row.get('COL 3')
                price_raw = row.get('COL 4')
                rating_raw = row.get('COL 6')
                sold_raw = row.get('COL 7')
                
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
                    sql = """
                        INSERT INTO products 
                        (product_name, product_url, image_url, brand, price, rating, sold) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        product_name,
                        product_url,
                        image_url,
                        brand,
                        price,
                        rating,
                        sold
                    ))
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
            cursor.execute("SELECT id, product_name, brand, price, rating, sold FROM products LIMIT 3")
            for sample in cursor.fetchall():
                print(f"ID: {sample['id']} | Brand: {sample['brand']} | Price: Rp{sample['price']} | Rating: {sample['rating']} | Sold: {sample['sold']}")
                print(f"Name: {sample['product_name']}\n")
                
    finally:
        conn.close()

if __name__ == "__main__":
    run_import()
