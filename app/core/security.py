"""
Modul Security — JWT & Password Hashing.

File ini adalah pondasi untuk authentication yang akan diimplementasi nanti.
Saat ini berisi:
- Password hashing dengan bcrypt (via Passlib)
- JWT token creation & verification (via python-jose)

Akan digunakan di Tahap 3 (JWT Login Admin).
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Context untuk hashing password menggunakan bcrypt
# bcrypt adalah algoritma yang direkomendasikan karena lambat secara desain
# sehingga tahan terhadap brute-force attack
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password menggunakan bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi password plain dengan hash yang tersimpan di database."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Membuat JWT Access Token.

    Args:
        data: Payload yang akan di-encode ke dalam token (biasanya berisi user ID).
        expires_delta: Durasi token berlaku. Default dari settings jika None.

    Returns:
        JWT token string yang siap dikirim ke client.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode dan verifikasi JWT Access Token.

    Returns:
        Payload dict jika token valid, None jika tidak valid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
