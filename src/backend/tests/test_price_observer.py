"""
Unit tests for the Observer pattern implementation:
  - PriceMonitor (PriceSubject concrete class)
  - TargetPriceNotificationObserver (PriceObserver concrete class)

All Supabase calls are mocked — no real DB interaction.
"""

import pytest
from unittest.mock import MagicMock, patch, call
from uuid import uuid4

from app.observers.price_observer import (
    PriceMonitor,
    TargetPriceNotificationObserver,
    PriceObserver,
    PriceSubject,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_product(name="Laptop", price=5000.0, target_price=4000.0, user_id=None):
    return {
        "id": str(uuid4()),
        "user_id": str(user_id or uuid4()),
        "name": name,
        "current_price": price,
        "target_price": target_price,
    }


# ---------------------------------------------------------------------------
# PriceMonitor — attach / detach / notify
# ---------------------------------------------------------------------------

class TestPriceMonitorAttach:

    def test_attach_adds_observer(self):
        monitor = PriceMonitor()
        obs = MagicMock(spec=PriceObserver)
        monitor.attach(obs)
        assert obs in monitor._observers

    def test_attach_same_observer_twice_is_idempotent(self):
        monitor = PriceMonitor()
        obs = MagicMock(spec=PriceObserver)
        monitor.attach(obs)
        monitor.attach(obs)
        assert monitor._observers.count(obs) == 1

    def test_attach_multiple_observers(self):
        monitor = PriceMonitor()
        obs1, obs2 = MagicMock(spec=PriceObserver), MagicMock(spec=PriceObserver)
        monitor.attach(obs1)
        monitor.attach(obs2)
        assert len(monitor._observers) == 2


class TestPriceMonitorDetach:

    def test_detach_removes_observer(self):
        monitor = PriceMonitor()
        obs = MagicMock(spec=PriceObserver)
        monitor.attach(obs)
        monitor.detach(obs)
        assert obs not in monitor._observers

    def test_detach_non_attached_observer_does_not_raise(self):
        monitor = PriceMonitor()
        obs = MagicMock(spec=PriceObserver)
        monitor.detach(obs)  # should not raise

    def test_detach_only_removes_target_observer(self):
        monitor = PriceMonitor()
        obs1, obs2 = MagicMock(spec=PriceObserver), MagicMock(spec=PriceObserver)
        monitor.attach(obs1)
        monitor.attach(obs2)
        monitor.detach(obs1)
        assert obs2 in monitor._observers
        assert obs1 not in monitor._observers


class TestPriceMonitorNotify:

    def test_notify_calls_update_on_all_observers(self):
        monitor = PriceMonitor()
        obs1, obs2 = MagicMock(spec=PriceObserver), MagicMock(spec=PriceObserver)
        monitor.attach(obs1)
        monitor.attach(obs2)
        product = make_product()
        monitor.notify(product, 5000.0, 4500.0)
        obs1.update.assert_called_once_with(product, 5000.0, 4500.0)
        obs2.update.assert_called_once_with(product, 5000.0, 4500.0)

    def test_notify_with_no_observers_does_not_raise(self):
        monitor = PriceMonitor()
        monitor.notify(make_product(), 5000.0, 4500.0)

    def test_notify_passes_correct_old_and_new_price(self):
        monitor = PriceMonitor()
        obs = MagicMock(spec=PriceObserver)
        monitor.attach(obs)
        product = make_product()
        monitor.notify(product, 9999.0, 7500.0)
        _, old, new = obs.update.call_args[0]
        assert old == 9999.0
        assert new == 7500.0

    def test_notify_passes_correct_product(self):
        monitor = PriceMonitor()
        obs = MagicMock(spec=PriceObserver)
        monitor.attach(obs)
        product = make_product(name="Phone")
        monitor.notify(product, 1000.0, 900.0)
        called_product = obs.update.call_args[0][0]
        assert called_product["name"] == "Phone"


# ---------------------------------------------------------------------------
# PriceMonitor — interface conformance
# ---------------------------------------------------------------------------

class TestPriceMonitorInterface:

    def test_price_monitor_is_price_subject(self):
        assert issubclass(PriceMonitor, PriceSubject)

    def test_new_monitor_has_empty_observer_list(self):
        monitor = PriceMonitor()
        assert monitor._observers == []


# ---------------------------------------------------------------------------
# TargetPriceNotificationObserver
# ---------------------------------------------------------------------------

class TestTargetPriceNotificationObserverInterface:

    def test_is_price_observer(self):
        assert issubclass(TargetPriceNotificationObserver, PriceObserver)

    def test_update_method_exists(self):
        obs = TargetPriceNotificationObserver()
        assert callable(obs.update)


class TestTargetPriceNotificationObserverUpdate:

    def test_sends_notification_when_price_drops_to_target(self):
        obs = TargetPriceNotificationObserver()
        product = make_product(price=5000.0, target_price=4000.0)
        with patch("app.observers.price_observer.supabase") as mock_supa:
            obs.update(product, old_price=5000.0, new_price=3999.0)
            mock_supa.table.return_value.insert.assert_called_once()

    def test_does_not_notify_when_price_above_target(self):
        obs = TargetPriceNotificationObserver()
        product = make_product(price=5000.0, target_price=4000.0)
        with patch("app.observers.price_observer.supabase") as mock_supa:
            obs.update(product, old_price=5000.0, new_price=4500.0)
            mock_supa.table.return_value.insert.assert_not_called()

    def test_does_not_notify_when_target_price_is_none(self):
        obs = TargetPriceNotificationObserver()
        product = make_product()
        product["target_price"] = None
        with patch("app.observers.price_observer.supabase") as mock_supa:
            obs.update(product, old_price=5000.0, new_price=3000.0)
            mock_supa.table.return_value.insert.assert_not_called()

    def test_does_not_spam_when_old_price_already_below_target(self):
        """If old_price was already <= target_price, no new notification should fire."""
        obs = TargetPriceNotificationObserver()
        product = make_product(target_price=4000.0)
        with patch("app.observers.price_observer.supabase") as mock_supa:
            obs.update(product, old_price=3500.0, new_price=3400.0)
            mock_supa.table.return_value.insert.assert_not_called()

    def test_notification_contains_correct_user_id(self):
        obs = TargetPriceNotificationObserver()
        uid = str(uuid4())
        product = make_product(target_price=4000.0, user_id=uid)
        product["user_id"] = uid
        with patch("app.observers.price_observer.supabase") as mock_supa:
            obs.update(product, old_price=5000.0, new_price=3999.0)
            inserted = mock_supa.table.return_value.insert.call_args[0][0]
            assert inserted["user_id"] == uid

    def test_notification_contains_correct_product_id(self):
        obs = TargetPriceNotificationObserver()
        product = make_product(target_price=4000.0)
        pid = product["id"]
        with patch("app.observers.price_observer.supabase") as mock_supa:
            obs.update(product, old_price=5000.0, new_price=3999.0)
            inserted = mock_supa.table.return_value.insert.call_args[0][0]
            assert inserted["product_id"] == pid

    def test_notification_is_unread_by_default(self):
        obs = TargetPriceNotificationObserver()
        product = make_product(target_price=4000.0)
        with patch("app.observers.price_observer.supabase") as mock_supa:
            obs.update(product, old_price=5000.0, new_price=3999.0)
            inserted = mock_supa.table.return_value.insert.call_args[0][0]
            assert inserted["is_read"] is False

    def test_notification_message_contains_product_name(self):
        obs = TargetPriceNotificationObserver()
        product = make_product(name="MacBook Pro", target_price=40000.0)
        with patch("app.observers.price_observer.supabase") as mock_supa:
            obs.update(product, old_price=50000.0, new_price=39999.0)
            inserted = mock_supa.table.return_value.insert.call_args[0][0]
            assert "MacBook Pro" in inserted["message"]

    def test_does_not_raise_when_supabase_fails(self):
        obs = TargetPriceNotificationObserver()
        product = make_product(target_price=4000.0)
        with patch("app.observers.price_observer.supabase") as mock_supa:
            mock_supa.table.side_effect = Exception("DB error")
            obs.update(product, old_price=5000.0, new_price=3999.0)  # should not raise

    def test_notifies_when_old_price_is_none(self):
        """First-time scrape (no old price) should still notify if below target."""
        obs = TargetPriceNotificationObserver()
        product = make_product(target_price=4000.0)
        with patch("app.observers.price_observer.supabase") as mock_supa:
            obs.update(product, old_price=None, new_price=3999.0)
            mock_supa.table.return_value.insert.assert_called_once()

    def test_notifies_exactly_at_target_price(self):
        obs = TargetPriceNotificationObserver()
        product = make_product(target_price=4000.0)
        with patch("app.observers.price_observer.supabase") as mock_supa:
            obs.update(product, old_price=5000.0, new_price=4000.0)
            mock_supa.table.return_value.insert.assert_called_once()
