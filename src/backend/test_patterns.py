"""Quick smoke test for Factory + Strategy pattern with Hepsiburada."""
from app.scrapers.scraper_strategy import ScraperStrategy, ScrapedProductData, ScrapingError
from app.scrapers.hepsiburada_scraper import HepsiburadaScraper
from app.factories.scraper_factory import ScraperFactory, UnsupportedPlatformError

# Test 1: Factory returns HepsiburadaScraper for hepsiburada.com URL
strategy = ScraperFactory.create_scraper("https://www.hepsiburada.com/product-p-XXXXX")
print(f"[OK] Factory returned: {type(strategy).__name__}")
assert isinstance(strategy, HepsiburadaScraper), "Expected HepsiburadaScraper"

# Test 2: Factory raises UnsupportedPlatformError for unknown domain
try:
    ScraperFactory.create_scraper("https://ebay.com/item/123")
    print("[FAIL] Should have raised UnsupportedPlatformError")
except UnsupportedPlatformError as e:
    print(f"[OK] Unsupported platform error: {e}")

# Test 3: ScraperStrategy interface check
assert issubclass(HepsiburadaScraper, ScraperStrategy), "HepsiburadaScraper should implement ScraperStrategy"
print(f"[OK] HepsiburadaScraper implements ScraperStrategy interface")

# Test 4: Actually scrape the user's product
print("\n--- Live scraping test ---")
url = "https://www.hepsiburada.com/apple-macbook-neo-a18-pro-8gb-256gb-ssd-macos-13-tasinabilir-bilgisayar-indigo-mhff4tu-a-p-HBCV0000D6UG08?magaza=Hepsiburada&"
strategy = ScraperFactory.create_scraper(url)
result = strategy.extract_product_data(url)
print(f"[OK] Title: {result.title}")
print(f"[OK] Price: {result.current_price} {result.currency}")
print(f"[OK] Image: {result.image_url[:60]}...")
print(f"[OK] Domain: {result.source_domain}")

assert result.title is not None and len(result.title) > 0, "Title should not be empty"
assert result.current_price is not None and result.current_price > 0, "Price should be positive"
assert result.image_url is not None, "Image should not be None"

print("\n=== All tests passed! ===")
