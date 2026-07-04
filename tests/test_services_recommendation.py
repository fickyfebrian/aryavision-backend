from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.recommendation import get_cluster_label_map, get_recommendations


def query_returning_first(value) -> MagicMock:
    m = MagicMock()
    m.filter.return_value.first.return_value = value
    return m


def query_returning_all(value) -> MagicMock:
    m = MagicMock()
    m.filter.return_value.all.return_value = value
    return m


def query_cluster_avg(rows) -> MagicMock:
    m = MagicMock()
    m.filter.return_value.group_by.return_value.all.return_value = rows
    return m


class TestGetClusterLabelMap:
    def test_maps_clusters_ascending_by_price_to_named_labels(self, mock_db):
        mock_db.query.return_value = query_cluster_avg(
            [
                SimpleNamespace(cluster=2, avg_price=900000),
                SimpleNamespace(cluster=0, avg_price=100000),
                SimpleNamespace(cluster=1, avg_price=500000),
            ]
        )

        result = get_cluster_label_map(mock_db)

        assert result == {0: "Budget", 1: "Mid Range", 2: "Premium"}

    def test_more_than_three_clusters_get_generic_labels(self, mock_db):
        rows = [SimpleNamespace(cluster=i, avg_price=i * 100) for i in range(4)]
        mock_db.query.return_value = query_cluster_avg(rows)

        result = get_cluster_label_map(mock_db)

        assert result[3] == "Cluster 3"


class TestGetRecommendations:
    def test_raises_404_when_product_not_found(self, mock_db):
        mock_db.query.side_effect = [query_returning_first(None)]

        with pytest.raises(HTTPException) as exc_info:
            get_recommendations(mock_db, 999, 10)

        assert exc_info.value.status_code == 404

    def test_raises_400_when_product_has_no_cluster(self, mock_db, sample_product):
        sample_product.cluster = None
        mock_db.query.side_effect = [query_returning_first(sample_product)]

        with pytest.raises(HTTPException) as exc_info:
            get_recommendations(mock_db, sample_product.id, 10)

        assert exc_info.value.status_code == 400

    def test_raises_500_when_cbf_models_missing(self, mocker, mock_db, sample_product):
        mock_db.query.side_effect = [query_returning_first(sample_product)]
        mocker.patch(
            "app.services.recommendation.load_cbf_models",
            side_effect=FileNotFoundError,
        )

        with pytest.raises(HTTPException) as exc_info:
            get_recommendations(mock_db, sample_product.id, 10)

        assert exc_info.value.status_code == 500

    def test_raises_400_when_product_missing_from_index_with_no_duplicate(
        self, mocker, mock_db, sample_product
    ):
        mock_db.query.side_effect = [
            query_returning_first(sample_product),  # selected product lookup
            query_returning_first(None),  # duplicate lookup fails
        ]
        mocker.patch(
            "app.services.recommendation.load_cbf_models",
            return_value=(None, [[1.0]], {}),  # product_index empty
        )

        with pytest.raises(HTTPException) as exc_info:
            get_recommendations(mock_db, sample_product.id, 10)

        assert exc_info.value.status_code == 400

    def test_returns_empty_recommendations_when_alone_in_cluster(
        self, mocker, mock_db, sample_product
    ):
        mock_db.query.side_effect = [
            query_returning_first(sample_product),  # selected product lookup
            query_returning_all([sample_product]),  # cluster products: only itself
        ]
        mocker.patch(
            "app.services.recommendation.load_cbf_models",
            return_value=(None, [[1.0]], {sample_product.id: 0}),
        )

        result = get_recommendations(mock_db, sample_product.id, 10)

        assert result["recommendations"] == []
        assert result["total_recommendation"] == 0
        assert result["cluster"] is None

    def test_sorts_recommendations_by_similarity_descending_and_applies_limit(
        self, mocker, mock_db, sample_product, another_product
    ):
        third_product = SimpleNamespace(
            id=3, product_name="Low sim product", brand="X", price=100,
            rating=4.0, sold=1, cluster=0,
        )
        another_product.cluster = 0  # same cluster as sample_product

        sim_matrix = [
            [1.0, 0.2, 0.9],  # row for sample_product (idx 0)
            [0.2, 1.0, 0.1],
            [0.9, 0.1, 1.0],
        ]
        product_index = {sample_product.id: 0, another_product.id: 1, third_product.id: 2}

        mock_db.query.side_effect = [
            query_returning_first(sample_product),
            query_returning_all([sample_product, another_product, third_product]),
            query_cluster_avg([SimpleNamespace(cluster=0, avg_price=100000)]),
        ]
        mocker.patch(
            "app.services.recommendation.load_cbf_models",
            return_value=(None, sim_matrix, product_index),
        )

        result = get_recommendations(mock_db, sample_product.id, limit=1)

        assert result["total_recommendation"] == 1
        assert result["recommendations"][0]["id"] == third_product.id  # higher similarity (0.9) wins
        assert result["recommendations"][0]["similarity_score"] == 0.9
        assert result["cluster"] == "Budget"

    def test_falls_back_to_duplicate_match_when_id_missing_from_index(
        self, mocker, mock_db, sample_product, another_product
    ):
        another_product.cluster = sample_product.cluster
        duplicate = SimpleNamespace(
            id=99, product_name=sample_product.product_name, price=sample_product.price,
        )
        sim_matrix = [[1.0, 0.5], [0.5, 1.0]]
        product_index = {duplicate.id: 0, another_product.id: 1}

        mock_db.query.side_effect = [
            query_returning_first(sample_product),  # selected product lookup (id not in index)
            query_returning_first(duplicate),  # duplicate match lookup succeeds
            query_returning_all([sample_product, another_product]),  # cluster products
            query_cluster_avg([SimpleNamespace(cluster=sample_product.cluster, avg_price=100000)]),
        ]
        mocker.patch(
            "app.services.recommendation.load_cbf_models",
            return_value=(None, sim_matrix, product_index),
        )

        result = get_recommendations(mock_db, sample_product.id, limit=10)

        assert result["total_recommendation"] == 1
        assert result["recommendations"][0]["id"] == another_product.id
        assert result["recommendations"][0]["similarity_score"] == 0.5
