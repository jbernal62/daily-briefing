"""HackerNews API — top stories."""

import httpx


async def fetch_hackernews(max_items: int = 10) -> list[dict]:
    """Fetch top stories from HackerNews."""
    items = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
            resp.raise_for_status()
            story_ids = resp.json()[:max_items]

            for sid in story_ids:
                r = await client.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
                r.raise_for_status()
                story = r.json()
                if story and story.get("title"):
                    items.append({
                        "category": "tech",
                        "title": story["title"],
                        "description": f"Score: {story.get('score', 0)} | Comments: {story.get('descendants', 0)}",
                        "source": "HackerNews",
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "published": "",
                    })
        except httpx.HTTPError:
            pass
    return items
