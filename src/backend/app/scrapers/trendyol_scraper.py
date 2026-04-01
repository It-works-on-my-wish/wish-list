from app.scrapers.scraper_strategy import (
    ScrapedProductData,
    ScraperStrategy,
    ScrapingError,
)
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests


class TrendyolScraper(ScraperStrategy):

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
            raise ScrapingError(f"Failed to fetch Trendyol page: {e}")

        soup = BeautifulSoup(response.text, "html.parser")

        title = self._extract_title(soup) or "Unknown Product"
        price = self._extract_price(soup)
        image_url = self._extract_image(soup)

        return ScrapedProductData(
            title=title,
            current_price=price,
            image_url=image_url,
            currency="TRY",
            source_domain="trendyol.com",
        )

    @staticmethod
    def _extract_price(soup: BeautifulSoup) -> float | None:
        price_tag = soup.select_one("span.discounted")
        if price_tag:
            try:
                price_str = price_tag.text.strip()
                price_str = (
                    price_str.replace(" TL", "").replace(".", "").replace(",", ".")
                )
                return float(price_str)
            except (ValueError, TypeError):
                return None
        return None

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str | None:
        title_tag = soup.select_one("h1.product-title")
        if title_tag:
            brand_tag = title_tag.select_one("strong")
            brand = brand_tag.text.strip() if brand_tag else ""

            full_text = title_tag.get_text(separator=" ").strip()
            return full_text
        return None

    @staticmethod
    def _extract_image(soup: BeautifulSoup) -> str | None:
        img_tag = soup.select_one("img._carouselImage_abb7111")
        if img_tag:
            return img_tag.get("src")
        return None
