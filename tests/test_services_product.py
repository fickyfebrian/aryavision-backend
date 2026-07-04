from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product import ProductService


@pytest.fixture
def mock_repository(mocker) -> MagicMock:
    """
    ProductService builds its own ProductRepository(db) internally, so we patch
    the class at the point it's looked up in app.services.product to isolate
    ProductService's own logic from repository internals (already covered by
    tests/test_repositories_product.py).
    """
    repo_cls = mocker.patch("app.services.product.ProductRepository")
    repo_instance = MagicMock()
    repo_cls.return_value = repo_instance
    return repo_instance


class TestGetProducts:
    def test_delegates_to_repository_with_computed_skip(self, mock_db, mock_repository):
        mock_repository.find_all.return_value = ([], 0)

        ProductService(mock_db).get_products(page=3, limit=10)

        mock_repository.find_all.assert_called_once()
        assert mock_repository.find_all.call_args.kwargs["skip"] == 20
        assert mock_repository.find_all.call_args.kwargs["limit"] == 10

    def test_page_below_one_is_clamped_to_one(self, mock_db, mock_repository):
        mock_repository.find_all.return_value = ([], 0)

        ProductService(mock_db).get_products(page=0, limit=10)

        assert mock_repository.find_all.call_args.kwargs["skip"] == 0

    def test_limit_below_one_defaults_to_twenty(self, mock_db, mock_repository):
        mock_repository.find_all.return_value = ([], 0)

        ProductService(mock_db).get_products(page=1, limit=0)

        assert mock_repository.find_all.call_args.kwargs["limit"] == 20

    def test_returns_items_and_total_from_repository(self, mock_db, mock_repository, sample_product):
        mock_repository.find_all.return_value = ([sample_product], 1)

        items, total = ProductService(mock_db).get_products()

        assert items == [sample_product]
        assert total == 1


class TestGetProductById:
    def test_returns_product_when_found(self, mock_db, mock_repository, sample_product):
        mock_repository.find_by_id.return_value = sample_product

        result = ProductService(mock_db).get_product_by_id(1)

        assert result is sample_product

    def test_raises_404_when_not_found(self, mock_db, mock_repository):
        mock_repository.find_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            ProductService(mock_db).get_product_by_id(999)

        assert exc_info.value.status_code == 404


class TestCreateProduct:
    def test_delegates_to_repository(self, mock_db, mock_repository, sample_product):
        mock_repository.create.return_value = sample_product
        product_in = ProductCreate(product_name="New CCTV", price=100000)

        result = ProductService(mock_db).create_product(product_in)

        mock_repository.create.assert_called_once_with(product_in)
        assert result is sample_product


class TestUpdateProduct:
    def test_raises_404_when_product_missing(self, mock_db, mock_repository):
        mock_repository.find_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            ProductService(mock_db).update_product(999, ProductUpdate(price=1000))

        assert exc_info.value.status_code == 404
        mock_repository.update.assert_not_called()

    def test_updates_when_product_exists(self, mock_db, mock_repository, sample_product):
        mock_repository.find_by_id.return_value = sample_product
        mock_repository.update.return_value = sample_product
        update_in = ProductUpdate(price=999000)

        result = ProductService(mock_db).update_product(1, update_in)

        mock_repository.update.assert_called_once_with(sample_product, update_in)
        assert result is sample_product


class TestDeleteProduct:
    def test_raises_404_when_product_missing(self, mock_db, mock_repository):
        mock_repository.find_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            ProductService(mock_db).delete_product(999)

        assert exc_info.value.status_code == 404
        mock_repository.delete.assert_not_called()

    def test_deletes_when_product_exists(self, mock_db, mock_repository, sample_product):
        mock_repository.find_by_id.return_value = sample_product

        ProductService(mock_db).delete_product(1)

        mock_repository.delete.assert_called_once_with(sample_product)


class TestGetDashboardStatistics:
    def test_delegates_to_repository(self, mock_db, mock_repository):
        stats = {"total_products": 10}
        mock_repository.get_dashboard_statistics.return_value = stats

        result = ProductService(mock_db).get_dashboard_statistics()

        assert result is stats
