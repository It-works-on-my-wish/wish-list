import pytest
from unittest.mock import MagicMock
from bs4 import BeautifulSoup
from app.scrapers.hepsiburada_scraper import HepsiburadaScraper
from app.scrapers.scraper_strategy import ScrapedProductData, ScrapingError


SAMPLE_HTML_GRAPH = """<html><body>
<script type="application/ld+json">
{
  "@graph": [
    {"@type": "WebSite", "name": "Hepsiburada"},
    {
      "@type": "Product",
      "name": "Samsung Galaxy S24",
      "offers": {"price": "29999.00", "priceCurrency": "TRY"},
      "image": ["https://cdn.hepsiburada.com/galaxy.jpg"]
    }
  ]
}
</script></body></html>"""

SAMPLE_HTML_DIRECT = """<html><body>
<script type="application/ld+json">
{
  "@type": "Product",
  "name": "Apple MacBook Air",
  "offers": {"price": "45999.00", "priceCurrency": "TRY"},
  "image": "https://cdn.hepsiburada.com/macbook.jpg"
}
</script></body></html>"""

SAMPLE_HTML_NO_PRODUCT = """<html><body>
<script type="application/ld+json">{"@type": "WebSite", "name": "test"}</script>
</body></html>"""


class TestExtractJsonldProduct:

    def test_finds_product_in_graph_array(self):
        soup = BeautifulSoup(SAMPLE_HTML_GRAPH, "html.parser")
        result = HepsiburadaScraper._extract_jsonld_product(soup)
        assert result is not None
        assert result["name"] == "Samsung Galaxy S24"

    def test_finds_direct_product_type(self):
        soup = BeautifulSoup(SAMPLE_HTML_DIRECT, "html.parser")
        result = HepsiburadaScraper._extract_jsonld_product(soup)
        assert result is not None
        assert result["name"] == "Apple MacBook Air"

    def test_returns_none_when_no_product_found(self):
        soup = BeautifulSoup(SAMPLE_HTML_NO_PRODUCT, "html.parser")
        result = HepsiburadaScraper._extract_jsonld_product(soup)
        assert result is None

    def test_returns_none_on_empty_page(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        result = HepsiburadaScraper._extract_jsonld_product(soup)
        assert result is None

    def test_finds_product_in_list_format(self):
        html = """<html><body>
        <script type="application/ld+json">
        [{"@type": "Product", "name": "List Product"}]
        </script></body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        result = HepsiburadaScraper._extract_jsonld_product(soup)
        assert result is not None
        assert result["name"] == "List Product"


class TestExtractPrice:

    def test_extracts_price_from_offers_dict(self):
        data = {"offers": {"price": "1299.99", "priceCurrency": "TRY"}}
        assert HepsiburadaScraper._extract_price(data) == 1299.99

    def test_handles_comma_as_decimal_separator(self):
        data = {"offers": {"price": "37999,00"}}
        assert HepsiburadaScraper._extract_price(data) == 37999.00

    def test_extracts_price_from_offers_list(self):
        data = {"offers": [{"price": "599.00"}]}
        assert HepsiburadaScraper._extract_price(data) == 599.00

    def test_returns_none_when_price_missing(self):
        data = {"offers": {}}
        assert HepsiburadaScraper._extract_price(data) is None

    def test_returns_none_when_no_offers(self):
        data = {}
        assert HepsiburadaScraper._extract_price(data) is None

    def test_integer_price_string(self):
        data = {"offers": {"price": "5000"}}
        assert HepsiburadaScraper._extract_price(data) == 5000.0


class TestExtractCurrency:

    def test_returns_currency_from_offers(self):
        data = {"offers": {"priceCurrency": "USD"}}
        assert HepsiburadaScraper._extract_currency(data) == "USD"

    def test_defaults_to_try(self):
        data = {"offers": {}}
        assert HepsiburadaScraper._extract_currency(data) == "TRY"

    def test_defaults_to_try_when_no_offers(self):
        data = {}
        assert HepsiburadaScraper._extract_currency(data) == "TRY"

    def test_currency_from_list_offers(self):
        data = {"offers": [{"priceCurrency": "EUR"}]}
        assert HepsiburadaScraper._extract_currency(data) == "EUR"


class TestExtractImage:

    def test_extracts_first_image_from_list(self):
        data = {"image": ["https://cdn.example.com/img1.jpg", "https://cdn.example.com/img2.jpg"]}
        assert HepsiburadaScraper._extract_image(data) == "https://cdn.example.com/img1.jpg"

    def test_extracts_image_string(self):
        data = {"image": "https://cdn.example.com/img.jpg"}
        assert HepsiburadaScraper._extract_image(data) == "https://cdn.example.com/img.jpg"

    def test_returns_none_when_no_image(self):
        data = {}
        assert HepsiburadaScraper._extract_image(data) is None

    def test_returns_none_for_empty_list(self):
        data = {"image": []}
        assert HepsiburadaScraper._extract_image(data) is None


class TestExtractProductData:

    def test_raises_scraping_error_on_http_failure(self, monkeypatch):
        import app.scrapers.hepsiburada_scraper as hb_module
        mock_req = MagicMock()
        mock_req.get.side_effect = Exception("Connection refused")
        monkeypatch.setattr(hb_module, "curl_requests", mock_req)

        with pytest.raises(ScrapingError):
            HepsiburadaScraper().extract_product_data("https://www.hepsiburada.com/p-12345")

    def test_raises_scraping_error_when_no_jsonld(self, monkeypatch):
        import app.scrapers.hepsiburada_scraper as hb_module
        mock_resp = MagicMock()
        mock_resp.text = "<html><body>No JSON-LD here</body></html>"
        mock_resp.raise_for_status = MagicMock()
        mock_req = MagicMock()
        mock_req.get.return_value = mock_resp
        monkeypatch.setattr(hb_module, "curl_requests", mock_req)

        with pytest.raises(ScrapingError):
            HepsiburadaScraper().extract_product_data("https://www.hepsiburada.com/p-12345")

    def test_returns_scraped_product_data(self, monkeypatch):
        import app.scrapers.hepsiburada_scraper as hb_module
        mock_resp = MagicMock()
        mock_resp.text = SAMPLE_HTML_GRAPH
        mock_resp.raise_for_status = MagicMock()
        mock_req = MagicMock()
        mock_req.get.return_value = mock_resp
        monkeypatch.setattr(hb_module, "curl_requests", mock_req)

        result = HepsiburadaScraper().extract_product_data("https://www.hepsiburada.com/p-12345")

        assert isinstance(result, ScrapedProductData)
        assert result.title == "Samsung Galaxy S24"
        assert result.current_price == 29999.00
        assert result.currency == "TRY"
        assert result.source_domain == "hepsiburada.com"

    def test_scraped_data_contains_image_url(self, monkeypatch):
        import app.scrapers.hepsiburada_scraper as hb_module
        mock_resp = MagicMock()
        mock_resp.text = SAMPLE_HTML_GRAPH
        mock_resp.raise_for_status = MagicMock()
        mock_req = MagicMock()
        mock_req.get.return_value = mock_resp
        monkeypatch.setattr(hb_module, "curl_requests", mock_req)

        result = HepsiburadaScraper().extract_product_data("https://www.hepsiburada.com/p-12345")
        assert result.image_url == "https://cdn.hepsiburada.com/galaxy.jpg"
