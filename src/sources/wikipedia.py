"""Wikipedia — random interesting articles and on-this-day facts."""

import httpx
from datetime import datetime, timezone


async def fetch_wikipedia() -> list[dict]:
    """Fetch interesting knowledge items from Wikipedia REST API."""
    items = []
    now = datetime.now(timezone.utc)
    headers = {
        "User-Agent": "Mozilla/5.0 (DailyBriefingBot/1.0; personal project)",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=15, headers=headers) as client:
        # On This Day events
        try:
            month, day = now.month, now.day
            url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
            resp = await client.get(url)
            resp.raise_for_status()
            events = resp.json().get("events", [])
            for event in events[:3]:
                pages = event.get("pages", [])
                page_url = pages[0].get("content_urls", {}).get("desktop", {}).get("page", "") if pages else ""
                items.append({
                    "category": "knowledge",
                    "title": f"On This Day ({event.get('year', '')}): {event.get('text', '')[:100]}",
                    "description": event.get("text", "")[:300],
                    "source": "Wikipedia — On This Day",
                    "url": page_url,
                    "published": now.isoformat(),
                })
        except httpx.HTTPError:
            pass

        # Random featured article summary
        try:
            resp = await client.get("https://en.wikipedia.org/api/rest_v1/page/random/summary")
            resp.raise_for_status()
            data = resp.json()
            items.append({
                "category": "knowledge",
                "title": data.get("title", "Interesting Fact"),
                "description": data.get("extract", "")[:300],
                "source": "Wikipedia",
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "published": now.isoformat(),
            })
        except httpx.HTTPError:
            pass

    return items
