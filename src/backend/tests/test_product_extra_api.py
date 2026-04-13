"""
API-level tests for additional product endpoints not covered in test_product_api.py:
  GET /products/{product_id}/price-history  — price history for a product
  GET /supported-platforms                  — list of supported scraping domains
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TEST_PRODUCT_ID = uuid4()


def make_price_record(product_id=None, price=1000.0):
    return {
        "id": str(uuid4()),
        "product_id": str(product_id or TEST_PRODUCT_ID),
        "price": price,
        "checked_at": datetime.now().isoformat(),
    }


# ------------------------------------------------------------------ #
#  GET /products/{product_id}/price-history                            #
# ------------------------------------------------------------------ #

class TestGetPriceHistoryEndpoint:

    def test_returns_200(self):
        with patch("app.api.product_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.execute.return_value.data = []
            response = client.get(f"/products/{TEST_PRODUCT_ID}/price-history")
        assert response.status_code == 200

    def test_response_is_list(self):
        with patch("app.api.product_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.execute.return_value.data = []
            response = client.get(f"/products/{TEST_PRODUCT_ID}/price-history")
        assert isinstance(response.json(), list)

    def test_returns_correct_number_of_records(self):
        records = [make_price_record() for _ in range(4)]
        with patch("app.api.product_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.execute.return_value.data = records
            response = client.get(f"/products/{TEST_PRODUCT_ID}/price-history")
        assert len(response.json()) == 4

    def test_record_contains_price_field(self):
        records = [make_price_record(price=1500.0)]
        with patch("app.api.product_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.execute.return_value.data = records
            response = client.get(f"/products/{TEST_PRODUCT_ID}/price-history")
        assert "price" in response.json()[0]

    def test_record_contains_checked_at_field(self):
        records = [make_price_record()]
        with patch("app.api.product_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.execute.return_value.data = records
            response = client.get(f"/products/{TEST_PRODUCT_ID}/price-history")
        assert "checked_at" in response.json()[0]

    def test_returns_empty_list_when_no_history(self):
        with patch("app.api.product_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.execute.return_value.data = []
            response = client.get(f"/products/{TEST_PRODUCT_ID}/price-history")
        assert response.json() == []

    def test_invalid_product_id_returns_422(self):
        response = client.get("/products/not-a-uuid/price-history")
        assert response.status_code == 422

    def test_price_values_are_numeric(self):
        records = [make_price_record(price=2999.99)]
        with patch("app.api.product_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.execute.return_value.data = records
            response = client.get(f"/products/{TEST_PRODUCT_ID}/price-history")
        assert isinstance(response.json()[0]["price"], (int, float))


# ------------------------------------------------------------------ #
#  GET /supported-platforms                                            #
# ------------------------------------------------------------------ #

class TestSupportedPlatformsEndpoint:

    def test_returns_200(self):
        response = client.get("/supported-platforms")
        assert response.status_code == 200

    def test_response_contains_platforms_key(self):
        response = client.get("/supported-platforms")
        assert "platforms" in response.json()

    def test_platforms_is_list(self):
        response = client.get("/supported-platforms")
        assert isinstance(response.json()["platforms"], list)

    def test_platforms_list_is_not_empty(self):
        response = client.get("/supported-platforms")
        assert len(response.json()["platforms"]) > 0

    def test_hepsiburada_in_platforms(self):
        response = client.get("/supported-platforms")
        platforms = response.json()["platforms"]
        assert any("hepsiburada" in p for p in platforms)

    def test_trendyol_in_platforms(self):
        response = client.get("/supported-platforms")
        platforms = response.json()["platforms"]
        assert any("trendyol" in p for p in platforms)

    def test_amazon_in_platforms(self):
        response = client.get("/supported-platforms")
        platforms = response.json()["platforms"]
        assert any("amazon" in p for p in platforms)

    def test_platforms_are_strings(self):
        response = client.get("/supported-platforms")
        platforms = response.json()["platforms"]
        assert all(isinstance(p, str) for p in platforms)
