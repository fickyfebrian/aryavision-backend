from datetime import timedelta

from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password


class TestPasswordHashing:
    def test_hash_is_not_equal_to_plain_password(self):
        hashed = get_password_hash("secret123")
        assert hashed != "secret123"

    def test_verify_password_succeeds_with_correct_password(self):
        hashed = get_password_hash("secret123")
        assert verify_password("secret123", hashed) is True

    def test_verify_password_fails_with_wrong_password(self):
        hashed = get_password_hash("secret123")
        assert verify_password("wrong-password", hashed) is False

    def test_hashing_same_password_twice_yields_different_hashes(self):
        # bcrypt salts each hash, so two hashes of the same password must differ
        assert get_password_hash("secret123") != get_password_hash("secret123")


class TestAccessToken:
    def test_token_contains_provided_claims(self):
        token = create_access_token(data={"sub": "1"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "1"
        assert "exp" in payload

    def test_token_respects_custom_expiry(self):
        token = create_access_token(data={"sub": "1"}, expires_delta=timedelta(minutes=5))
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in payload

    def test_token_is_decodable_only_with_correct_secret(self):
        token = create_access_token(data={"sub": "1"})
        try:
            jwt.decode(token, "wrong-secret-key", algorithms=[settings.ALGORITHM])
            assert False, "decoding with the wrong secret should have raised"
        except jwt.JWTError:
            pass
