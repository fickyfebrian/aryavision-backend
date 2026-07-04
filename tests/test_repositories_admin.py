from unittest.mock import MagicMock

from app.core.security import verify_password
from app.models.admin import Admin
from app.repositories.admin import create_admin, get_admin_by_id, get_admin_by_username


class TestGetAdminByUsername:
    def test_returns_admin_when_found(self, mock_db: MagicMock, sample_admin: Admin):
        mock_db.query.return_value.filter.return_value.first.return_value = sample_admin

        result = get_admin_by_username(mock_db, "admin")

        assert result is sample_admin
        mock_db.query.assert_called_once_with(Admin)

    def test_returns_none_when_not_found(self, mock_db: MagicMock):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = get_admin_by_username(mock_db, "ghost")

        assert result is None


class TestGetAdminById:
    def test_returns_admin_when_found(self, mock_db: MagicMock, sample_admin: Admin):
        mock_db.query.return_value.filter.return_value.first.return_value = sample_admin

        result = get_admin_by_id(mock_db, 1)

        assert result is sample_admin

    def test_returns_none_when_not_found(self, mock_db: MagicMock):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = get_admin_by_id(mock_db, 999)

        assert result is None


class TestCreateAdmin:
    def test_hashes_password_before_persisting(self, mock_db: MagicMock):
        created = create_admin(mock_db, "newadmin", "plain-password")

        assert created.username == "newadmin"
        assert created.password != "plain-password"
        assert verify_password("plain-password", created.password)

    def test_persists_via_session(self, mock_db: MagicMock):
        created = create_admin(mock_db, "newadmin", "plain-password")

        mock_db.add.assert_called_once_with(created)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(created)
