from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScrapedProductData:
    """
    Standard data container returned by all scraper strategies.
    Every scraper must populate at least `title` and `source_domain`.
    Fields like `current_price` and `image_url` are optional because
    not every platform may expose them.
    """
    title: str
    source_domain: str
    current_price: Optional[float] = None
    image_url: Optional[str] = None
    currency: str = "USD"


class ScraperStrategy(ABC):
    """
    Strategy Interface.

    Declares the `extract_product_data` method that all concrete
    scraper strategies must implement. The core application calls
    this method without knowing which concrete scraper is executing.
    """

    @abstractmethod
    def extract_product_data(self, url: str) -> ScrapedProductData:
        """
        Scrape the given product URL and return standardized product data.

        Args:
            url: The full product URL to scrape.

        Returns:
            ScrapedProductData with the extracted information.

        Raises:
            ScrapingError: If the product data cannot be extracted.
        """
        pass


class ScrapingError(Exception):
    """Raised when a scraper strategy fails to extract product data."""
    pass
