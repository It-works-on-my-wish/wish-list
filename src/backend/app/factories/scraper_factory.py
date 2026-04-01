from urllib.parse import urlparse

from app.scrapers.amazon_scraper import AmazonScraper
from app.scrapers.boyner_scraper import BoynerScraper
from app.scrapers.hepsiburada_scraper import HepsiburadaScraper
from app.scrapers.mediamarkt_scraper import MediaMarktScraper
from app.scrapers.scraper_strategy import ScraperStrategy
from app.scrapers.trendyol_scraper import TrendyolScraper


class UnsupportedPlatformError(Exception):
    """Raised when the URL domain is not supported by any scraper."""

    pass


class ScraperFactory:
    """
    Factory Pattern: creates the appropriate ScraperStrategy based on the URL domain.

    Usage:
        strategy = ScraperFactory.create_scraper("https://www.hepsiburada.com/product-p-XXXX")
        product_data = strategy.extract_product_data(url)

    The factory inspects the domain of the given URL and returns
    the matching concrete strategy instance. The caller doesn't need
    to know which scraper class was instantiated — it just uses the
    common ScraperStrategy interface.
    """

    # Map of domain keywords to their scraper strategy constructors.
    # To add a new platform, simply register it here.
    _DOMAIN_REGISTRY: dict[str, type[ScraperStrategy]] = {
        "hepsiburada": HepsiburadaScraper,
        "trendyol": TrendyolScraper,
        "amazon": AmazonScraper,
        "boyner": BoynerScraper,
        "mediamarkt": MediaMarktScraper,
    }

    @staticmethod
    def create_scraper(url: str) -> ScraperStrategy:
        """
        Parse the URL domain and return the appropriate scraper strategy.

        Args:
            url: The full product URL string.

        Returns:
            An instantiated ScraperStrategy for the detected platform.

        Raises:
            UnsupportedPlatformError: If no scraper matches the URL domain.
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove common prefixes like 'www.'
        if domain.startswith("www."):
            domain = domain[4:]

        # Check each registered domain keyword against the actual domain
        for keyword, scraper_class in ScraperFactory._DOMAIN_REGISTRY.items():
            if keyword in domain:
                return scraper_class()

        supported = ", ".join(ScraperFactory._DOMAIN_REGISTRY.keys())
        raise UnsupportedPlatformError(
            f"No scraper available for domain '{parsed.netloc}'. "
            f"Supported platforms: {supported}"
        )
