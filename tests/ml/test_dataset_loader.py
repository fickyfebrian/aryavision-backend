from unittest.mock import MagicMock

import pandas as pd

from app.ml.dataset_loader import load_dataset_from_db


class TestLoadDatasetFromDb:
    def test_reads_sql_using_session_statement_and_bind(self, mocker, mock_db):
        expected_df = pd.DataFrame({"id": [1, 2], "price": [1000, 2000]})
        fake_statement = "SELECT * FROM products"
        mock_db.query.return_value.statement = fake_statement
        mock_db.bind = MagicMock()
        read_sql = mocker.patch("app.ml.dataset_loader.pd.read_sql", return_value=expected_df)

        result = load_dataset_from_db(mock_db)

        read_sql.assert_called_once_with(fake_statement, mock_db.bind)
        pd.testing.assert_frame_equal(result, expected_df)
