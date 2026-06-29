from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def print_res(res, title):
    print(f"\n--- {title} ---")
    print(f"Status Code: {res.status_code}")
    try:
        print(json.dumps(res.json(), indent=2))
    except Exception as e:
        print(res.text)

def run_tests():
    # 1. Create Product
    new_product = {
        "product_name": "Test Camera",
        "price": 500000,
        "rating": 4.5,
        "sold": 10
    }
    res_create = client.post("/api/products", json=new_product)
    print_res(res_create, "Create Product")

    created_id = res_create.json().get('data', {}).get('id')
    if not created_id:
        print("Failed to extract created_id, tests will fail")
        exit(1)

    # 2. Update Product
    update_data = {
        "price": 550000,
        "rating": 4.8
    }
    res_update = client.put(f"/api/products/{created_id}", json=update_data)
    print_res(res_update, "Update Product")

    # 3. Get Product by ID
    res_get = client.get(f"/api/products/{created_id}")
    print_res(res_get, "Get Product by ID")

    # 4. Search & Pagination & Sorting
    res_search = client.get(f"/api/products?page=1&limit=5&search=EZVIZ&sort=price&order=desc")
    print_res(res_search, "Search, Pagination, and Sorting")

    # 5. Delete Product
    res_delete = client.delete(f"/api/products/{created_id}")
    print_res(res_delete, "Delete Product")

    # 6. Verify Deletion
    res_verify = client.get(f"/api/products/{created_id}")
    print_res(res_verify, "Verify Deletion (Should be 404)")

if __name__ == "__main__":
    run_tests()
