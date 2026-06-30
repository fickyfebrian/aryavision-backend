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
    print("Testing ML Pipeline & Evaluation...")
    
    # 1. Test Preprocessing Pipeline
    res_test = client.get("/api/ml/test")
    print_res(res_test, "Test Pipeline (Stats)")
    
    # 2. Run Clustering
    res_clustering = client.get("/api/ml/clustering")
    print_res(res_clustering, "Run Clustering")
    
    # 3. Get Clusters Summary
    res_summary = client.get("/api/ml/clusters")
    print_res(res_summary, "Clusters Summary")
    
    # 4. Evaluation
    res_evaluation = client.get("/api/ml/evaluation")
    print_res(res_evaluation, "KMeans Evaluation")
    
    # 5. Test CBF Engine
    res_cbf = client.get("/api/ml/cbf/test")
    print_res(res_cbf, "Content-Based Filtering Engine")
    
if __name__ == "__main__":
    run_tests()
