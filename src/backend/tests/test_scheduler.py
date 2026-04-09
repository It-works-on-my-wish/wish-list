"""
Unit tests for the price-check scheduler (check_prices function).
All tests mock supabase and ScraperFactory — no real DB or HTTP calls.

Note: ScraperFactory is imported LOCALLY inside check_prices(), so it must be
patched on its original module path, not on app.scheduler.scheduler.
"""

import pytest
from unittest.mock import MagicMock, patch, call
from uuid import uuid4
from app.scheduler.scheduler import check_prices
from app.scrapers.scraper_strategy import ScrapedProductData, ScrapingError

SCRAPER_FACTORY_PATH = "app.factories.scraper_factory.ScraperFactory.create_scraper"


def make_db_product(name="Phone", price=1000.0, url="https://www.hepsiburada.com/p-1", auto_track=True):
    return {
        "id": str(uuid4()),
        "name": name,
        "url": url,
        "current_price": price,
        "auto_track": auto_track,
    }


def setup_supabase_products(mock_supa, products):
    mock_supa.table.return_value.select.return_value.eq.return_value.execute.return_value.data = products


class TestCheckPricesFunction:

    def test_fetches_auto_track_products(self):
        with patch("app.scheduler.scheduler.supabase") as mock_supa:
            setup_supabase_products(mock_supa, [])
            check_prices()
            mock_supa.table.return_value.select.return_value.eq.assert_called_with("auto_track", True)

    def test_skips_products_without_url(self):
        product = make_db_product()
        product["url"] = None
        with patch("app.scheduler.scheduler.supabase") as mock_supa, \
             patch(SCRAPER_FACTORY_PATH) as mock_factory:
            setup_supabase_products(mock_supa, [product])
            check_prices()
            mock_factory.assert_not_called()

    def test_calls_scraper_factory_for_each_product(self):
        products = [make_db_product(f"Product {i}") for i in range(3)]
        mock_strategy = MagicMock()
        mock_strategy.extract_product_data.return_value = ScrapedProductData(
            title="Phone", source_domain="hepsiburada.com", current_price=999.0
        )
        with patch("app.scheduler.scheduler.supabase") as mock_supa, \
             patch(SCRAPER_FACTORY_PATH, return_value=mock_strategy) as mock_factory:
            setup_supabase_products(mock_supa, products)
            check_prices()
            assert mock_factory.call_count == 3

    def test_saves_new_price_to_price_history(self):
        product = make_db_product(price=1000.0)
        mock_strategy = MagicMock()
        mock_strategy.extract_product_data.return_value = ScrapedProductData(
            title="Phone", source_domain="hepsiburada.com", current_price=899.0
        )
        with patch("app.scheduler.scheduler.supabase") as mock_supa, \
             patch(SCRAPER_FACTORY_PATH, return_value=mock_strategy):
            setup_supabase_products(mock_supa, [product])
            check_prices()
            insert_calls = mock_supa.table.return_value.insert.call_args_list
            assert any(
                isinstance(c[0][0], dict) and c[0][0].get("price") == 899.0
                for c in insert_calls
            )

    def test_updates_current_price_in_products_table(self):
        product = make_db_product(price=1000.0)
        mock_strategy = MagicMock()
        mock_strategy.extract_product_data.return_value = ScrapedProductData(
            title="Phone", source_domain="hepsiburada.com", current_price=850.0
        )
        with patch("app.scheduler.scheduler.supabase") as mock_supa, \
             patch(SCRAPER_FACTORY_PATH, return_value=mock_strategy):
            setup_supabase_products(mock_supa, [product])
            check_prices()
            mock_supa.table.return_value.update.assert_called_with({"current_price": 850.0})

    def test_skips_product_when_scraped_price_is_none(self):
        product = make_db_product()
        mock_strategy = MagicMock()
        mock_strategy.extract_product_data.return_value = ScrapedProductData(
            title="Phone", source_domain="hepsiburada.com", current_price=None
        )
        with patch("app.scheduler.scheduler.supabase") as mock_supa, \
             patch(SCRAPER_FACTORY_PATH, return_value=mock_strategy):
            setup_supabase_products(mock_supa, [product])
            check_prices()
            mock_supa.table.return_value.update.assert_not_called()

    def test_continues_on_single_product_scraping_error(self):
        products = [make_db_product("Phone"), make_db_product("Laptop")]
        call_count = 0

        def scraper_side_effect(url):
            nonlocal call_count
            call_count += 1
            m = MagicMock()
            if call_count == 1:
                m.extract_product_data.side_effect = ScrapingError("Failed")
            else:
                m.extract_product_data.return_value = ScrapedProductData(
                    title="Laptop", source_domain="hepsiburada.com", current_price=20000.0
                )
            return m

        with patch("app.scheduler.scheduler.supabase") as mock_supa, \
             patch(SCRAPER_FACTORY_PATH, side_effect=scraper_side_effect):
            setup_supabase_products(mock_supa, products)
            check_prices()
            assert call_count == 2

    def test_does_not_raise_when_supabase_fails(self):
        with patch("app.scheduler.scheduler.supabase") as mock_supa:
            mock_supa.table.side_effect = Exception("DB connection lost")
            check_prices()


class TestStartScheduler:

    def test_scheduler_is_started(self):
        from app.scheduler.scheduler import start_scheduler
        mock_scheduler_cls = MagicMock()
        mock_scheduler_instance = MagicMock()
        mock_scheduler_cls.return_value = mock_scheduler_instance

        with patch("app.scheduler.scheduler.BackgroundScheduler", mock_scheduler_cls), \
             patch("app.scheduler.scheduler.IntervalTrigger", MagicMock()):
            start_scheduler()
            mock_scheduler_instance.start.assert_called_once()

    def test_scheduler_adds_check_prices_job(self):
        from app.scheduler.scheduler import start_scheduler
        mock_scheduler_cls = MagicMock()
        mock_scheduler_instance = MagicMock()
        mock_scheduler_cls.return_value = mock_scheduler_instance

        with patch("app.scheduler.scheduler.BackgroundScheduler", mock_scheduler_cls), \
             patch("app.scheduler.scheduler.IntervalTrigger", MagicMock()):
            start_scheduler()
            mock_scheduler_instance.add_job.assert_called_once()
            job_func = mock_scheduler_instance.add_job.call_args[0][0]
            assert job_func.__name__ == "check_prices"
