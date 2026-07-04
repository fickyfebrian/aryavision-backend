from unittest.mock import MagicMock

from fastapi import HTTPException

from app.database.connection import get_db
from main import app


class TestRecommendProducts:
    def test_returns_recommendations_payload(self, client, mocker):
        app.dependency_overrides[get_db] = lambda: MagicMock()
        fake_result = {
            "selected_product": {"id": 1},
            "cluster": "Budget",
            "total_recommendation": 1,
            "recommendations": [{"id": 2, "similarity_score": 0.9}],
        }
        mocker.patch("app.api.recommendation.get_recommendations", return_value=fake_result)

        response = client.get("/api/recommendations/1")

        assert response.status_code == 200
        assert response.json()["data"] == fake_result

    def test_forwards_limit_query_param(self, client, mocker):
        app.dependency_overrides[get_db] = lambda: MagicMock()
        mock_get_recs = mocker.patch(
            "app.api.recommendation.get_recommendations",
            return_value={"selected_product": {}, "cluster": None, "total_recommendation": 0, "recommendations": []},
        )

        client.get("/api/recommendations/1?limit=5")

        args, _ = mock_get_recs.call_args
        assert args[1] == 1
        assert args[2] == 5

    def test_returns_404_when_product_missing(self, client, mocker):
        app.dependency_overrides[get_db] = lambda: MagicMock()
        mocker.patch(
            "app.api.recommendation.get_recommendations",
            side_effect=HTTPException(status_code=404, detail="Product with ID 999 not found."),
        )

        response = client.get("/api/recommendations/999")

        assert response.status_code == 404

    def test_rejects_limit_above_fifty(self, client):
        response = client.get("/api/recommendations/1?limit=1000")

        assert response.status_code == 422
