import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime
from app.services.product_service import ProductService
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductScrapeRequest, ProductResponse
from app.scrapers.scraper_strategy import ScrapedProductData
from app.factories.scraper_factory import UnsupportedPlatformError
from app.scrapers.scraper_strategy import ScrapingError


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    return ProductService(mock_repo)


@pytest.fixture
def product_response(user_id):
    return ProductResponse(
        id=uuid4(),
        user_id=user_id,
        name="Test Laptop",
        url="https://www.hepsiburada.com/laptop-p-12345",
        priority="medium",
        check_frequency="daily",
        auto_track=True,
        current_price=15999.99,
        purchase_state="pending",
        created_at=datetime.now(),
    )


class TestAddProduct:

    def test_delegates_to_repository_create_product(self, service, mock_repo, product_response, user_id):
        data = ProductCreate(name="Phone", priority="high", check_frequency="hourly", auto_track=True)
        mock_repo.create_product.return_value = product_response
        service.add_product(user_id, data)
        mock_repo.create_product.assert_called_once_with(user_id, data)

    def test_returns_created_product(self, service, mock_repo, product_response, user_id):
        data = ProductCreate(name="Phone", priority="low", check_frequency="weekly", auto_track=False)
        mock_repo.create_product.return_value = product_response
        result = service.add_product(user_id, data)
        assert result is product_response

    def test_passes_user_id_to_repository(self, service, mock_repo, product_response):
        specific_uid = uuid4()
        data = ProductCreate(name="Watch", priority="medium", check_frequency="daily", auto_track=True)
        mock_repo.create_product.return_value = product_response
        service.add_product(specific_uid, data)
        call_args = mock_repo.create_product.call_args[0]
        assert call_args[0] == specific_uid


class TestAddProductFromUrl:

    def _make_scraper_mock(self, title="Test Product", price=999.0, image=None):
        scraped = ScrapedProductData(title=title, source_domain="hepsiburada.com",
                                     current_price=price, image_url=image)
        mock_strategy = MagicMock()
        mock_strategy.extract_product_data.return_value = scraped
        return mock_strategy

    def test_calls_scraper_factory_with_url(self, service, mock_repo, product_response, user_id):
        mock_strategy = self._make_scraper_mock()
        mock_repo.create_product.return_value = product_response

        with patch("app.services.product_service.ScraperFactory.create_scraper", return_value=mock_strategy) as mock_factory:
            req = ProductScrapeRequest(url="https://www.hepsiburada.com/product-p-12345")
            service.add_product_from_url(user_id, req)
            mock_factory.assert_called_once_with("https://www.hepsiburada.com/product-p-12345")

    def test_strategy_extract_is_called(self, service, mock_repo, product_response, user_id):
        mock_strategy = self._make_scraper_mock()
        mock_repo.create_product.return_value = product_response

        with patch("app.services.product_service.ScraperFactory.create_scraper", return_value=mock_strategy):
            req = ProductScrapeRequest(url="https://www.hepsiburada.com/product-p-12345")
            service.add_product_from_url(user_id, req)
            mock_strategy.extract_product_data.assert_called_once()

    def test_product_create_uses_scraped_title(self, service, mock_repo, product_response, user_id):
        mock_strategy = self._make_scraper_mock(title="Scraped Title")
        mock_repo.create_product.return_value = product_response

        with patch("app.services.product_service.ScraperFactory.create_scraper", return_value=mock_strategy):
            req = ProductScrapeRequest(url="https://www.hepsiburada.com/product-p-12345")
            service.add_product_from_url(user_id, req)
            _, product_arg = mock_repo.create_product.call_args[0]
            assert product_arg.name == "Scraped Title"

    def test_product_create_uses_scraped_price(self, service, mock_repo, product_response, user_id):
        mock_strategy = self._make_scraper_mock(price=29999.0)
        mock_repo.create_product.return_value = product_response

        with patch("app.services.product_service.ScraperFactory.create_scraper", return_value=mock_strategy):
            req = ProductScrapeRequest(url="https://www.hepsiburada.com/product-p-12345")
            service.add_product_from_url(user_id, req)
            _, product_arg = mock_repo.create_product.call_args[0]
            assert product_arg.current_price == 29999.0

    def test_product_create_uses_scraped_image(self, service, mock_repo, product_response, user_id):
        img_url = "https://cdn.hepsiburada.com/img.jpg"
        mock_strategy = self._make_scraper_mock(image=img_url)
        mock_repo.create_product.return_value = product_response

        with patch("app.services.product_service.ScraperFactory.create_scraper", return_value=mock_strategy):
            req = ProductScrapeRequest(url="https://www.hepsiburada.com/product-p-12345")
            service.add_product_from_url(user_id, req)
            _, product_arg = mock_repo.create_product.call_args[0]
            assert product_arg.image_url == img_url

    def test_unsupported_platform_error_propagates(self, service, mock_repo, user_id):
        with patch("app.services.product_service.ScraperFactory.create_scraper",
                   side_effect=UnsupportedPlatformError("No scraper for domain")):
            req = ProductScrapeRequest(url="https://www.hepsiburada.com/product-p-12345")
            with pytest.raises(UnsupportedPlatformError):
                service.add_product_from_url(user_id, req)

    def test_scraping_error_propagates(self, service, mock_repo, user_id):
        mock_strategy = MagicMock()
        mock_strategy.extract_product_data.side_effect = ScrapingError("Page not found")

        with patch("app.services.product_service.ScraperFactory.create_scraper", return_value=mock_strategy):
            req = ProductScrapeRequest(url="https://www.hepsiburada.com/product-p-12345")
            with pytest.raises(ScrapingError):
                service.add_product_from_url(user_id, req)


class TestGetUserProducts:

    def test_delegates_to_repository(self, service, mock_repo, user_id):
        mock_repo.get_products_by_user.return_value = []
        service.get_user_products(user_id)
        mock_repo.get_products_by_user.assert_called_once_with(user_id)

    def test_returns_products_list(self, service, mock_repo, product_response, user_id):
        mock_repo.get_products_by_user.return_value = [product_response]
        result = service.get_user_products(user_id)
        assert result == [product_response]

    def test_returns_empty_list_when_no_products(self, service, mock_repo, user_id):
        mock_repo.get_products_by_user.return_value = []
        result = service.get_user_products(user_id)
        assert result == []


class TestUpdateProductDetails:

    def test_delegates_to_repository(self, service, mock_repo, product_response):
        product_id = uuid4()
        update_data = ProductUpdate(name="Updated Name")
        mock_repo.update_product.return_value = product_response
        service.update_product_details(product_id, update_data)
        mock_repo.update_product.assert_called_once_with(product_id, update_data)

    def test_returns_updated_product(self, service, mock_repo, product_response):
        mock_repo.update_product.return_value = product_response
        result = service.update_product_details(uuid4(), ProductUpdate(name="New Name"))
        assert result is product_response


class TestRemoveProduct:

    def test_delegates_to_repository(self, service, mock_repo):
        product_id = uuid4()
        service.remove_product(product_id)
        mock_repo.delete_product.assert_called_once_with(product_id)

    def test_does_not_call_other_methods(self, service, mock_repo):
        service.remove_product(uuid4())
        mock_repo.create_product.assert_not_called()
        mock_repo.get_products_by_user.assert_not_called()
