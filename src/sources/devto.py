"""Dev.to API — trending developer articles."""

import httpx


async def fetch_devto(tags: list[str], max_per_tag: int = 3) -> list[dict]:
    """Fetch trending articles from Dev.to for each tag."""
    items = []
    async with httpx.AsyncClient(timeout=15) as client:
        for tag in tags:
            try:
                resp = await client.get(
                    "https://dev.to/api/articles",
                    params={"tag": tag, "top": 1, "per_page": max_per_tag},
                )
                resp.raise_for_status()
                for article in resp.json():
                    items.append({
                        "category": "tech",
                        "title": article["title"],
                        "description": article.get("description", ""),
                        "source": f"Dev.to — {article.get('user', {}).get('name', 'Unknown')}",
                        "url": article.get("url", ""),
                        "published": article.get("published_at", ""),
                    })
            except httpx.HTTPError:
                continue
    return items
