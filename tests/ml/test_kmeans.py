import os

import pandas as pd
import pytest

from app.ml import kmeans as kmeans_module
from app.ml.kmeans import (
    cluster_summary,
    get_ordered_cluster_mapping,
    load_model,
    predict_cluster,
    save_model,
    train_model,
)


@pytest.fixture
def isolated_model_path(tmp_path, monkeypatch):
    """Redirect model persistence to a temp dir so tests never touch app/ml/models/."""
    model_dir = tmp_path / "models"
    model_path = model_dir / "kmeans_model.pkl"
    monkeypatch.setattr(kmeans_module, "MODEL_DIR", str(model_dir))
    monkeypatch.setattr(kmeans_module, "MODEL_PATH", str(model_path))
    return model_path


@pytest.fixture
def separated_features_df():
    return pd.DataFrame(
        {
            "price": [0.0, 0.01, 0.02, 1.0, 0.99, 0.98, 0.5, 0.51, 0.49],
        }
    )


class TestTrainModel:
    def test_produces_requested_number_of_clusters(self, separated_features_df):
        model = train_model(separated_features_df, n_clusters=3)

        assert len(set(model.labels_)) == 3

    def test_is_deterministic_given_fixed_random_state(self, separated_features_df):
        model_a = train_model(separated_features_df, n_clusters=3)
        model_b = train_model(separated_features_df, n_clusters=3)

        assert list(model_a.labels_) == list(model_b.labels_)


class TestGetOrderedClusterMapping:
    def test_maps_lowest_centroid_to_zero(self, separated_features_df):
        model = train_model(separated_features_df, n_clusters=3)

        mapping = get_ordered_cluster_mapping(model)
        centers = model.cluster_centers_[:, 0]
        lowest_original_cluster = centers.argmin()

        assert mapping[lowest_original_cluster] == 0

    def test_mapping_is_a_bijection_over_all_clusters(self, separated_features_df):
        model = train_model(separated_features_df, n_clusters=3)

        mapping = get_ordered_cluster_mapping(model)

        assert sorted(mapping.values()) == [0, 1, 2]


class TestPredictCluster:
    def test_relabels_so_budget_products_get_lowest_cluster_id(self, separated_features_df):
        model = train_model(separated_features_df, n_clusters=3)

        clusters = predict_cluster(model, separated_features_df)
        cheapest_row_cluster = clusters[0]  # price=0.0, the cheapest row

        assert cheapest_row_cluster == 0


class TestSaveAndLoadModel:
    def test_round_trips_model_to_disk(self, isolated_model_path, separated_features_df):
        model = train_model(separated_features_df, n_clusters=3)

        save_model(model)
        assert os.path.exists(isolated_model_path)

        loaded = load_model()
        assert list(loaded.predict(separated_features_df)) == list(model.predict(separated_features_df))

    def test_load_missing_model_raises_file_not_found(self, isolated_model_path):
        with pytest.raises(FileNotFoundError):
            load_model()


class TestClusterSummary:
    def test_summarizes_average_features_per_cluster(self):
        df_original = pd.DataFrame(
            {
                "price": [100000, 200000, 900000, 950000],
                "rating": [4.0, 4.2, 4.8, 4.9],
                "sold": [10, 20, 5, 7],
            }
        )
        clusters = [0, 0, 1, 1]

        summary = cluster_summary(df_original, clusters)

        assert len(summary) == 2
        budget = next(s for s in summary if s["cluster_id"] == 0)
        assert budget["label"] == "Budget"
        assert budget["total_product"] == 2
        assert budget["average_price"] == pytest.approx(150000.0)

    def test_results_sorted_by_cluster_id(self):
        df_original = pd.DataFrame({"price": [1, 2, 3], "rating": [1, 2, 3], "sold": [1, 2, 3]})
        clusters = [2, 0, 1]

        summary = cluster_summary(df_original, clusters)

        assert [s["cluster_id"] for s in summary] == [0, 1, 2]
