import pytest
from fastapi import HTTPException
from jose import jwt

from app.api.deps import get_current_admin
from app.core.config import settings
from app.core.security import create_access_token


def make_token(**claims) -> str:
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


class TestGetCurrentAdmin:
    def test_returns_admin_for_valid_token(self, mock_db, sample_admin):
        mock_db.query.return_value.filter.return_value.first.return_value = sample_admin
        token = create_access_token(data={"sub": str(sample_admin.id)})

        result = get_current_admin(token=token, db=mock_db)

        assert result is sample_admin

    def test_raises_401_for_malformed_token(self, mock_db):
        with pytest.raises(HTTPException) as exc_info:
            get_current_admin(token="not-a-real-token", db=mock_db)

        assert exc_info.value.status_code == 401

    def test_raises_401_when_sub_claim_missing(self, mock_db):
        token = make_token(foo="bar")

        with pytest.raises(HTTPException) as exc_info:
            get_current_admin(token=token, db=mock_db)

        assert exc_info.value.status_code == 401

    def test_raises_401_when_sub_is_not_an_integer(self, mock_db):
        token = make_token(sub="not-an-int")

        with pytest.raises(HTTPException) as exc_info:
            get_current_admin(token=token, db=mock_db)

        assert exc_info.value.status_code == 401

    def test_raises_401_when_admin_no_longer_exists(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        token = create_access_token(data={"sub": "999"})

        with pytest.raises(HTTPException) as exc_info:
            get_current_admin(token=token, db=mock_db)

        assert exc_info.value.status_code == 401

    def test_raises_401_when_signed_with_wrong_secret(self, mock_db):
        token = jwt.encode({"sub": "1"}, "wrong-secret", algorithm=settings.ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            get_current_admin(token=token, db=mock_db)

        assert exc_info.value.status_code == 401
