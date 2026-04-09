"""
Unit tests for LLMScraper — tests _parse_price static method and
extract_product_data with fully mocked HTTP + Groq client.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.scrapers.llm_scraper import LLMScraper
from app.scrapers.scraper_strategy import ScrapedProductData, ScrapingError


class TestLLMScraperParsePrice:

    def test_parses_float_directly(self):
        assert LLMScraper._parse_price(1299.99) == 1299.99

    def test_parses_integer(self):
        assert LLMScraper._parse_price(5000) == 5000.0

    def test_parses_string_number(self):
        assert LLMScraper._parse_price("2499.99") == 2499.99

    def test_removes_comma_thousand_separator(self):
        # LLM sometimes returns "1,299.00" (US format)
        assert LLMScraper._parse_price("1,299.00") == 1299.00

    def test_returns_none_for_none(self):
        assert LLMScraper._parse_price(None) is None

    def test_returns_none_for_invalid_string(self):
        assert LLMScraper._parse_price("not-a-price") is None

    def test_returns_none_for_empty_string(self):
        assert LLMScraper._parse_price("") is None

    def test_parses_zero(self):
        assert LLMScraper._parse_price(0) == 0.0

    def test_parses_string_with_spaces(self):
        assert LLMScraper._parse_price("  999.00  ") == 999.0


class TestLLMScraperExtractProductData:

    def _make_scraper(self):
        """Create LLMScraper with a mocked Groq client."""
        scraper = LLMScraper.__new__(LLMScraper)
        scraper.client = MagicMock()
        return scraper

    def _mock_http(self, monkeypatch, html: str):
        import app.scrapers.llm_scraper as mod
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_req = MagicMock()
        mock_req.get.return_value = mock_resp
        monkeypatch.setattr(mod, "curl_requests", mock_req)

    def _mock_groq_response(self, scraper, json_text: str):
        mock_choice = MagicMock()
        mock_choice.message.content = json_text
        mock_result = MagicMock()
        mock_result.choices = [mock_choice]
        scraper.client.chat.completions.create.return_value = mock_result

    def test_returns_scraped_product_data(self, monkeypatch):
        scraper = self._make_scraper()
        self._mock_http(monkeypatch, "<html><body>Product page</body></html>")
        self._mock_groq_response(scraper, '{"title": "Test Phone", "price": 9999.0, "currency": "TRY", "image_url": null}')
        result = scraper.extract_product_data("https://www.unknownshop.com/p/1")
        assert isinstance(result, ScrapedProductData)
        assert result.title == "Test Phone"

    def test_price_is_parsed_correctly(self, monkeypatch):
        scraper = self._make_scraper()
        self._mock_http(monkeypatch, "<html><body>text</body></html>")
        self._mock_groq_response(scraper, '{"title": "Laptop", "price": 25000.0, "currency": "TRY", "image_url": null}')
        result = scraper.extract_product_data("https://www.unknownshop.com/p/2")
        assert result.current_price == 25000.0

    def test_currency_is_set_from_llm_response(self, monkeypatch):
        scraper = self._make_scraper()
        self._mock_http(monkeypatch, "<html><body>text</body></html>")
        self._mock_groq_response(scraper, '{"title": "Watch", "price": 500.0, "currency": "USD", "image_url": null}')
        result = scraper.extract_product_data("https://www.unknownshop.com/p/3")
        assert result.currency == "USD"

    def test_source_domain_is_extracted_from_url(self, monkeypatch):
        scraper = self._make_scraper()
        self._mock_http(monkeypatch, "<html><body>text</body></html>")
        self._mock_groq_response(scraper, '{"title": "Bag", "price": 300.0, "currency": "TRY", "image_url": null}')
        result = scraper.extract_product_data("https://www.ciceksepeti.com/urun/1")
        assert result.source_domain == "www.ciceksepeti.com"

    def test_raises_scraping_error_on_http_failure(self, monkeypatch):
        import app.scrapers.llm_scraper as mod
        mock_req = MagicMock()
        mock_req.get.side_effect = Exception("Connection refused")
        monkeypatch.setattr(mod, "curl_requests", mock_req)
        scraper = self._make_scraper()
        with pytest.raises(ScrapingError):
            scraper.extract_product_data("https://www.unknownshop.com/p/1")

    def test_raises_scraping_error_when_llm_returns_invalid_json(self, monkeypatch):
        scraper = self._make_scraper()
        self._mock_http(monkeypatch, "<html><body>text</body></html>")
        self._mock_groq_response(scraper, "Sorry, I cannot help with that.")
        with pytest.raises(ScrapingError):
            scraper.extract_product_data("https://www.unknownshop.com/p/1")

    def test_defaults_unknown_product_title_when_missing(self, monkeypatch):
        scraper = self._make_scraper()
        self._mock_http(monkeypatch, "<html><body>text</body></html>")
        self._mock_groq_response(scraper, '{"price": 100.0, "currency": "TRY"}')
        result = scraper.extract_product_data("https://www.unknownshop.com/p/1")
        assert result.title == "Unknown Product"
