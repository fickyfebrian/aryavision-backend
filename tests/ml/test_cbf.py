import os

import pandas as pd
import pytest

from app.ml import cbf as cbf_module
from app.ml.cbf import load_cbf_models, save_cbf_models, train_cbf


@pytest.fixture
def isolated_model_paths(tmp_path, monkeypatch):
    model_dir = tmp_path / "models"
    monkeypatch.setattr(cbf_module, "MODEL_DIR", str(model_dir))
    monkeypatch.setattr(cbf_module, "TFIDF_PATH", str(model_dir / "tfidf_vectorizer.pkl"))
    monkeypatch.setattr(cbf_module, "SIMILARITY_PATH", str(model_dir / "similarity_matrix.pkl"))
    monkeypatch.setattr(cbf_module, "INDEX_MAPPING_PATH", str(model_dir / "product_index.pkl"))
    return model_dir


@pytest.fixture
def features_df():
    return pd.DataFrame({"price": [100000, 100000, 900000], "rating": [4.5, 4.5, 3.0], "sold": [10, 10, 1]})


class TestTrainCbf:
    def test_similarity_matrix_is_square_and_matches_product_count(self, features_df):
        _, sim_matrix, product_index = train_cbf(features_df, product_ids=[1, 2, 3])

        assert sim_matrix.shape == (3, 3)
        assert product_index == {1: 0, 2: 1, 3: 2}

    def test_identical_feature_rows_have_similarity_one(self, features_df):
        _, sim_matrix, _ = train_cbf(features_df, product_ids=[1, 2, 3])

        # rows 0 and 1 have identical price/rating/sold
        assert sim_matrix[0][1] == pytest.approx(1.0)

    def test_diagonal_is_self_similarity_one(self, features_df):
        _, sim_matrix, _ = train_cbf(features_df, product_ids=[1, 2, 3])

        for i in range(3):
            assert sim_matrix[i][i] == pytest.approx(1.0)


class TestSaveAndLoadCbfModels:
    def test_round_trips_to_disk(self, isolated_model_paths, features_df):
        vectorizer, sim_matrix, product_index = train_cbf(features_df, product_ids=[1, 2, 3])

        save_cbf_models(vectorizer, sim_matrix, product_index)
        assert os.path.exists(cbf_module.SIMILARITY_PATH)

        loaded_vectorizer, loaded_sim_matrix, loaded_index = load_cbf_models()

        assert loaded_vectorizer is None
        assert loaded_index == product_index
        assert (loaded_sim_matrix == sim_matrix).all()

    def test_load_missing_models_raises_file_not_found(self, isolated_model_paths):
        with pytest.raises(FileNotFoundError):
            load_cbf_models()
