from app.database.supabase_client import supabase
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


def check_prices():
    print("Checking prices...")
    try:
        products = (
            supabase.table("products").select("*").eq("auto_track", True).execute().data
        )
        for product in products:
            if not product.get("url"):
                continue
            try:
                from app.factories.scraper_factory import ScraperFactory

                scraper = ScraperFactory.create_scraper(product["url"])
                data = scraper.extract_product_data(product["url"])
                if data.current_price is None:
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
                print(f"Updated {product['name']}: ₺{data.current_price}")
            except Exception as e:
                print(f"Failed to check {product['name']}: {e}")
    except Exception as e:
        print(f"Scheduler error: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler()
    # Her saat başı çalışır, check_frequency'ye göre filtreleme check_prices içinde yapılabilir
    scheduler.add_job(check_prices, IntervalTrigger(hours=1))
    scheduler.start()
    print("Scheduler started.")
    return scheduler
