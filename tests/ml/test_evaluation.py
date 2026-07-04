import pandas as pd
import pytest

from app.ml.evaluation import calculate_elbow, calculate_silhouette


@pytest.fixture
def well_separated_df():
    # Two tight, clearly separated blobs so clustering metrics are well-defined.
    return pd.DataFrame(
        {
            "price": [0.0, 0.01, 0.02, 1.0, 0.99, 0.98],
            "rating": [0.0, 0.01, 0.02, 1.0, 0.99, 0.98],
        }
    )


class TestCalculateElbow:
    def test_returns_one_entry_per_k(self, well_separated_df):
        result = calculate_elbow(well_separated_df, max_k=4)

        assert [entry["k"] for entry in result] == [2, 3, 4]

    def test_inertia_is_non_negative(self, well_separated_df):
        result = calculate_elbow(well_separated_df, max_k=3)

        assert all(entry["inertia"] >= 0 for entry in result)

    def test_inertia_decreases_as_k_increases(self, well_separated_df):
        result = calculate_elbow(well_separated_df, max_k=4)

        inertias = [entry["inertia"] for entry in result]
        assert inertias == sorted(inertias, reverse=True)


class TestCalculateSilhouette:
    def test_returns_one_entry_per_k(self, well_separated_df):
        result = calculate_silhouette(well_separated_df, max_k=4)

        assert [entry["k"] for entry in result] == [2, 3, 4]

    def test_score_is_within_valid_range(self, well_separated_df):
        result = calculate_silhouette(well_separated_df, max_k=3)

        assert all(-1.0 <= entry["score"] <= 1.0 for entry in result)

    def test_two_clear_clusters_scores_highest_at_k_equals_two(self, well_separated_df):
        result = calculate_silhouette(well_separated_df, max_k=4)

        best = max(result, key=lambda entry: entry["score"])
        assert best["k"] == 2
