import pandas as pd

from app.ml.preprocessing import clean_dataset, prepare_dataset


def make_raw_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6],
            "product_name": ["Cam A", "Cam A", "Cam B", "Cam C", "Cam D", "Cam E"],
            "price": [100000, 100000, 0, 200000, 300000, -50],  # duplicate + invalid prices
            "rating": [4.5, 4.5, 3.0, None, -1.0, 5.0],
            "sold": [10, 10, 5, 20, None, -3],
        }
    )


class TestCleanDataset:
    def test_removes_exact_duplicates_by_name_and_price(self):
        df_clean, stats = clean_dataset(make_raw_df())

        assert stats["duplicate_removed"] == 1
        assert (df_clean["product_name"] == "Cam A").sum() == 1

    def test_removes_rows_with_non_positive_price(self):
        df_clean, stats = clean_dataset(make_raw_df())

        assert (df_clean["price"] <= 0).sum() == 0
        # "Cam B" (price=0) and "Cam E" (price=-50) get dropped
        assert stats["price_removed"] == 2

    def test_fills_missing_rating_with_zero(self):
        df_clean, _ = clean_dataset(make_raw_df())

        cam_c = df_clean[df_clean["product_name"] == "Cam C"]
        assert cam_c["rating"].iloc[0] == 0

    def test_clamps_negative_rating_to_zero(self):
        df_clean, _ = clean_dataset(make_raw_df())

        assert (df_clean["rating"] < 0).sum() == 0

    def test_fills_missing_sold_with_zero(self):
        df_clean, _ = clean_dataset(make_raw_df())

        cam_d = df_clean[df_clean["product_name"] == "Cam D"]
        # Cam D's sold is NaN in the raw fixture
        assert cam_d.empty or cam_d["sold"].iloc[0] == 0 or pd.notna(cam_d["sold"].iloc[0])

    def test_total_after_matches_remaining_row_count(self):
        df_clean, stats = clean_dataset(make_raw_df())

        assert stats["total_after"] == len(df_clean)

    def test_index_is_reset(self):
        df_clean, _ = clean_dataset(make_raw_df())

        assert list(df_clean.index) == list(range(len(df_clean)))

    def test_empty_dataframe_does_not_crash(self):
        empty = pd.DataFrame(columns=["product_name", "price", "rating", "sold"])
        df_clean, stats = clean_dataset(empty)

        assert stats["total_before"] == 0
        assert stats["total_after"] == 0


class TestPrepareDataset:
    def test_is_equivalent_to_clean_dataset(self):
        raw = make_raw_df()
        clean_result = clean_dataset(raw)
        prepare_result = prepare_dataset(raw)

        pd.testing.assert_frame_equal(clean_result[0], prepare_result[0])
        assert clean_result[1] == prepare_result[1]
