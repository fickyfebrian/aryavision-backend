from unittest.mock import MagicMock

import pytest

from app.models.product import Product
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


def make_chained_query(**terminal_returns) -> MagicMock:
    """
    Build a query mock where .filter()/.order_by() return the query itself,
    so every call in a fluent chain lands on the same mock object and its
    call counts can be asserted directly.
    """
    query = MagicMock()
    query.filter.return_value = query
    query.order_by.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query
    for name, value in terminal_returns.items():
        setattr(getattr(query, name), "return_value", value)
    return query


class TestFindAll:
    def test_no_filters_applies_no_filter_calls(self, mock_db: MagicMock, sample_product):
        query = make_chained_query(count=1, all=[sample_product])
        mock_db.query.return_value = query
        repo = ProductRepository(mock_db)

        items, total = repo.find_all()

        mock_db.query.assert_called_once_with(Product)
        assert query.filter.call_count == 0
        assert query.order_by.call_count == 0
        assert items == [sample_product]
        assert total == 1

    def test_all_filters_are_applied(self, mock_db: MagicMock):
        query = make_chained_query(count=0, all=[])
        mock_db.query.return_value = query
        repo = ProductRepository(mock_db)

        repo.find_all(
            search="EZVIZ",
            cluster=0,
            min_price=100000,
            max_price=500000,
            min_rating=3.0,
            max_rating=4.5,
        )

        # search, cluster, min_price, max_price, min_rating, max_rating => 6 filters
        assert query.filter.call_count == 6

    def test_skip_and_limit_are_forwarded(self, mock_db: MagicMock):
        query = make_chained_query(count=0, all=[])
        mock_db.query.return_value = query
        repo = ProductRepository(mock_db)

        repo.find_all(skip=40, limit=20)

        query.offset.assert_called_once_with(40)
        query.limit.assert_called_once_with(20)

    def test_valid_sort_column_triggers_order_by_desc(self, mock_db: MagicMock):
        query = make_chained_query(count=0, all=[])
        mock_db.query.return_value = query
        repo = ProductRepository(mock_db)

        repo.find_all(sort_by="price", order="desc")

        query.order_by.assert_called_once()

    def test_valid_sort_column_triggers_order_by_asc_by_default(self, mock_db: MagicMock):
        query = make_chained_query(count=0, all=[])
        mock_db.query.return_value = query
        repo = ProductRepository(mock_db)

        repo.find_all(sort_by="price", order="asc")

        query.order_by.assert_called_once()

    def test_invalid_sort_column_is_ignored(self, mock_db: MagicMock):
        query = make_chained_query(count=0, all=[])
        mock_db.query.return_value = query
        repo = ProductRepository(mock_db)

        repo.find_all(sort_by="not_a_real_column")

        query.order_by.assert_not_called()

    def test_max_rating_five_uses_inclusive_comparison(self, mock_db: MagicMock):
        """When both min and max rating are 5, ratings of exactly 5 must remain (<=)."""
        query = make_chained_query(count=0, all=[])
        mock_db.query.return_value = query
        repo = ProductRepository(mock_db)

        repo.find_all(min_rating=5, max_rating=5)

        clause = str(query.filter.call_args_list[-1].args[0])
        assert "<=" in clause

    def test_max_rating_below_five_uses_exclusive_comparison(self, mock_db: MagicMock):
        query = make_chained_query(count=0, all=[])
        mock_db.query.return_value = query
        repo = ProductRepository(mock_db)

        repo.find_all(min_rating=3, max_rating=4)

        clause = str(query.filter.call_args_list[-1].args[0])
        assert "<=" not in clause
        assert "<" in clause


class TestFindById:
    def test_returns_product_when_found(self, mock_db: MagicMock, sample_product):
        mock_db.query.return_value.filter.return_value.first.return_value = sample_product

        result = ProductRepository(mock_db).find_by_id(1)

        assert result is sample_product

    def test_returns_none_when_not_found(self, mock_db: MagicMock):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = ProductRepository(mock_db).find_by_id(999)

        assert result is None


class TestCreate:
    def test_builds_product_from_schema_and_persists(self, mock_db: MagicMock):
        product_in = ProductCreate(product_name="New CCTV", price=100000)

        created = ProductRepository(mock_db).create(product_in)

        assert isinstance(created, Product)
        assert created.product_name == "New CCTV"
        assert created.price == 100000
        mock_db.add.assert_called_once_with(created)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(created)


class TestUpdate:
    def test_only_provided_fields_are_updated(self, mock_db: MagicMock, sample_product):
        original_name = sample_product.product_name
        update_in = ProductUpdate(price=999000)

        updated = ProductRepository(mock_db).update(sample_product, update_in)

        assert updated.price == 999000
        assert updated.product_name == original_name  # untouched field preserved
        mock_db.add.assert_called_once_with(sample_product)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_product)


class TestDelete:
    def test_deletes_and_commits(self, mock_db: MagicMock, sample_product):
        ProductRepository(mock_db).delete(sample_product)

        mock_db.delete.assert_called_once_with(sample_product)
        mock_db.commit.assert_called_once()


class TestGetDashboardStatistics:
    def test_aggregates_counts_in_expected_order(self, mock_db: MagicMock):
        query = make_chained_query()
        query.scalar.side_effect = [120, 8, 40, 50, 30]
        mock_db.query.return_value = query

        stats = ProductRepository(mock_db).get_dashboard_statistics()

        assert stats == {
            "total_products": 120,
            "total_brands": 8,
            "budget_cluster": 40,
            "mid_range_cluster": 50,
            "premium_cluster": 30,
        }

    def test_null_scalar_results_default_to_zero(self, mock_db: MagicMock):
        query = make_chained_query()
        query.scalar.side_effect = [None, None, None, None, None]
        mock_db.query.return_value = query

        stats = ProductRepository(mock_db).get_dashboard_statistics()

        assert all(value == 0 for value in stats.values())
