from unittest.mock import MagicMock

from app.database.connection import check_database_connection


class TestCheckDatabaseConnection:
    def test_returns_true_when_engine_connects(self, mocker):
        fake_connection = MagicMock()
        fake_connection.__enter__.return_value = fake_connection
        mocker.patch("app.database.connection.engine.connect", return_value=fake_connection)

        assert check_database_connection() is True

    def test_returns_false_when_engine_raises(self, mocker):
        mocker.patch("app.database.connection.engine.connect", side_effect=Exception("network down"))

        assert check_database_connection() is False
