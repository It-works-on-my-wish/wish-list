import json
import os

from app.scrapers.scraper_strategy import (
    ScrapedProductData,
    ScraperStrategy,
    ScrapingError,
)
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests
from groq import Groq


class LLMScraper(ScraperStrategy):
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def extract_product_data(self, url: str) -> ScrapedProductData:
        try:
            response = curl_requests.get(
                url, headers=self.HEADERS, impersonate="chrome120", timeout=15
            )
            response.raise_for_status()
        except Exception as e:
            raise ScrapingError(f"Failed to fetch page: {e}")

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(
            ["script", "style", "nav", "footer", "header", "svg", "iframe"]
        ):
            tag.decompose()
        clean_text = soup.get_text(separator=" ", strip=True)[:3000]

        prompt = f"""Extract product info from this webpage text and return ONLY a JSON object with no extra text:
{{"title": "...", "price": 0.0, "currency": "TRY", "image_url": "..."}}

Webpage text:
{clean_text}"""

        try:
            result = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
            )
            text = result.choices[0].message.content.strip()
            print("LLM TEXT:", text)
            start = text.find("{")
            end = text.rfind("}") + 1
            data = json.loads(text[start:end])
        except Exception as e:
            raise ScrapingError(f"LLM parsing failed: {e}")

        return ScrapedProductData(
            title=data.get("title", "Unknown Product"),
            current_price=self._parse_price(data.get("price")),
            currency=data.get("currency", "TRY"),
            image_url=data.get("image_url"),
            source_domain=url.split("/")[2],
        )

    @staticmethod
    def _parse_price(price) -> float | None:
        if price is None:
            return None
        try:
            # LLM bazen string bazen float döndürür
            price_str = str(price).strip()
            # Binlik ayracı olan virgülü kaldır
            price_str = price_str.replace(",", "")
            return float(price_str)
        except (ValueError, TypeError):
            return None
