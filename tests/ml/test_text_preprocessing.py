import pandas as pd

from app.ml.text_preprocessing import clean_text, combine_text_features, preprocess_text


class TestCombineTextFeatures:
    def test_combines_available_text_columns(self):
        df = pd.DataFrame(
            {
                "product_name": ["EZVIZ C6N"],
                "brand": ["EZVIZ"],
                "category": ["Indoor"],
                "description": ["Kamera bagus"],
            }
        )

        result = combine_text_features(df)

        assert result["combined_text"].iloc[0] == "EZVIZ C6N EZVIZ Indoor Kamera bagus"

    def test_skips_null_columns(self):
        df = pd.DataFrame(
            {
                "product_name": ["EZVIZ C6N"],
                "brand": [None],
                "category": ["Indoor"],
                "description": [None],
            }
        )

        result = combine_text_features(df)

        assert result["combined_text"].iloc[0] == "EZVIZ C6N Indoor"

    def test_missing_optional_columns_do_not_crash(self):
        df = pd.DataFrame({"product_name": ["EZVIZ C6N"]})

        result = combine_text_features(df)

        assert result["combined_text"].iloc[0] == "EZVIZ C6N"


class TestCleanText:
    def test_lowercases_text(self):
        assert clean_text("EZVIZ Camera") == "ezviz camera"

    def test_removes_punctuation(self):
        assert clean_text("Kamera, CCTV! (Indoor)") == "kamera cctv indoor"

    def test_collapses_extra_whitespace(self):
        assert clean_text("kamera    cctv   indoor") == "kamera cctv indoor"

    def test_non_string_input_returns_empty_string(self):
        assert clean_text(None) == ""
        assert clean_text(123) == ""


class TestPreprocessText:
    def test_produces_clean_text_column(self):
        df = pd.DataFrame(
            {
                "product_name": ["EZVIZ, C6N!"],
                "brand": ["EZVIZ"],
                "category": [None],
                "description": [None],
            }
        )

        result = preprocess_text(df)

        assert result["clean_text"].iloc[0] == "ezviz c6n ezviz"
