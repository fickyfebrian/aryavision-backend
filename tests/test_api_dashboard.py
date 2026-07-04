from unittest.mock import MagicMock

from app.api.dashboard import get_product_service as get_dashboard_service_dep
from main import app


class TestGetDashboardStats:
    def test_returns_statistics_from_service(self, client):
        service = MagicMock()
        service.get_dashboard_statistics.return_value = {
            "total_products": 120,
            "total_brands": 8,
            "budget_cluster": 40,
            "mid_range_cluster": 50,
            "premium_cluster": 30,
        }
        app.dependency_overrides[get_dashboard_service_dep] = lambda: service

        response = client.get("/api/dashboard/stats")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["total_products"] == 120
        assert body["success"] is True
