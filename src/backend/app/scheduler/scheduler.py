from datetime import datetime, timezone, timedelta
from app.database.supabase_client import supabase
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.observers.price_observer import PriceMonitor, TargetPriceNotificationObserver

price_monitor = PriceMonitor()
price_monitor.attach(TargetPriceNotificationObserver())


def check_prices():
    print("Checking prices...")
    try:
        products = (
            supabase.table("products").select("*").eq("auto_track", True).execute().data
        )
        for product in products:
            if not product.get("url"):
                continue

            # Determine check frequency
            freq = product.get("check_frequency", "daily")
            
            # Fetch last check time
            history = supabase.table("price_history").select("checked_at").eq("product_id", product["id"]).order("checked_at", desc=True).limit(1).execute().data
            
            should_check = True
            if history and history[0].get("checked_at"):
                last_checked = datetime.fromisoformat(history[0]["checked_at"])
                now = datetime.now(timezone.utc)
                delta = now - last_checked
                
                if freq == "hourly" and delta < timedelta(hours=1):
                    should_check = False
                elif (freq == "daily" or freq is None) and delta < timedelta(days=1):
                    should_check = False
                elif freq == "weekly" and delta < timedelta(weeks=1):
                    should_check = False
            
            if not should_check:
                continue

            try:
                from app.factories.scraper_factory import ScraperFactory

                scraper = ScraperFactory.create_scraper(product["url"])
                data = scraper.extract_product_data(product["url"])
                old_price = product.get("current_price")
                if data.current_price is None or old_price == data.current_price:
                    continue
                # Fiyat geçmişine ekle
                supabase.table("price_history").insert(
                    {
                        "product_id": product["id"],
                        "price": data.current_price,
                    }
                ).execute()
                # Ürünün current_price'ını güncelle
                supabase.table("products").update(
                    {"current_price": data.current_price}
                ).eq("id", product["id"]).execute()
                
                # Sadece TRY olarak bas, Windows konsolu ₺ karakterinde çökebilir
                print(f"Updated {product['name']}: {data.current_price} TRY")
                
                # Check for notification target
                price_monitor.notify(product, old_price, data.current_price)
                
            except Exception as e:
                # Olası unicode karakterleri hatasını engellemek için encode
                print(f"Failed to check product ID {product.get('id')}: {e}".encode("cp1254", errors="ignore").decode("cp1254"))
    except Exception as e:
        print(f"Scheduler error: {e}".encode("cp1254", errors="ignore").decode("cp1254"))


def start_scheduler():
    scheduler = BackgroundScheduler()
    # Runs immediately on startup, then every hour
    scheduler.add_job(check_prices, IntervalTrigger(hours=1), next_run_time=datetime.now())
    scheduler.start()
    print("Scheduler started.")
    return scheduler
