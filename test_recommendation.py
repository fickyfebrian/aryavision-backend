from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def print_res(res, title):
    print(f"\n--- {title} ---")
    print(f"Status Code: {res.status_code}")
    try:
        print(json.dumps(res.json(), indent=2))
    except Exception:
        print(res.text)

def run_tests():
    print("Testing Recommendation Engine...")
    
    # Let's search for products to test with using /api/products endpoint
    # 1. Search EZVIZ
    res_ezviz = client.get("/api/products", params={"search": "EZVIZ", "limit": 1})
    ezviz_id = res_ezviz.json()["data"]["items"][0]["id"] if res_ezviz.status_code == 200 and res_ezviz.json()["data"]["items"] else None
    
    # 2. Search HIKVISION
    res_hikvision = client.get("/api/products", params={"search": "HIKVISION", "limit": 1})
    hikvision_id = res_hikvision.json()["data"]["items"][0]["id"] if res_hikvision.status_code == 200 and res_hikvision.json()["data"]["items"] else None
    
    # 3. Search DAHUA
    res_dahua = client.get("/api/products", params={"search": "DAHUA", "limit": 1})
    dahua_id = res_dahua.json()["data"]["items"][0]["id"] if res_dahua.status_code == 200 and res_dahua.json()["data"]["items"] else None
    
    # Get Recommendations
    if ezviz_id:
        res = client.get(f"/api/recommendations/{ezviz_id}")
        print_res(res, f"Recommendation for EZVIZ (ID: {ezviz_id})")
        
    if hikvision_id:
        res = client.get(f"/api/recommendations/{hikvision_id}")
        print_res(res, f"Recommendation for HIKVISION (ID: {hikvision_id})")
        
    if dahua_id:
        res = client.get(f"/api/recommendations/{dahua_id}")
        print_res(res, f"Recommendation for DAHUA (ID: {dahua_id})")

if __name__ == "__main__":
    run_tests()
