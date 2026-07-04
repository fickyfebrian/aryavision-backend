from unittest.mock import MagicMock

from fastapi import HTTPException

from app.api.product import get_product_service as get_product_service_dep
from main import app


def override_product_service(client, fake_service):
    app.dependency_overrides[get_product_service_dep] = lambda: fake_service


class TestGetProducts:
    def test_returns_paginated_items(self, client, sample_product):
        service = MagicMock()
        service.get_products.return_value = ([sample_product], 1)
        override_product_service(client, service)

        response = client.get("/api/products?page=1&limit=20")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["pagination"]["total_items"] == 1
        assert body["data"]["items"][0]["product_name"] == sample_product.product_name

    def test_forwards_query_params_to_service(self, client, sample_product):
        service = MagicMock()
        service.get_products.return_value = ([sample_product], 1)
        override_product_service(client, service)

        client.get(
            "/api/products"
            "?page=2&limit=5&search=EZVIZ&cluster=0&min_price=1000&max_price=5000"
            "&min_rating=3&max_rating=5&sort=price&order=desc"
        )

        service.get_products.assert_called_once_with(
            page=2,
            limit=5,
            search="EZVIZ",
            cluster=0,
            min_price=1000,
            max_price=5000,
            min_rating=3.0,
            max_rating=5.0,
            sort_by="price",
            order="desc",
        )

    def test_rejects_limit_above_100(self, client):
        service = MagicMock()
        override_product_service(client, service)

        response = client.get("/api/products?limit=1000")

        assert response.status_code == 422


class TestGetProductById:
    def test_returns_product_when_found(self, client, sample_product):
        service = MagicMock()
        service.get_product_by_id.return_value = sample_product
        override_product_service(client, service)

        response = client.get(f"/api/products/{sample_product.id}")

        assert response.status_code == 200
        assert response.json()["data"]["id"] == sample_product.id

    def test_returns_404_when_not_found(self, client):
        service = MagicMock()
        service.get_product_by_id.side_effect = HTTPException(status_code=404, detail="Product with ID 999 not found")
        override_product_service(client, service)

        response = client.get("/api/products/999")

        assert response.status_code == 404
        assert response.json()["success"] is False


class TestCreateProduct:
    def test_creates_and_returns_201(self, client, sample_product):
        service = MagicMock()
        service.create_product.return_value = sample_product
        override_product_service(client, service)

        response = client.post(
            "/api/products",
            json={"product_name": "New CCTV", "price": 100000},
        )

        assert response.status_code == 201
        assert response.json()["data"]["product_name"] == sample_product.product_name

    def test_rejects_missing_required_field(self, client):
        service = MagicMock()
        override_product_service(client, service)

        response = client.post("/api/products", json={"price": 100000})

        assert response.status_code == 422

    def test_rejects_negative_price(self, client):
        service = MagicMock()
        override_product_service(client, service)

        response = client.post("/api/products", json={"product_name": "X", "price": -1})

        assert response.status_code == 422

    def test_rejects_rating_above_five(self, client):
        service = MagicMock()
        override_product_service(client, service)

        response = client.post(
            "/api/products", json={"product_name": "X", "price": 1, "rating": 5.5}
        )

        assert response.status_code == 422


class TestUpdateProduct:
    def test_updates_and_returns_product(self, client, sample_product):
        service = MagicMock()
        service.update_product.return_value = sample_product
        override_product_service(client, service)

        response = client.put(f"/api/products/{sample_product.id}", json={"price": 999000})

        assert response.status_code == 200
        service.update_product.assert_called_once()

    def test_returns_404_when_not_found(self, client):
        service = MagicMock()
        service.update_product.side_effect = HTTPException(status_code=404, detail="not found")
        override_product_service(client, service)

        response = client.put("/api/products/999", json={"price": 1000})

        assert response.status_code == 404


class TestDeleteProduct:
    def test_deletes_successfully(self, client, sample_product):
        service = MagicMock()
        service.delete_product.return_value = None
        override_product_service(client, service)

        response = client.delete(f"/api/products/{sample_product.id}")

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_returns_404_when_not_found(self, client):
        service = MagicMock()
        service.delete_product.side_effect = HTTPException(status_code=404, detail="not found")
        override_product_service(client, service)

        response = client.delete("/api/products/999")

        assert response.status_code == 404
