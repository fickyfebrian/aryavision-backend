from fastapi import HTTPException

from app.api.deps import get_current_admin
from app.schemas.auth import TokenResponse
from main import app


class TestLoginForm:
    def test_returns_access_token_on_success(self, client, mocker):
        mocker.patch(
            "app.api.auth.authenticate_admin",
            return_value=TokenResponse(access_token="fake-token", token_type="bearer"),
        )

        response = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "secret123"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["access_token"] == "fake-token"
        assert body["data"]["token_type"] == "bearer"

    def test_returns_401_on_invalid_credentials(self, client, mocker):
        mocker.patch(
            "app.api.auth.authenticate_admin",
            side_effect=HTTPException(status_code=401, detail="Incorrect username or password"),
        )

        response = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "wrong"},
        )

        assert response.status_code == 401
        assert response.json()["success"] is False


class TestLoginJson:
    def test_returns_access_token_on_success(self, client, mocker):
        mocker.patch(
            "app.api.auth.authenticate_admin",
            return_value=TokenResponse(access_token="fake-token", token_type="bearer"),
        )

        response = client.post(
            "/api/auth/login/json",
            json={"username": "admin", "password": "secret123"},
        )

        assert response.status_code == 200
        assert response.json()["data"]["access_token"] == "fake-token"

    def test_rejects_missing_fields_with_422(self, client):
        response = client.post("/api/auth/login/json", json={"username": "admin"})

        assert response.status_code == 422
        assert response.json()["success"] is False


class TestGetMe:
    def test_returns_current_admin_profile(self, client, sample_admin):
        app.dependency_overrides[get_current_admin] = lambda: sample_admin

        response = client.get("/api/auth/me")

        assert response.status_code == 200
        body = response.json()
        assert body["data"] == {"id": sample_admin.id, "username": sample_admin.username}

    def test_requires_authentication(self, client):
        response = client.get("/api/auth/me")

        assert response.status_code == 401
