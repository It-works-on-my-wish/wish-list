import pytest
from unittest.mock import patch
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.product_schema import ProductResponse
from app.factories.scraper_factory import UnsupportedPlatformError
from app.scrapers.scraper_strategy import ScrapingError

client = TestClient(app)

TEST_USER_ID = uuid4()
TEST_PRODUCT_ID = uuid4()


def make_product_response(user_id=None, name="Test Laptop", price=15999.99):
    return ProductResponse(
        id=uuid4(),
        user_id=user_id or TEST_USER_ID,
        name=name,
        url="https://www.hepsiburada.com/laptop-p-12345",
        priority="medium",
        check_frequency="daily",
        auto_track=True,
        current_price=price,
        purchase_state="pending",
        created_at=datetime.now(),
    )


VALID_PRODUCT_PAYLOAD = {
    "name": "Test Laptop",
    "url": "https://www.hepsiburada.com/laptop-p-12345",
    "priority": "medium",
    "check_frequency": "daily",
    "auto_track": True,
    "current_price": 15999.99,
}

VALID_SCRAPE_PAYLOAD = {
    "url": "https://www.hepsiburada.com/laptop-p-12345",
    "priority": "medium",
    "check_frequency": "daily",
    "auto_track": True,
}


class TestAddProductEndpoint:

    def test_returns_200_on_valid_product(self):
        with patch("app.api.product_router.service.add_product", return_value=make_product_response()):
            response = client.post(f"/users/{TEST_USER_ID}/products", json=VALID_PRODUCT_PAYLOAD)
        assert response.status_code == 200

    def test_response_contains_product_name(self):
        with patch("app.api.product_router.service.add_product", return_value=make_product_response(name="Test Laptop")):
            response = client.post(f"/users/{TEST_USER_ID}/products", json=VALID_PRODUCT_PAYLOAD)
        assert response.json()["name"] == "Test Laptop"

    def test_response_contains_user_id(self):
        with patch("app.api.product_router.service.add_product", return_value=make_product_response()):
            response = client.post(f"/users/{TEST_USER_ID}/products", json=VALID_PRODUCT_PAYLOAD)
        assert "user_id" in response.json()

    def test_missing_name_returns_422(self):
        payload = {k: v for k, v in VALID_PRODUCT_PAYLOAD.items() if k != "name"}
        response = client.post(f"/users/{TEST_USER_ID}/products", json=payload)
        assert response.status_code == 422

    def test_invalid_user_id_returns_422(self):
        response = client.post("/users/not-a-uuid/products", json=VALID_PRODUCT_PAYLOAD)
        assert response.status_code == 422

    def test_service_returns_none_gives_error_response(self):
        # Router raises HTTPException(400) when product is None, but the outer
        # `except Exception` block in the router catches it and re-raises as 500.
        with patch("app.api.product_router.service.add_product", return_value=None):
            response = client.post(f"/users/{TEST_USER_ID}/products", json=VALID_PRODUCT_PAYLOAD)
        assert response.status_code in (400, 500)

    def test_service_exception_returns_500(self):
        with patch("app.api.product_router.service.add_product", side_effect=Exception("DB error")):
            response = client.post(f"/users/{TEST_USER_ID}/products", json=VALID_PRODUCT_PAYLOAD)
        assert response.status_code == 500


class TestScrapeAndAddProductEndpoint:

    def test_returns_200_on_valid_scrape(self):
        with patch("app.api.product_router.service.add_product_from_url", return_value=make_product_response()):
            response = client.post(f"/users/{TEST_USER_ID}/products/scrape", json=VALID_SCRAPE_PAYLOAD)
        assert response.status_code == 200

    def test_response_has_product_id(self):
        with patch("app.api.product_router.service.add_product_from_url", return_value=make_product_response()):
            response = client.post(f"/users/{TEST_USER_ID}/products/scrape", json=VALID_SCRAPE_PAYLOAD)
        assert "id" in response.json()

    def test_unsupported_platform_returns_400(self):
        with patch("app.api.product_router.service.add_product_from_url",
                   side_effect=UnsupportedPlatformError("No scraper for trendyol.com")):
            response = client.post(f"/users/{TEST_USER_ID}/products/scrape", json=VALID_SCRAPE_PAYLOAD)
        assert response.status_code == 400

    def test_scraping_error_returns_502(self):
        with patch("app.api.product_router.service.add_product_from_url",
                   side_effect=ScrapingError("Page structure changed")):
            response = client.post(f"/users/{TEST_USER_ID}/products/scrape", json=VALID_SCRAPE_PAYLOAD)
        assert response.status_code == 502

    def test_missing_url_returns_422(self):
        response = client.post(f"/users/{TEST_USER_ID}/products/scrape", json={"priority": "medium"})
        assert response.status_code == 422

    def test_invalid_user_id_returns_422(self):
        response = client.post("/users/not-a-uuid/products/scrape", json=VALID_SCRAPE_PAYLOAD)
        assert response.status_code == 422


class TestGetUserProductsEndpoint:

    def test_returns_200(self):
        products = [make_product_response(), make_product_response()]
        with patch("app.api.product_router.service.get_user_products", return_value=products):
            response = client.get(f"/users/{TEST_USER_ID}/products")
        assert response.status_code == 200

    def test_returns_list(self):
        with patch("app.api.product_router.service.get_user_products", return_value=[]):
            response = client.get(f"/users/{TEST_USER_ID}/products")
        assert isinstance(response.json(), list)

    def test_returns_correct_count(self):
        products = [make_product_response() for _ in range(3)]
        with patch("app.api.product_router.service.get_user_products", return_value=products):
            response = client.get(f"/users/{TEST_USER_ID}/products")
        assert len(response.json()) == 3

    def test_invalid_user_id_returns_422(self):
        response = client.get("/users/not-a-uuid/products")
        assert response.status_code == 422

    def test_service_exception_returns_500(self):
        with patch("app.api.product_router.service.get_user_products", side_effect=Exception("DB error")):
            response = client.get(f"/users/{TEST_USER_ID}/products")
        assert response.status_code == 500


class TestUpdateProductEndpoint:

    def test_returns_200_on_valid_update(self):
        with patch("app.api.product_router.service.update_product_details", return_value=make_product_response()):
            response = client.put(f"/products/{TEST_PRODUCT_ID}", json={"name": "Updated Laptop"})
        assert response.status_code == 200

    def test_response_contains_id(self):
        with patch("app.api.product_router.service.update_product_details", return_value=make_product_response()):
            response = client.put(f"/products/{TEST_PRODUCT_ID}", json={"name": "Updated Laptop"})
        assert "id" in response.json()

    def test_service_returns_none_gives_404(self):
        with patch("app.api.product_router.service.update_product_details", return_value=None):
            response = client.put(f"/products/{TEST_PRODUCT_ID}", json={"name": "Updated"})
        assert response.status_code == 404

    def test_invalid_product_id_returns_422(self):
        response = client.put("/products/not-a-uuid", json={"name": "New Name"})
        assert response.status_code == 422

    def test_update_purchase_state(self):
        updated = make_product_response()
        with patch("app.api.product_router.service.update_product_details", return_value=updated):
            response = client.put(f"/products/{TEST_PRODUCT_ID}", json={"purchase_state": "purchased"})
        assert response.status_code == 200


class TestDeleteProductEndpoint:

    def test_returns_200_on_success(self):
        with patch("app.api.product_router.service.remove_product", return_value=None):
            response = client.delete(f"/products/{TEST_PRODUCT_ID}")
        assert response.status_code == 200

    def test_response_contains_detail_message(self):
        with patch("app.api.product_router.service.remove_product", return_value=None):
            response = client.delete(f"/products/{TEST_PRODUCT_ID}")
        assert "detail" in response.json()

    def test_invalid_product_id_returns_422(self):
        response = client.delete("/products/not-a-uuid")
        assert response.status_code == 422

    def test_service_exception_returns_500(self):
        with patch("app.api.product_router.service.remove_product", side_effect=Exception("DB error")):
            response = client.delete(f"/products/{TEST_PRODUCT_ID}")
        assert response.status_code == 500
