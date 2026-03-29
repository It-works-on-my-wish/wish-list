from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductScrapeRequest
from app.factories.scraper_factory import ScraperFactory
from uuid import UUID


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def add_product(self, user_id: UUID, product_data: ProductCreate):
        """Add a product with manually provided data (no scraping)."""
        return self.repository.create_product(user_id, product_data)

    def add_product_from_url(self, user_id: UUID, scrape_request: ProductScrapeRequest):
        """
        Add a product by scraping its URL using the Factory + Strategy pattern.

        Flow:
        1. ScraperFactory parses the URL domain and creates the right scraper strategy
        2. The strategy's extract_product_data() scrapes the page
        3. Scraped data is merged with user preferences into a ProductCreate
        4. The product is saved to the database
        """
        url_str = str(scrape_request.url)

        # --- Factory creates the appropriate strategy ---
        strategy = ScraperFactory.create_scraper(url_str)

        # --- Strategy extracts the product data ---
        scraped = strategy.extract_product_data(url_str)

        # --- Build ProductCreate from scraped data + user preferences ---
        product_data = ProductCreate(
            name=scraped.title,
            url=scrape_request.url,
            category_id=scrape_request.category_id,
            priority=scrape_request.priority,
            check_frequency=scrape_request.check_frequency,
            auto_track=scrape_request.auto_track,
            current_price=scraped.current_price,
            target_price=scrape_request.target_price,
            image_url=scraped.image_url,
        )

        return self.repository.create_product(user_id, product_data)

    def get_user_products(self, user_id: UUID):
        return self.repository.get_products_by_user(user_id)

    def update_product_details(self, product_id: UUID, product_data: ProductUpdate):
        return self.repository.update_product(product_id, product_data)
        
    def remove_product(self, product_id: UUID):
        return self.repository.delete_product(product_id)
