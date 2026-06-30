from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_ml_pipeline():
    print("Testing GET /api/ml/test...")
    response = client.get("/api/ml/test")
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_ml_pipeline()
