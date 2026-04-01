from app.scrapers.scraper_strategy import (
    ScrapedProductData,
    ScraperStrategy,
    ScrapingError,
)
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests


class MediaMarktScraper(ScraperStrategy):

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
            raise ScrapingError(f"Failed to fetch MediaMarkt page: {e}")

        soup = BeautifulSoup(response.text, "html.parser")

        title = self._extract_title(soup) or "Unknown Product"
        price = self._extract_price(soup)
        image_url = self._extract_image(soup)

        return ScrapedProductData(
            title=title,
            current_price=price,
            image_url=image_url,
            currency="TRY",
            source_domain="mediamarkt.com",
        )

    @staticmethod
    def _extract_price(soup: BeautifulSoup) -> float | None:
        price_tag = soup.select_one('[data-test="branded-price-whole-value"]')

        if price_tag:
            price_str = price_tag.text.strip()

            price_str = price_str.replace("₺", "").strip()
            price_str = price_str.replace(".", "")
            price_str = price_str.replace(",", "")

            try:
                return float(price_str)
            except ValueError:
                return None

        return None

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str | None:
        title_tag = soup.select_one('h1[class*="sc-"]')

        if title_tag:
            return title_tag.text.strip()

        return None

    @staticmethod
    def _extract_image(soup: BeautifulSoup) -> str | None:
        img_tags = soup.select("img.pdp-gallery-image")

        for img in img_tags:
            src = img.get("src")
            if not src:
                continue
            if src.startswith("data:image"):
                continue
            return src.strip()

        return None
