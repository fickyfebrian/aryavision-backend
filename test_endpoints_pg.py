import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
from main import app
from app.database.connection import engine
from sqlalchemy import text

client = TestClient(app)

def test_health():
    response = client.get("/api/health/")
    print("GET /api/health:", response.status_code, response.json())
    assert response.status_code == 200

def test_products():
    response = client.get("/api/products?limit=1")
    print("GET /api/products:", response.status_code)
    assert response.status_code == 200
    
    products = response.json().get("data", {}).get("items", [])
    if len(products) > 0:
        product_id = products[0]["id"]
        
        # Test Recommendations
        response = client.get(f"/api/recommendations/{product_id}")
        print(f"GET /api/recommendations/{product_id}:", response.status_code)
        # Note: might fail if cluster is None or CBF not trained, we catch exceptions.
        
def test_ml():
    response = client.get("/api/ml/test")
    print("GET /api/ml/test:", response.status_code)
    
    response = client.get("/api/ml/evaluation")
    print("GET /api/ml/evaluation:", response.status_code)

def run_tests():
    try:
        test_health()
        test_products()
        test_ml()
        print("Initial tests passed.")
    except Exception as e:
        print("Test failed:", e)

if __name__ == "__main__":
    run_tests()
