import pytest
from app.factories.scraper_factory import ScraperFactory, UnsupportedPlatformError
from app.scrapers.hepsiburada_scraper import HepsiburadaScraper
from app.scrapers.trendyol_scraper import TrendyolScraper
from app.scrapers.amazon_scraper import AmazonScraper
from app.scrapers.boyner_scraper import BoynerScraper
from app.scrapers.mediamarkt_scraper import MediaMarktScraper
from app.scrapers.teknosa_scraper import TeknosaScraper
from app.scrapers.llm_scraper import LLMScraper
from app.scrapers.scraper_strategy import ScraperStrategy


class TestScraperFactoryRegisteredPlatforms:

    def test_hepsiburada_url_returns_hepsiburada_scraper(self):
        scraper = ScraperFactory.create_scraper("https://www.hepsiburada.com/product-p-12345")
        assert isinstance(scraper, HepsiburadaScraper)

    def test_trendyol_url_returns_trendyol_scraper(self):
        scraper = ScraperFactory.create_scraper("https://www.trendyol.com/product/detail-p-12345")
        assert isinstance(scraper, TrendyolScraper)

    def test_amazon_url_returns_amazon_scraper(self):
        scraper = ScraperFactory.create_scraper("https://www.amazon.com.tr/dp/B09XYZ")
        assert isinstance(scraper, AmazonScraper)

    def test_boyner_url_returns_boyner_scraper(self):
        scraper = ScraperFactory.create_scraper("https://www.boyner.com.tr/p/product-123")
        assert isinstance(scraper, BoynerScraper)

    def test_mediamarkt_url_returns_mediamarkt_scraper(self):
        scraper = ScraperFactory.create_scraper("https://www.mediamarkt.com.tr/tr/product/12345.html")
        assert isinstance(scraper, MediaMarktScraper)

    def test_teknosa_url_returns_teknosa_scraper(self):
        scraper = ScraperFactory.create_scraper("https://www.teknosa.com/urun/12345")
        assert isinstance(scraper, TeknosaScraper)


class TestScraperFactoryLLMFallback:

    def test_unknown_domain_falls_back_to_llm_scraper(self):
        scraper = ScraperFactory.create_scraper("https://www.n11.com/product/123")
        assert isinstance(scraper, LLMScraper)

    def test_unsupported_platform_returns_llm_not_raises(self):
        # Factory no longer raises — it falls back to LLM for any unknown domain
        scraper = ScraperFactory.create_scraper("https://www.ciceksepeti.com/product/123")
        assert isinstance(scraper, LLMScraper)

    def test_completely_unknown_site_returns_llm(self):
        scraper = ScraperFactory.create_scraper("https://www.randomshop.com/item/abc")
        assert isinstance(scraper, LLMScraper)


class TestScraperFactoryInterface:

    def test_all_registered_scrapers_implement_strategy(self):
        urls = [
            "https://www.hepsiburada.com/p-12345",
            "https://www.trendyol.com/p-12345",
            "https://www.amazon.com.tr/dp/B09",
            "https://www.boyner.com.tr/p/123",
            "https://www.mediamarkt.com.tr/tr/product/1.html",
            "https://www.teknosa.com/urun/1",
        ]
        for url in urls:
            scraper = ScraperFactory.create_scraper(url)
            assert isinstance(scraper, ScraperStrategy), f"Scraper for {url} must implement ScraperStrategy"

    def test_llm_fallback_also_implements_strategy(self):
        scraper = ScraperFactory.create_scraper("https://www.unknown-site.com/product")
        assert isinstance(scraper, ScraperStrategy)

    def test_each_call_returns_new_instance(self):
        url = "https://www.hepsiburada.com/product-p-12345"
        s1 = ScraperFactory.create_scraper(url)
        s2 = ScraperFactory.create_scraper(url)
        assert s1 is not s2

    def test_hepsiburada_without_www(self):
        scraper = ScraperFactory.create_scraper("https://hepsiburada.com/product-p-12345")
        assert isinstance(scraper, HepsiburadaScraper)

    def test_trendyol_without_www(self):
        scraper = ScraperFactory.create_scraper("https://trendyol.com/product-p-12345")
        assert isinstance(scraper, TrendyolScraper)
