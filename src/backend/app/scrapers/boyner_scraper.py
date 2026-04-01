from app.scrapers.scraper_strategy import (
    ScrapedProductData,
    ScraperStrategy,
    ScrapingError,
)
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests


class BoynerScraper(ScraperStrategy):

    HEADERS = {
        "User-Agent": "Mozilla/5.0 ...",
    }

    def extract_product_data(self, url: str) -> ScrapedProductData:
        try:
            response = curl_requests.get(
                url, headers=self.HEADERS, impersonate="chrome120", timeout=15
            )
            response.raise_for_status()
        except Exception as e:
            raise ScrapingError(f"Failed to fetch Boyner page: {e}")

        soup = BeautifulSoup(response.text, "html.parser")

        title = self._extract_title(soup) or "Unknown Product"
        price = self._extract_price(soup)
        image_url = self._extract_image(soup)

        return ScrapedProductData(
            title=title,
            current_price=price,
            image_url=image_url,
            currency="TRY",
            source_domain="boyner.com",
        )

    @staticmethod
    def _extract_price(soup: BeautifulSoup) -> float | None:
        price_tag = soup.select_one("h2.price_priceMain__DrVVQ")

        if price_tag:
            price_str = price_tag.text.strip()
            price_str = price_str.replace("TL", "").strip()
            price_str = price_str.replace(".", "").replace(",", ".")
            try:
                return float(price_str)
            except ValueError:
                return None

        return None

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str | None:
        name_tag = soup.select_one("h1[class*='productInfoSectionHeaderProductName']")
        brand_tag = soup.select_one("p[class*='productInfoSectionHeaderBrandName'] a")

        if name_tag:
            name = name_tag.text.strip()
            brand = brand_tag.text.strip() if brand_tag else ""
            return f"{brand} {name}".strip()

        return None

    @staticmethod
    def _extract_image(soup: BeautifulSoup) -> str | None:
        img_tags = soup.select('div[class*="productGalleryDesktopImageBox"] img')

        for img in img_tags:
            src = img.get("src")

            if not src:
                continue

            # fake placeholder skip
            if src.startswith("data:image"):
                continue

            # sadece gerçek CDN görselleri al
            if "boyner.com.tr" in src:
                return src.strip()

        return None
