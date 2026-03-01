"""GNews API — global news headlines."""

import httpx


async def fetch_news(api_key: str, topics: list[str], max_per_topic: int = 5) -> list[dict]:
    """Fetch top headlines from GNews for each topic."""
    items = []
    async with httpx.AsyncClient(timeout=15) as client:
        for topic in topics:
            url = "https://gnews.io/api/v4/top-headlines"
            params = {
                "category": topic,
                "lang": "en",
                "max": max_per_topic,
                "apikey": api_key,
            }
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                for article in resp.json().get("articles", []):
                    items.append({
                        "category": "news",
                        "title": article["title"],
                        "description": article.get("description", ""),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "url": article.get("url", ""),
                        "published": article.get("publishedAt", ""),
                    })
            except httpx.HTTPError:
                continue
    return items
