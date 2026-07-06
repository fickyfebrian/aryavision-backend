"""
Shared pytest fixtures.

Testing strategy: no real database or network connections are made anywhere
in this suite. All SQLAlchemy Session usage is replaced with MagicMock, and
the FastAPI TestClient is instantiated without the `with` context manager so
that the app's lifespan (which pings the real Supabase DB) never runs.
"""
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.admin import Admin
from app.models.product import Product


@pytest.fixture
def mock_db() -> MagicMock:
    """A MagicMock standing in for a SQLAlchemy Session. Never touches a real DB."""
    return MagicMock(spec=Session)


@pytest.fixture
def sample_admin() -> Admin:
    admin = Admin(username="admin", password=get_password_hash("secret123"))
    admin.id = 1
    admin.created_at = datetime(2026, 1, 1)
    admin.updated_at = datetime(2026, 1, 1)
    return admin


@pytest.fixture
def sample_product() -> Product:
    product = Product(
        product_name="EZVIZ C6N Indoor CCTV",
        product_url="https://aryavision.com/products/ezviz-c6n",
        image_url="https://aryavision.com/images/ezviz-c6n.jpg",
        brand="EZVIZ",
        category="Indoor",
        price=350000,
        rating=4.5,
        sold=120,
        description="Kamera CCTV indoor dengan resolusi 1080p",
        cluster=0,
    )
    product.id = 1
    product.created_at = datetime(2026, 1, 1)
    product.updated_at = datetime(2026, 1, 1)
    return product


@pytest.fixture
def another_product() -> Product:
    product = Product(
        product_name="Hikvision DS-2CE Outdoor CCTV",
        brand="Hikvision",
        category="Outdoor",
        price=750000,
        rating=4.7,
        sold=80,
        description="Kamera CCTV outdoor tahan cuaca",
        cluster=1,
    )
    product.id = 2
    product.created_at = datetime(2026, 1, 1)
    product.updated_at = datetime(2026, 1, 1)
    return product


@pytest.fixture
def client():
    """
    FastAPI TestClient. Deliberately NOT used as a context manager so that
    the app's `lifespan` (which calls check_database_connection against the
    real Supabase instance) never executes.
    """
    from main import app

    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()
