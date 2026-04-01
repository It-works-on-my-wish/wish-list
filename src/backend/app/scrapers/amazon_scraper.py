from app.scrapers.scraper_strategy import (
    ScrapedProductData,
    ScraperStrategy,
    ScrapingError,
)
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests


class AmazonScraper(ScraperStrategy):

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
            raise ScrapingError(f"Failed to fetch Amazon page: {e}")

        soup = BeautifulSoup(response.text, "html.parser")

        title = self._extract_title(soup) or "Unknown Product"
        price = self._extract_price(soup)
        image_url = self._extract_image(soup)

        return ScrapedProductData(
            title=title,
            current_price=price,
            image_url=image_url,
            currency="TRY",
            source_domain="amazon.com",
        )

    @staticmethod
    def _extract_price(soup: BeautifulSoup) -> float | None:
        price_tag = soup.select_one("span.a-price-whole")
        if price_tag:
            for span in price_tag.find_all("span"):
                span.decompose()
            price_str = price_tag.text.strip()
            price_str = price_str.replace(".", "")
            return float(price_str)

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str | None:
        title_tag = soup.select_one("span#productTitle")
        if title_tag:
            return title_tag.text.strip()
        return None

    @staticmethod
    def _extract_image(soup: BeautifulSoup) -> str | None:
        img_tag = soup.select_one("img#landingImage")
        if img_tag:
            return img_tag.get("data-old-hires") or img_tag.get("src")
        return None
