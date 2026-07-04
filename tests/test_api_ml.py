from unittest.mock import MagicMock

import pandas as pd
import pytest

from app.database.connection import get_db
from main import app


@pytest.fixture(autouse=True)
def override_db():
    mock_session = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_session
    yield mock_session


@pytest.fixture
def small_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6],
            "product_name": ["A", "B", "C", "D", "E", "F"],
            "brand": ["EZVIZ", "EZVIZ", "Hikvision", "Hikvision", "Xiaomi", "Xiaomi"],
            "category": ["Indoor"] * 6,
            "description": ["desc"] * 6,
            "price": [100000, 120000, 300000, 320000, 900000, 950000],
            "rating": [4.0, 4.2, 4.3, 4.1, 4.8, 4.9],
            "sold": [10, 20, 15, 5, 3, 7],
        }
    )


class TestMlPipelineTest:
    def test_returns_400_when_dataset_empty(self, client, mocker):
        mocker.patch("app.api.ml.load_dataset_from_db", return_value=pd.DataFrame())

        response = client.get("/api/ml/test")

        assert response.status_code == 400

    def test_returns_stats_and_selected_features(self, client, mocker, small_dataset):
        mocker.patch("app.api.ml.load_dataset_from_db", return_value=small_dataset)

        response = client.get("/api/ml/test")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["selected_features"] == ["price"]
        assert data["total_after"] == 6


class TestRunClustering:
    def test_returns_400_when_dataset_empty(self, client, mocker):
        mocker.patch("app.api.ml.load_dataset_from_db", return_value=pd.DataFrame())

        response = client.get("/api/ml/clustering")

        assert response.status_code == 400

    def test_trains_and_persists_clusters(self, client, mocker, small_dataset, override_db):
        mocker.patch("app.api.ml.load_dataset_from_db", return_value=small_dataset)
        mocker.patch("app.api.ml.save_model")  # avoid writing a real model file
        override_db.query.return_value.filter.return_value.all.return_value = []  # no unclustered rows

        response = client.get("/api/ml/clustering")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total_product_processed"] == 6
        assert data["total_clusters"] == 3
        assert sum(data["distribution"].values()) == 6
        override_db.commit.assert_called()

    def test_synchronizes_unclustered_duplicates_with_matching_product(
        self, client, mocker, small_dataset, override_db
    ):
        mocker.patch("app.api.ml.load_dataset_from_db", return_value=small_dataset)
        mocker.patch("app.api.ml.save_model")

        duplicate = MagicMock(product_name="A", price=100000, cluster=None)
        matched = MagicMock(product_name="A", price=100000, cluster=0)
        override_db.query.return_value.filter.return_value.all.return_value = [duplicate]
        override_db.query.return_value.filter.return_value.first.return_value = matched

        response = client.get("/api/ml/clustering")

        assert response.status_code == 200
        assert duplicate.cluster == 0  # synced from the matching clustered product


class TestGetClusters:
    def test_returns_400_when_dataset_empty(self, client, mocker):
        mocker.patch("app.api.ml.load_dataset_from_db", return_value=pd.DataFrame())

        response = client.get("/api/ml/clusters")

        assert response.status_code == 400

    def test_returns_404_when_model_not_trained_yet(self, client, mocker, small_dataset):
        mocker.patch("app.api.ml.load_dataset_from_db", return_value=small_dataset)
        mocker.patch("app.api.ml.load_model", side_effect=FileNotFoundError)

        response = client.get("/api/ml/clusters")

        assert response.status_code == 404

    def test_returns_cluster_summary_when_model_exists(self, client, mocker, small_dataset):
        mocker.patch("app.api.ml.load_dataset_from_db", return_value=small_dataset)
        mocker.patch("app.api.ml.load_model", return_value=MagicMock())
        mocker.patch("app.api.ml.predict_cluster", return_value=[0, 0, 1, 1, 2, 2])

        response = client.get("/api/ml/clusters")

        assert response.status_code == 200
        summary = response.json()["data"]
        assert len(summary) == 3
        assert {c["label"] for c in summary} == {"Budget", "Mid Range", "Premium"}


class TestEvaluateKmeans:
    def test_returns_400_when_dataset_empty(self, client, mocker):
        mocker.patch("app.api.ml.load_dataset_from_db", return_value=pd.DataFrame())

        response = client.get("/api/ml/evaluation")

        assert response.status_code == 400

    def test_returns_recommended_k_from_best_silhouette_score(self, client, mocker, small_dataset):
        mocker.patch("app.api.ml.load_dataset_from_db", return_value=small_dataset)
        mocker.patch("app.api.ml.calculate_elbow", return_value=[{"k": 2, "inertia": 10.0}])
        mocker.patch(
            "app.api.ml.calculate_silhouette",
            return_value=[{"k": 2, "score": 0.4}, {"k": 3, "score": 0.7}],
        )

        response = client.get("/api/ml/evaluation")

        assert response.status_code == 200
        assert response.json()["data"]["recommended_k"] == 3


class TestCbfEngineTest:
    def test_returns_400_when_dataset_empty(self, client, mocker):
        mocker.patch("app.api.ml.load_dataset_from_db", return_value=pd.DataFrame())

        response = client.get("/api/ml/cbf/test")

        assert response.status_code == 400

    def test_builds_similarity_matrix(self, client, mocker, small_dataset):
        mocker.patch("app.api.ml.load_dataset_from_db", return_value=small_dataset)
        mocker.patch("app.api.ml.save_cbf_models")  # avoid writing real model files

        response = client.get("/api/ml/cbf/test")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total_products"] == 6
        assert data["similarity_shape"] == [6, 6]
