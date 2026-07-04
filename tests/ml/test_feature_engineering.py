import pandas as pd
import pytest

from app.ml.feature_engineering import extract_cbf_features, extract_features


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            "price": [100000, 200000],
            "rating": [4.5, 3.8],
            "sold": [10, 20],
            "product_name": ["A", "B"],
        }
    )


class TestExtractFeatures:
    def test_returns_only_selected_features(self, df):
        result = extract_features(df)

        assert list(result.columns) == ["price"]
        assert len(result) == 2

    def test_raises_when_required_feature_missing(self):
        df_missing = pd.DataFrame({"rating": [4.5]})

        with pytest.raises(ValueError):
            extract_features(df_missing)

    def test_does_not_mutate_original_dataframe(self, df):
        original_columns = list(df.columns)
        extract_features(df)

        assert list(df.columns) == original_columns


class TestExtractCbfFeatures:
    def test_returns_price_rating_sold_columns(self, df):
        result = extract_cbf_features(df)

        assert list(result.columns) == ["price", "rating", "sold"]

    def test_raises_when_required_feature_missing(self):
        df_missing = pd.DataFrame({"price": [1], "rating": [1]})  # missing 'sold'

        with pytest.raises(ValueError):
            extract_cbf_features(df_missing)
