"""
API-level tests for user endpoints:
  POST /users          — create a new user
  GET  /users/{id}/stats — dashboard statistics
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.user_schema import UserRead

client = TestClient(app)

TEST_USER_ID = uuid4()


def make_user_read(first_name="Ali", last_name="Veli", email="ali@test.com"):
    return UserRead(
        id=uuid4(),
        first_name=first_name,
        last_name=last_name,
        email=email,
        created_at=datetime.now(),
    )


def make_supabase_product(user_id, name="Phone", price=1000.0, target=1200.0, state="pending"):
    return {
        "id": str(uuid4()),
        "user_id": str(user_id),
        "name": name,
        "current_price": price,
        "target_price": target,
        "purchase_state": state,
    }


# ------------------------------------------------------------------ #
#  POST /users                                                         #
# ------------------------------------------------------------------ #

class TestCreateUserEndpoint:

    def test_returns_200_on_valid_request(self):
        with patch("app.api.user_router.service.create_user", return_value=make_user_read()):
            response = client.post("/users", json={
                "first_name": "Ali", "last_name": "Veli", "email": "ali@test.com"
            })
        assert response.status_code == 200

    def test_response_contains_email(self):
        with patch("app.api.user_router.service.create_user", return_value=make_user_read(email="test@test.com")):
            response = client.post("/users", json={
                "first_name": "Test", "last_name": "User", "email": "test@test.com"
            })
        assert response.json()["email"] == "test@test.com"

    def test_missing_first_name_returns_422(self):
        response = client.post("/users", json={"last_name": "Veli", "email": "a@b.com"})
        assert response.status_code == 422

    def test_missing_last_name_returns_422(self):
        response = client.post("/users", json={"first_name": "Ali", "email": "a@b.com"})
        assert response.status_code == 422

    def test_missing_email_returns_422(self):
        response = client.post("/users", json={"first_name": "Ali", "last_name": "Veli"})
        assert response.status_code == 422

    def test_empty_body_returns_422(self):
        response = client.post("/users", json={})
        assert response.status_code == 422

    def test_service_called_with_correct_args(self):
        with patch("app.api.user_router.service.create_user", return_value=make_user_read()) as mock_svc:
            client.post("/users", json={"first_name": "Elif", "last_name": "Çelik", "email": "elif@test.com"})
            mock_svc.assert_called_once_with(
                first_name="Elif", last_name="Çelik", email="elif@test.com"
            )


# ------------------------------------------------------------------ #
#  GET /users/{user_id}/stats                                          #
# ------------------------------------------------------------------ #

def setup_stats_mock(mock_supa, products, price_history=None):
    """Helper to wire up the supabase mock chain for the stats endpoint."""
    price_history = price_history or []

    def table_side_effect(table_name):
        m = MagicMock()
        if table_name == "products":
            m.select.return_value.eq.return_value.execute.return_value.data = products
        elif table_name == "price_history":
            m.select.return_value.gte.return_value.execute.return_value.data = price_history
        return m

    mock_supa.table.side_effect = table_side_effect


class TestUserStatsEndpoint:

    def test_returns_200(self):
        with patch("app.api.user_router.supabase") as mock_supa:
            setup_stats_mock(mock_supa, [])
            response = client.get(f"/users/{TEST_USER_ID}/stats")
        assert response.status_code == 200

    def test_response_has_required_fields(self):
        with patch("app.api.user_router.supabase") as mock_supa:
            setup_stats_mock(mock_supa, [])
            response = client.get(f"/users/{TEST_USER_ID}/stats")
        body = response.json()
        assert "tracked" in body
        assert "purchased" in body
        assert "total_savings" in body
        assert "price_drops_today" in body

    def test_tracked_count_equals_product_count(self):
        products = [make_supabase_product(TEST_USER_ID) for _ in range(3)]
        with patch("app.api.user_router.supabase") as mock_supa:
            setup_stats_mock(mock_supa, products)
            response = client.get(f"/users/{TEST_USER_ID}/stats")
        assert response.json()["tracked"] == 3

    def test_purchased_count_filters_by_state(self):
        products = [
            make_supabase_product(TEST_USER_ID, state="purchased"),
            make_supabase_product(TEST_USER_ID, state="purchased"),
            make_supabase_product(TEST_USER_ID, state="pending"),
        ]
        with patch("app.api.user_router.supabase") as mock_supa:
            setup_stats_mock(mock_supa, products)
            response = client.get(f"/users/{TEST_USER_ID}/stats")
        assert response.json()["purchased"] == 2

    def test_total_savings_calculated_for_price_drops(self):
        products = [
            make_supabase_product(TEST_USER_ID, price=800.0, target=1000.0),  # savings = 200
            make_supabase_product(TEST_USER_ID, price=1500.0, target=1000.0),  # no savings (above target)
        ]
        with patch("app.api.user_router.supabase") as mock_supa:
            setup_stats_mock(mock_supa, products)
            response = client.get(f"/users/{TEST_USER_ID}/stats")
        assert response.json()["total_savings"] == 200.0

    def test_total_savings_zero_when_no_products(self):
        with patch("app.api.user_router.supabase") as mock_supa:
            setup_stats_mock(mock_supa, [])
            response = client.get(f"/users/{TEST_USER_ID}/stats")
        assert response.json()["total_savings"] == 0.0

    def test_price_drops_today_counted_correctly(self):
        pid = str(uuid4())
        products = [{"id": pid, "user_id": str(TEST_USER_ID), "name": "Phone",
                     "current_price": 900.0, "target_price": 1000.0, "purchase_state": "pending"}]
        history = [
            {"product_id": pid, "price": 1000.0, "checked_at": "2026-04-09T08:00:00"},
            {"product_id": pid, "price": 900.0,  "checked_at": "2026-04-09T12:00:00"},
        ]
        with patch("app.api.user_router.supabase") as mock_supa:
            setup_stats_mock(mock_supa, products, history)
            response = client.get(f"/users/{TEST_USER_ID}/stats")
        assert response.json()["price_drops_today"] == 1

    def test_invalid_user_id_returns_422(self):
        response = client.get("/users/not-a-uuid/stats")
        assert response.status_code == 422
