from abc import ABC, abstractmethod
from typing import Any, Dict

from app.database.supabase_client import supabase


class PriceObserver(ABC):
    """Observer interface for price monitoring."""

    @abstractmethod
    def update(self, product: dict, old_price: float | None, new_price: float) -> None:
        pass


class PriceSubject(ABC):
    """Subject interface for price monitoring."""

    @abstractmethod
    def attach(self, observer: PriceObserver) -> None:
        pass

    @abstractmethod
    def detach(self, observer: PriceObserver) -> None:
        pass

    @abstractmethod
    def notify(self, product: dict, old_price: float | None, new_price: float) -> None:
        pass


class PriceMonitor(PriceSubject):
    """Concrete subject implementation for price changes."""

    def __init__(self):
        self._observers: list[PriceObserver] = []

    def attach(self, observer: PriceObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: PriceObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, product: dict, old_price: float | None, new_price: float) -> None:
        for observer in self._observers:
            observer.update(product, old_price, new_price)


class TargetPriceNotificationObserver(PriceObserver):
    """Observer that checks if the new price meets the target price and sends a notification."""

    def update(self, product: dict, old_price: float | None, new_price: float) -> None:
        target_price = product.get("target_price")
        if target_price is None or new_price is None:
            return

        # Explicitly ignore cases where old price was already smaller to prevent spam,
        # but for simplicity, we report any target drop if it's currently at or below target.
        # Ideally, we only notify if it crossed the threshold, or if old_price > target_price.
        if (old_price is None or float(old_price) > float(target_price)) and float(new_price) <= float(target_price):
            product_name = product.get("name", "A tracked product")
            message = f"Düşüş Alarmı: {product_name} fiyatı hedeflenen ₺{float(target_price)} seviyesine (veya altına) indi! Güncel Fiyat: ₺{new_price}"
            
            try:
                supabase.table("notifications").insert(
                    {
                        "user_id": product["user_id"],
                        "product_id": product["id"],
                        "message": message,
                        "is_read": False,
                    }
                ).execute()
                print(f"[{product_name}] Notification created in database.")
            except Exception as e:
                print(f"Failed to create notification for {product_name}: {e}")
