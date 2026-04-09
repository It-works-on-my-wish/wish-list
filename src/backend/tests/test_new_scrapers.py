"""
Parser unit tests for Trendyol, Amazon, Boyner, MediaMarkt, and Teknosa scrapers.
All tests use pre-built HTML snippets — no real HTTP calls are made.
"""

import pytest
from unittest.mock import MagicMock
from bs4 import BeautifulSoup
from app.scrapers.trendyol_scraper import TrendyolScraper
from app.scrapers.amazon_scraper import AmazonScraper
from app.scrapers.boyner_scraper import BoynerScraper
from app.scrapers.mediamarkt_scraper import MediaMarktScraper
from app.scrapers.teknosa_scraper import TeknosaScraper
from app.scrapers.scraper_strategy import ScrapedProductData, ScrapingError


# ------------------------------------------------------------------ #
#  Trendyol                                                           #
# ------------------------------------------------------------------ #

class TestTrendyolScraperParsers:

    def test_extract_price_from_discounted_span(self):
        html = '<html><body><span class="discounted">1.299,90 TL</span></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        price = TrendyolScraper._extract_price(soup)
        assert price == 1299.90

    def test_extract_price_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert TrendyolScraper._extract_price(soup) is None

    def test_extract_title_from_h1(self):
        html = '<html><body><h1 class="product-title"><strong>Nike</strong> Air Max</h1></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        title = TrendyolScraper._extract_title(soup)
        assert title is not None
        assert "Nike" in title

    def test_extract_title_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert TrendyolScraper._extract_title(soup) is None

    def test_extract_image_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert TrendyolScraper._extract_image(soup) is None

    def test_extract_raises_scraping_error_on_http_failure(self, monkeypatch):
        import app.scrapers.trendyol_scraper as mod
        mock_req = MagicMock()
        mock_req.get.side_effect = Exception("Connection refused")
        monkeypatch.setattr(mod, "curl_requests", mock_req)
        with pytest.raises(ScrapingError):
            TrendyolScraper().extract_product_data("https://www.trendyol.com/p-1")

    def test_extract_returns_scraped_data(self, monkeypatch):
        import app.scrapers.trendyol_scraper as mod
        html = '<html><body><h1 class="product-title">Test Shoe</h1><span class="discounted">999,00 TL</span></body></html>'
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_req = MagicMock()
        mock_req.get.return_value = mock_resp
        monkeypatch.setattr(mod, "curl_requests", mock_req)
        result = TrendyolScraper().extract_product_data("https://www.trendyol.com/p-1")
        assert isinstance(result, ScrapedProductData)
        assert result.source_domain == "trendyol.com"


# ------------------------------------------------------------------ #
#  Amazon                                                             #
# ------------------------------------------------------------------ #

class TestAmazonScraperParsers:

    def test_extract_price_from_price_whole(self):
        html = '<html><body><span class="a-price-whole">4.599<span class="separator">.</span></span></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        price = AmazonScraper._extract_price(soup)
        assert price == 4599.0

    def test_extract_price_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert AmazonScraper._extract_price(soup) is None

    def test_extract_title_from_product_title(self):
        html = '<html><body><span id="productTitle">  Apple iPhone 15  </span></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert AmazonScraper._extract_title(soup) == "Apple iPhone 15"

    def test_extract_title_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert AmazonScraper._extract_title(soup) is None

    def test_extract_image_from_landing_image(self):
        html = '<html><body><img id="landingImage" data-old-hires="https://cdn.amazon.com/img.jpg" src="small.jpg"/></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert AmazonScraper._extract_image(soup) == "https://cdn.amazon.com/img.jpg"

    def test_extract_image_falls_back_to_src(self):
        html = '<html><body><img id="landingImage" src="https://cdn.amazon.com/fallback.jpg"/></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert AmazonScraper._extract_image(soup) == "https://cdn.amazon.com/fallback.jpg"

    def test_extract_image_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert AmazonScraper._extract_image(soup) is None

    def test_extract_raises_on_http_failure(self, monkeypatch):
        import app.scrapers.amazon_scraper as mod
        mock_req = MagicMock()
        mock_req.get.side_effect = Exception("Timeout")
        monkeypatch.setattr(mod, "curl_requests", mock_req)
        with pytest.raises(ScrapingError):
            AmazonScraper().extract_product_data("https://www.amazon.com.tr/dp/B09")


# ------------------------------------------------------------------ #
#  Boyner                                                             #
# ------------------------------------------------------------------ #

class TestBoynerScraperParsers:

    def test_extract_price_removes_tl_suffix(self):
        html = '<html><body><h2 class="price_priceMain__DrVVQ">2.499,00 TL</h2></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert BoynerScraper._extract_price(soup) == 2499.00

    def test_extract_price_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert BoynerScraper._extract_price(soup) is None

    def test_extract_title_combines_brand_and_name(self):
        html = '''<html><body>
        <p class="productInfoSectionHeaderBrandName"><a>Nike</a></p>
        <h1 class="productInfoSectionHeaderProductName">Air Force 1</h1>
        </body></html>'''
        soup = BeautifulSoup(html, "html.parser")
        title = BoynerScraper._extract_title(soup)
        assert "Nike" in title
        assert "Air Force 1" in title

    def test_extract_title_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert BoynerScraper._extract_title(soup) is None

    def test_extract_image_skips_data_urls(self):
        html = '''<html><body>
        <div class="productGalleryDesktopImageBox">
          <img src="data:image/gif;base64,R0lGOD"/>
          <img src="https://img.boyner.com.tr/product.jpg"/>
        </div></body></html>'''
        soup = BeautifulSoup(html, "html.parser")
        result = BoynerScraper._extract_image(soup)
        assert result == "https://img.boyner.com.tr/product.jpg"

    def test_extract_image_returns_none_when_only_placeholder(self):
        html = '<html><body><div class="productGalleryDesktopImageBox"><img src="data:image/gif;base64,abc"/></div></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert BoynerScraper._extract_image(soup) is None

    def test_extract_raises_on_http_failure(self, monkeypatch):
        import app.scrapers.boyner_scraper as mod
        mock_req = MagicMock()
        mock_req.get.side_effect = Exception("Network error")
        monkeypatch.setattr(mod, "curl_requests", mock_req)
        with pytest.raises(ScrapingError):
            BoynerScraper().extract_product_data("https://www.boyner.com.tr/p/123")


# ------------------------------------------------------------------ #
#  MediaMarkt                                                         #
# ------------------------------------------------------------------ #

class TestMediaMarktScraperParsers:

    def test_extract_price_removes_currency_symbols(self):
        html = '<html><body><span data-test="branded-price-whole-value">₺12.999</span></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert MediaMarktScraper._extract_price(soup) == 12999.0

    def test_extract_price_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert MediaMarktScraper._extract_price(soup) is None

    def test_extract_title_from_h1(self):
        html = '<html><body><h1 class="sc-abc123">Samsung 65" QLED TV</h1></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert MediaMarktScraper._extract_title(soup) == 'Samsung 65" QLED TV'

    def test_extract_title_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert MediaMarktScraper._extract_title(soup) is None

    def test_extract_image_skips_data_urls(self):
        html = '''<html><body>
        <img class="pdp-gallery-image" src="data:image/png;base64,abc"/>
        <img class="pdp-gallery-image" src="https://cdn.mediamarkt.com.tr/img.jpg"/>
        </body></html>'''
        soup = BeautifulSoup(html, "html.parser")
        assert MediaMarktScraper._extract_image(soup) == "https://cdn.mediamarkt.com.tr/img.jpg"

    def test_extract_image_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert MediaMarktScraper._extract_image(soup) is None

    def test_extract_raises_on_http_failure(self, monkeypatch):
        import app.scrapers.mediamarkt_scraper as mod
        mock_req = MagicMock()
        mock_req.get.side_effect = Exception("SSL error")
        monkeypatch.setattr(mod, "curl_requests", mock_req)
        with pytest.raises(ScrapingError):
            MediaMarktScraper().extract_product_data("https://www.mediamarkt.com.tr/tr/product/1.html")


# ------------------------------------------------------------------ #
#  Teknosa                                                            #
# ------------------------------------------------------------------ #

class TestTeknosaScraper:

    def test_extract_price_from_visible_pi_input(self):
        html = '<html><body><input id="visiblePi" value="8.999,00"/></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert TeknosaScraper._extract_price(soup) == 8999.00

    def test_extract_price_from_prc_span_fallback(self):
        html = '<html><body><span class="prc">5.499,99 TL</span></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert TeknosaScraper._extract_price(soup) == 5499.99

    def test_extract_price_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert TeknosaScraper._extract_price(soup) is None

    def test_extract_title_combines_brand_and_name(self):
        html = '''<html><body>
        <a class="link"><b>Apple</b></a>
        <span class="replaceName">iPhone 15 128GB</span>
        </body></html>'''
        soup = BeautifulSoup(html, "html.parser")
        title = TeknosaScraper._extract_title(soup)
        assert "Apple" in title
        assert "iPhone 15 128GB" in title

    def test_extract_title_returns_none_when_both_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert TeknosaScraper._extract_title(soup) is None

    def test_extract_image_from_swiper_zoom(self):
        html = '<html><body><div class="swiper-slide" data-zoom="https://cdn.teknosa.com/1200/1200/img.jpg"></div></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        result = TeknosaScraper._extract_image(soup)
        assert result == "https://cdn.teknosa.com/600/600/img.jpg"

    def test_extract_image_returns_none_when_missing(self):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert TeknosaScraper._extract_image(soup) is None

    def test_extract_raises_on_http_failure(self, monkeypatch):
        import app.scrapers.teknosa_scraper as mod
        mock_req = MagicMock()
        mock_req.get.side_effect = Exception("Timeout")
        monkeypatch.setattr(mod, "curl_requests", mock_req)
        with pytest.raises(ScrapingError):
            TeknosaScraper().extract_product_data("https://www.teknosa.com/urun/123")
