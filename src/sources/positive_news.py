"""Positive news — good news from around the world."""

import httpx


async def fetch_positive_news(api_key: str, max_items: int = 5) -> list[dict]:
    """Fetch positive/uplifting news via GNews search."""
    items = []
    queries = ["good news today", "positive breakthrough", "innovation success"]

    async with httpx.AsyncClient(timeout=15) as client:
        for query in queries[:1]:  # One query to save API calls
            try:
                resp = await client.get(
                    "https://gnews.io/api/v4/search",
                    params={
                        "q": query,
                        "lang": "en",
                        "max": max_items,
                        "apikey": api_key,
                    },
                )
                resp.raise_for_status()
                for article in resp.json().get("articles", []):
                    items.append({
                        "category": "positive",
                        "title": article["title"],
                        "description": article.get("description", "")[:200],
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "url": article.get("url", ""),
                        "published": article.get("publishedAt", ""),
                    })
            except httpx.HTTPError:
                continue
    return items
