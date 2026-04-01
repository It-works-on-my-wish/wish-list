import json

from app.scrapers.scraper_strategy import (
    ScrapedProductData,
    ScraperStrategy,
    ScrapingError,
)
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests


class HepsiburadaScraper(ScraperStrategy):
    """
    Concrete Strategy: Hepsiburada product scraper.

    Extracts product data from Hepsiburada product pages by parsing
    the JSON-LD structured data (Schema.org Product type) that
    Hepsiburada embeds in every product page.

    Uses curl_cffi with Chrome TLS impersonation to bypass basic
    bot detection.
    """

    # Headers mimicking a real browser request
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
    }

    def extract_product_data(self, url: str) -> ScrapedProductData:
        """
        Scrape product data from a Hepsiburada product page.

        Parses JSON-LD structured data to extract:
        - Product title
        - Price and currency from the Offer
        - Product image URL

        Args:
            url: Full Hepsiburada product URL.

        Returns:
            ScrapedProductData with extracted fields.

        Raises:
            ScrapingError: If the page cannot be fetched or parsed.
        """
        try:
            response = curl_requests.get(
                url,
                headers=self.HEADERS,
                impersonate="chrome120",
                timeout=15,
            )
            response.raise_for_status()
        except Exception as e:
            raise ScrapingError(f"Failed to fetch Hepsiburada page: {e}")

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract Product data from JSON-LD
        product_data = self._extract_jsonld_product(soup)

        if not product_data:
            raise ScrapingError(
                "Could not find Product JSON-LD data on the Hepsiburada page. "
                "The page structure may have changed."
            )

        # Extract fields from the JSON-LD Product object
        title = product_data.get("name", "Unknown Product")
        price = self._extract_price(product_data)
        currency = self._extract_currency(product_data)
        image_url = self._extract_image(product_data)

        return ScrapedProductData(
            title=title,
            current_price=price,
            image_url=image_url,
            currency=currency,
            source_domain="hepsiburada.com",
        )

    # ------------------------------------------------------------------ #
    #  Private helper methods                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_jsonld_product(soup: BeautifulSoup) -> dict | None:
        """
        Find the Product object inside JSON-LD script tags.

        Hepsiburada embeds Product data in a JSON-LD block inside
        a @graph array within the first ld+json script tag.
        """
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
            except (json.JSONDecodeError, TypeError):
                continue

            # Case 1: @graph array containing a Product object
            if isinstance(data, dict) and "@graph" in data:
                for item in data["@graph"]:
                    if isinstance(item, dict) and item.get("@type") == "Product":
                        return item

            # Case 2: Direct Product object
            if isinstance(data, dict) and data.get("@type") == "Product":
                return data

            # Case 3: Array of objects
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "Product":
                        return item

        return None

    @staticmethod
    def _extract_price(product_data: dict) -> float | None:
        """Extract price from the offers field of the Product JSON-LD."""
        offers = product_data.get("offers", {})

        # Offers can be a single dict or a list
        if isinstance(offers, list):
            offers = offers[0] if offers else {}

        price_str = offers.get("price")
        if price_str is not None:
            try:
                # Handle both "37999.00" and "37999,00" formats
                cleaned = str(price_str).replace(",", ".")
                return float(cleaned)
            except (ValueError, TypeError):
                pass

        return None

    @staticmethod
    def _extract_currency(product_data: dict) -> str:
        """Extract currency from the offers field."""
        offers = product_data.get("offers", {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        return offers.get("priceCurrency", "TRY")

    @staticmethod
    def _extract_image(product_data: dict) -> str | None:
        """Extract the first product image URL."""
        image = product_data.get("image")
        if isinstance(image, list) and image:
            return image[0]
        if isinstance(image, str):
            return image
        return None
