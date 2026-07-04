class TestHealthCheck:
    def test_returns_healthy_when_database_connected(self, client, mocker):
        mocker.patch("app.api.health.check_database_connection", return_value=True)

        response = client.get("/api/health/")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["status"] == "healthy"
        assert body["data"]["database"] == "connected"

    def test_returns_503_when_database_disconnected(self, client, mocker):
        mocker.patch("app.api.health.check_database_connection", return_value=False)

        response = client.get("/api/health/")

        assert response.status_code == 503
        body = response.json()
        assert body["success"] is False
        assert body["errors"]["database"] == "disconnected"
