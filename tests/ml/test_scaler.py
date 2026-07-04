import pandas as pd
import pytest

from app.ml.scaler import min_max_scaler, standard_scaler


@pytest.fixture
def df():
    return pd.DataFrame({"price": [100000, 200000, 300000, 400000, 500000]})


class TestStandardScaler:
    def test_result_has_zero_mean(self, df):
        result = standard_scaler(df)

        assert result["price"].mean() == pytest.approx(0.0, abs=1e-9)

    def test_result_has_unit_population_variance(self, df):
        result = standard_scaler(df)

        assert result["price"].std(ddof=0) == pytest.approx(1.0, abs=1e-9)

    def test_preserves_columns_and_index(self, df):
        result = standard_scaler(df)

        assert list(result.columns) == list(df.columns)
        assert list(result.index) == list(df.index)


class TestMinMaxScaler:
    def test_result_is_bounded_between_zero_and_one(self, df):
        result = min_max_scaler(df)

        assert result["price"].min() == pytest.approx(0.0)
        assert result["price"].max() == pytest.approx(1.0)

    def test_preserves_relative_order(self, df):
        result = min_max_scaler(df)

        assert result["price"].is_monotonic_increasing

    def test_constant_column_does_not_produce_nan(self):
        constant_df = pd.DataFrame({"price": [100, 100, 100]})

        result = min_max_scaler(constant_df)

        assert not result["price"].isna().any()
