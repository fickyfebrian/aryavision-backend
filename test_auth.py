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
    print("Testing Authentication Engine...")
    
    # 1. Test Login (Form Data for OAuth2 compatibility)
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    # Send as form data
    res_login = client.post("/api/auth/login", data=login_data)
    print_res(res_login, "Login (Form Data)")
    
    if res_login.status_code == 200:
        token = res_login.json()["data"]["access_token"]
        
        # 2. Test Get Me
        headers = {
            "Authorization": f"Bearer {token}"
        }
        res_me = client.get("/api/auth/me", headers=headers)
        print_res(res_me, "Get Current Admin (/api/auth/me)")
        
        # 3. Test Invalid Token
        res_invalid = client.get("/api/auth/me", headers={"Authorization": "Bearer invalidtoken123"})
        print_res(res_invalid, "Invalid Token (/api/auth/me)")
        
    else:
        print("Login failed, skipping /me test")
        
if __name__ == "__main__":
    run_tests()
