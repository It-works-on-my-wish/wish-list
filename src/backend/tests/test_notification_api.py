"""
API-level tests for notification endpoints:
  GET  /users/{user_id}/notifications         — list notifications
  PUT  /notifications/{notification_id}/read  — mark single notification read
  PUT  /users/{user_id}/notifications/read    — mark all notifications read
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TEST_USER_ID = uuid4()
TEST_NOTIFICATION_ID = uuid4()


def make_notification(user_id=None, is_read=False):
    return {
        "id": str(uuid4()),
        "user_id": str(user_id or TEST_USER_ID),
        "product_id": str(uuid4()),
        "message": "Fiyat düştü!",
        "is_read": is_read,
        "created_at": datetime.now().isoformat(),
    }


# ------------------------------------------------------------------ #
#  GET /users/{user_id}/notifications                                  #
# ------------------------------------------------------------------ #

class TestGetUserNotificationsEndpoint:

    def test_returns_200(self):
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.limit.return_value.execute.return_value.data = []
            response = client.get(f"/users/{TEST_USER_ID}/notifications")
        assert response.status_code == 200

    def test_response_is_list(self):
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.limit.return_value.execute.return_value.data = []
            response = client.get(f"/users/{TEST_USER_ID}/notifications")
        assert isinstance(response.json(), list)

    def test_returns_notifications_for_user(self):
        notifications = [make_notification(), make_notification()]
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.limit.return_value.execute.return_value.data = notifications
            response = client.get(f"/users/{TEST_USER_ID}/notifications")
        assert len(response.json()) == 2

    def test_notification_has_message_field(self):
        notifications = [make_notification()]
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.limit.return_value.execute.return_value.data = notifications
            response = client.get(f"/users/{TEST_USER_ID}/notifications")
        assert "message" in response.json()[0]

    def test_notification_has_is_read_field(self):
        notifications = [make_notification()]
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.limit.return_value.execute.return_value.data = notifications
            response = client.get(f"/users/{TEST_USER_ID}/notifications")
        assert "is_read" in response.json()[0]

    def test_returns_500_on_supabase_error(self):
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.side_effect = Exception("DB error")
            response = client.get(f"/users/{TEST_USER_ID}/notifications")
        assert response.status_code == 500

    def test_invalid_user_id_returns_422(self):
        response = client.get("/users/not-a-uuid/notifications")
        assert response.status_code == 422

    def test_unread_notifications_have_is_read_false(self):
        notifications = [make_notification(is_read=False)]
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.select.return_value.eq.return_value\
                .order.return_value.limit.return_value.execute.return_value.data = notifications
            response = client.get(f"/users/{TEST_USER_ID}/notifications")
        assert response.json()[0]["is_read"] is False


# ------------------------------------------------------------------ #
#  PUT /notifications/{notification_id}/read                           #
# ------------------------------------------------------------------ #

class TestMarkNotificationReadEndpoint:

    def test_returns_200_on_success(self):
        notif = make_notification(is_read=True)
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.update.return_value.eq.return_value\
                .execute.return_value.data = [notif]
            response = client.put(f"/notifications/{TEST_NOTIFICATION_ID}/read")
        assert response.status_code == 200

    def test_response_is_read_true(self):
        notif = make_notification(is_read=True)
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.update.return_value.eq.return_value\
                .execute.return_value.data = [notif]
            response = client.put(f"/notifications/{TEST_NOTIFICATION_ID}/read")
        assert response.json()["is_read"] is True

    def test_returns_404_when_notification_not_found(self):
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.update.return_value.eq.return_value\
                .execute.return_value.data = []
            response = client.put(f"/notifications/{TEST_NOTIFICATION_ID}/read")
        assert response.status_code == 404

    def test_returns_500_on_supabase_error(self):
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.side_effect = Exception("DB error")
            response = client.put(f"/notifications/{TEST_NOTIFICATION_ID}/read")
        assert response.status_code == 500

    def test_invalid_notification_id_returns_422(self):
        response = client.put("/notifications/not-a-uuid/read")
        assert response.status_code == 422

    def test_updates_is_read_field_in_supabase(self):
        notif = make_notification(is_read=True)
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.update.return_value.eq.return_value\
                .execute.return_value.data = [notif]
            client.put(f"/notifications/{TEST_NOTIFICATION_ID}/read")
            mock_supa.table.return_value.update.assert_called_once_with({"is_read": True})


# ------------------------------------------------------------------ #
#  PUT /users/{user_id}/notifications/read                             #
# ------------------------------------------------------------------ #

class TestMarkAllNotificationsReadEndpoint:

    def test_returns_200_on_success(self):
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.update.return_value.eq.return_value\
                .eq.return_value.execute.return_value.data = []
            response = client.put(f"/users/{TEST_USER_ID}/notifications/read")
        assert response.status_code == 200

    def test_response_contains_detail(self):
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.update.return_value.eq.return_value\
                .eq.return_value.execute.return_value.data = []
            response = client.put(f"/users/{TEST_USER_ID}/notifications/read")
        assert "detail" in response.json()

    def test_calls_update_with_is_read_true(self):
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.return_value.update.return_value.eq.return_value\
                .eq.return_value.execute.return_value.data = []
            client.put(f"/users/{TEST_USER_ID}/notifications/read")
            mock_supa.table.return_value.update.assert_called_once_with({"is_read": True})

    def test_returns_500_on_supabase_error(self):
        with patch("app.api.user_router.supabase") as mock_supa:
            mock_supa.table.side_effect = Exception("DB error")
            response = client.put(f"/users/{TEST_USER_ID}/notifications/read")
        assert response.status_code == 500

    def test_invalid_user_id_returns_422(self):
        response = client.put("/users/not-a-uuid/notifications/read")
        assert response.status_code == 422
