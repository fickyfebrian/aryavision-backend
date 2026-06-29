from fastapi.testclient import TestClient
from main import app
import traceback

client = TestClient(app)

def test():
    try:
        new_product = {
            "product_name": "Test Camera",
            "price": 500000,
            "rating": 4.5,
            "sold": 10
        }
        print("Sending POST request...")
        response = client.post("/api/products", json=new_product)
        print("Status code:", response.status_code)
        print("Response body:", response.json())
    except Exception as e:
        print("Got exception during request:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
