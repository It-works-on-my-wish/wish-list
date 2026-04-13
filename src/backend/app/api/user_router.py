from uuid import UUID

from app.database.supabase_client import supabase
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.schemas.notification_schema import NotificationResponse
from app.services.user_service import UserService
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

repository = UserRepository()
service = UserService(repository)


@router.post("/users")
def create_user(user: UserCreate):
    return service.create_user(
        first_name=user.first_name, last_name=user.last_name, email=user.email
    )


@router.get("/users/{user_id}/stats")
def get_user_stats(user_id: UUID):
    products = (
        supabase.table("products")
        .select("*")
        .eq("user_id", str(user_id))
        .execute()
        .data
    )

    tracked = len(products)
    purchased = len([p for p in products if p.get("purchase_state") == "purchased"])

    # Total savings: target_price - current_price toplamı (sadece düşmüşler için)
    total_savings = sum(
        (p["target_price"] - p["current_price"])
        for p in products
        if p.get("target_price")
        and p.get("current_price")
        and p["current_price"] <= p["target_price"]
    )

    # Price drops today: bugün price_history'de fiyatı düşenler
    from datetime import datetime, timezone

    today = datetime.now(timezone.utc).date().isoformat()
    product_ids = [p["id"] for p in products]

    price_drops_today = 0
    if product_ids:
        history = (
            supabase.table("price_history")
            .select("*")
            .gte("checked_at", today)
            .execute()
            .data
        )
        for product in products:
            product_records = [h for h in history if h["product_id"] == product["id"]]
            if len(product_records) >= 2:
                product_records.sort(key=lambda x: x["checked_at"])
                if product_records[-1]["price"] < product_records[0]["price"]:
                    price_drops_today += 1

    return {
        "tracked": tracked,
        "purchased": purchased,
        "total_savings": round(total_savings, 2),
        "price_drops_today": price_drops_today,
    }


@router.get("/users/{user_id}/notifications", response_model=List[NotificationResponse])
def get_user_notifications(user_id: UUID):
    try:
        response = (
            supabase.table("notifications")
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(notification_id: UUID):
    try:
        response = (
            supabase.table("notifications")
            .update({"is_read": True})
            .eq("id", str(notification_id))
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Notification not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{user_id}/notifications/read")
def mark_all_notifications_read(user_id: UUID):
    try:
        response = (
            supabase.table("notifications")
            .update({"is_read": True})
            .eq("user_id", str(user_id))
            .eq("is_read", False)
            .execute()
        )
        return {"detail": f"Marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
