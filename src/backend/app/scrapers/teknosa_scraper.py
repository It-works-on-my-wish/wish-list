from app.scrapers.scraper_strategy import (
    ScrapedProductData,
    ScraperStrategy,
    ScrapingError,
)
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests


class TeknosaScraper(ScraperStrategy):

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    def extract_product_data(self, url: str) -> ScrapedProductData:
        try:
            response = curl_requests.get(
                url, headers=self.HEADERS, impersonate="chrome120", timeout=15
            )
            response.raise_for_status()
        except Exception as e:
            raise ScrapingError(f"Failed to fetch Teknosa page: {e}")

        soup = BeautifulSoup(response.text, "html.parser")

        title = self._extract_title(soup) or "Unknown Product"
        price = self._extract_price(soup)
        image_url = self._extract_image(soup)

        return ScrapedProductData(
            title=title,
            current_price=price,
            image_url=image_url,
            currency="TRY",
            source_domain="teknosa.com",
        )

    @staticmethod
    def _extract_price(soup: BeautifulSoup) -> float | None:
        price_tag = soup.select_one("#visiblePi")

        if price_tag:
            price_str = price_tag.get("value", "")
        else:
            price_tag = soup.select_one("span.prc")
            price_str = price_tag.text if price_tag else ""

        if price_str:
            price_str = price_str.replace("TL", "").strip()
            price_str = price_str.replace(".", "").replace(",", ".")

            try:
                return float(price_str)
            except ValueError:
                return None

        return None

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str | None:
        brand_tag = soup.select_one("a.link b")
        name_tag = soup.select_one("span.replaceName")

        brand = brand_tag.text.strip() if brand_tag else ""
        name = name_tag.text.strip() if name_tag else ""

        full_title = f"{brand} {name}".strip()

        return full_title if full_title else None

    @staticmethod
    def _extract_image(soup: BeautifulSoup) -> str | None:
        slide = soup.select_one("div.swiper-slide[data-zoom]")

        if slide:
            zoom_url = slide.get("data-zoom")

            if zoom_url:
                # 1200x1200 -> 600x600
                return zoom_url.replace("/1200/1200", "/600/600")

        return None
