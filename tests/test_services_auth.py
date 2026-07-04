from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.core.security import verify_password
from app.schemas.auth import LoginRequest
from app.services.auth import authenticate_admin


class TestAuthenticateAdmin:
    def test_returns_bearer_token_on_success(self, mock_db: MagicMock, sample_admin):
        mock_db.query.return_value.filter.return_value.first.return_value = sample_admin

        result = authenticate_admin(mock_db, LoginRequest(username="admin", password="secret123"))

        assert result.token_type == "bearer"
        assert result.access_token

    def test_raises_401_when_admin_not_found(self, mock_db: MagicMock):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            authenticate_admin(mock_db, LoginRequest(username="ghost", password="whatever"))

        assert exc_info.value.status_code == 401

    def test_raises_401_when_password_incorrect(self, mock_db: MagicMock, sample_admin):
        mock_db.query.return_value.filter.return_value.first.return_value = sample_admin

        with pytest.raises(HTTPException) as exc_info:
            authenticate_admin(mock_db, LoginRequest(username="admin", password="wrong-password"))

        assert exc_info.value.status_code == 401

    def test_token_subject_is_admin_id(self, mock_db: MagicMock, sample_admin):
        from jose import jwt
        from app.core.config import settings

        mock_db.query.return_value.filter.return_value.first.return_value = sample_admin

        result = authenticate_admin(mock_db, LoginRequest(username="admin", password="secret123"))
        payload = jwt.decode(result.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload["sub"] == str(sample_admin.id)
