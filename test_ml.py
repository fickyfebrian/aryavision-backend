from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_ml_pipeline():
    print("Running Clustering...")
    response = client.get("/api/ml/clustering")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    print("\nRunning CBF Engine...")
    response = client.get("/api/ml/cbf/test")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_ml_pipeline()
