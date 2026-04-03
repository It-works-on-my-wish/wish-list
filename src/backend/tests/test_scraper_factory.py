import pytest
from app.factories.scraper_factory import ScraperFactory, UnsupportedPlatformError
from app.scrapers.hepsiburada_scraper import HepsiburadaScraper
from app.scrapers.scraper_strategy import ScraperStrategy


class TestScraperFactoryHepsiburada:

    def test_hepsiburada_url_returns_hepsiburada_scraper(self):
        scraper = ScraperFactory.create_scraper("https://www.hepsiburada.com/product-p-12345")
        assert isinstance(scraper, HepsiburadaScraper)

    def test_hepsiburada_without_www_also_works(self):
        scraper = ScraperFactory.create_scraper("https://hepsiburada.com/product-p-12345")
        assert isinstance(scraper, HepsiburadaScraper)

    def test_returned_scraper_implements_strategy_interface(self):
        scraper = ScraperFactory.create_scraper("https://www.hepsiburada.com/product-p-12345")
        assert isinstance(scraper, ScraperStrategy)

    def test_hepsiburada_with_deep_path_works(self):
        url = "https://www.hepsiburada.com/samsung-galaxy-s24-pm-HBC00003NTYGU"
        scraper = ScraperFactory.create_scraper(url)
        assert isinstance(scraper, HepsiburadaScraper)

    def test_each_call_returns_new_instance(self):
        url = "https://www.hepsiburada.com/product-p-12345"
        s1 = ScraperFactory.create_scraper(url)
        s2 = ScraperFactory.create_scraper(url)
        assert s1 is not s2


class TestScraperFactoryUnsupported:

    def test_unknown_domain_raises_unsupported_error(self):
        with pytest.raises(UnsupportedPlatformError):
            ScraperFactory.create_scraper("https://www.amazon.com/product/123")

    def test_trendyol_not_yet_supported(self):
        with pytest.raises(UnsupportedPlatformError):
            ScraperFactory.create_scraper("https://www.trendyol.com/product/123")

    def test_n11_not_supported(self):
        with pytest.raises(UnsupportedPlatformError):
            ScraperFactory.create_scraper("https://www.n11.com/product/123")

    def test_error_message_contains_unsupported_domain(self):
        with pytest.raises(UnsupportedPlatformError) as exc_info:
            ScraperFactory.create_scraper("https://www.trendyol.com/product/123")
        assert "trendyol.com" in str(exc_info.value)

    def test_error_message_mentions_supported_platforms(self):
        with pytest.raises(UnsupportedPlatformError) as exc_info:
            ScraperFactory.create_scraper("https://www.amazon.com/product/123")
        assert "hepsiburada" in str(exc_info.value).lower()

    def test_localhost_url_raises_error(self):
        with pytest.raises(UnsupportedPlatformError):
            ScraperFactory.create_scraper("http://localhost:3000/product/1")

    def test_empty_domain_raises_error(self):
        with pytest.raises((UnsupportedPlatformError, Exception)):
            ScraperFactory.create_scraper("not-a-url")
