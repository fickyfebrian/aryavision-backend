import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from app.middlewares.exception_handler import register_exception_handlers


class Payload(BaseModel):
    name: str


@pytest.fixture
def handler_client():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/http-error")
    def raise_http_error():
        raise HTTPException(status_code=404, detail="Not found here")

    @app.post("/validate")
    def validate_payload(payload: Payload):
        return {"ok": True}

    @app.get("/db-error")
    def raise_db_error():
        raise SQLAlchemyError("connection lost")

    @app.get("/boom")
    def raise_generic_error():
        raise ValueError("something broke")

    # The base `Exception` handler is wired into Starlette's ServerErrorMiddleware,
    # which always re-raises after invoking the handler so real servers can log it.
    # raise_server_exceptions=False lets the test observe the JSON response instead.
    return TestClient(app, raise_server_exceptions=False)


class TestHttpExceptionHandler:
    def test_preserves_status_code_and_formats_message(self, handler_client):
        response = handler_client.get("/http-error")

        assert response.status_code == 404
        body = response.json()
        assert body == {"success": False, "message": "Not found here", "errors": None}


class TestValidationExceptionHandler:
    def test_returns_422_with_field_level_errors(self, handler_client):
        response = handler_client.post("/validate", json={})

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["errors"][0]["field"] == "name"


class TestSqlAlchemyExceptionHandler:
    def test_returns_500_and_hides_details(self, handler_client):
        response = handler_client.get("/db-error")

        assert response.status_code == 500
        body = response.json()
        assert body["success"] is False
        assert "connection lost" not in body["message"]


class TestGenericExceptionHandler:
    def test_returns_500_and_hides_details(self, handler_client):
        response = handler_client.get("/boom")

        assert response.status_code == 500
        body = response.json()
        assert body["success"] is False
        assert "something broke" not in body["message"]
