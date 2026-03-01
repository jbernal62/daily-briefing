"""DutchNews.nl — top news from the Netherlands."""

import httpx


async def fetch_dutch_news(max_items: int = 3) -> list[dict]:
    """Fetch top Dutch news headlines from DutchNews.nl RSS feed."""
    items = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # DutchNews.nl RSS feed
            resp = await client.get("https://www.dutchnews.nl/feed/")
            resp.raise_for_status()
            text = resp.text

            # Simple XML parsing for RSS items
            import re
            item_blocks = re.findall(r"<item>(.*?)</item>", text, re.DOTALL)
            for block in item_blocks[:max_items]:
                title = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", block)
                if not title:
                    title = re.search(r"<title>(.*?)</title>", block)
                desc = re.search(r"<description><!\[CDATA\[(.*?)\]\]></description>", block, re.DOTALL)
                if not desc:
                    desc = re.search(r"<description>(.*?)</description>", block, re.DOTALL)
                link = re.search(r"<link>(.*?)</link>", block)

                # Strip HTML from description
                desc_text = desc.group(1) if desc else ""
                desc_text = re.sub(r"<[^>]+>", "", desc_text).strip()[:200]

                items.append({
                    "category": "dutch_news",
                    "title": title.group(1) if title else "Dutch News",
                    "description": desc_text,
                    "source": "DutchNews.nl",
                    "url": link.group(1) if link else "",
                    "published": "",
                })
        except httpx.HTTPError:
            pass
    return items
