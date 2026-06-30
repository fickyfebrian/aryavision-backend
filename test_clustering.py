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
    print("Testing Clustering Pipeline...")
    
    # 1. Run Clustering
    res_clustering = client.get("/api/ml/clustering")
    print_res(res_clustering, "Run Clustering")
    
    # 2. Get Clusters Summary
    res_summary = client.get("/api/ml/clusters")
    print_res(res_summary, "Clusters Summary")
    
if __name__ == "__main__":
    run_tests()
