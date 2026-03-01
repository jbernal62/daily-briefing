"""Cloud innovations — latest from AWS, Azure, GCP via HN and Dev.to."""

import httpx


async def fetch_cloud_news(tags: list[str]) -> list[dict]:
    """Fetch latest cloud innovations from HN Algolia and Dev.to."""
    items = []

    async with httpx.AsyncClient(timeout=15) as client:
        # HN Algolia search for cloud news
        for tag in tags:
            try:
                resp = await client.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={"query": tag, "tags": "story", "hitsPerPage": 3},
                )
                resp.raise_for_status()
                for hit in resp.json().get("hits", []):
                    if hit.get("title"):
                        items.append({
                            "category": "cloud",
                            "title": hit["title"],
                            "description": f"Points: {hit.get('points', 0)} | Comments: {hit.get('num_comments', 0)}",
                            "source": f"HackerNews — {tag}",
                            "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"),
                            "published": hit.get("created_at", ""),
                        })
            except httpx.HTTPError:
                continue

        # Dev.to for cloud articles
        for tag in ["aws", "azure", "gcp"]:
            try:
                resp = await client.get(
                    "https://dev.to/api/articles",
                    params={"tag": tag, "top": 7, "per_page": 2},
                )
                resp.raise_for_status()
                for article in resp.json():
                    items.append({
                        "category": "cloud",
                        "title": article["title"],
                        "description": article.get("description", "")[:200],
                        "source": f"Dev.to — {article.get('user', {}).get('name', 'Unknown')}",
                        "url": article.get("url", ""),
                        "published": article.get("published_at", ""),
                    })
            except httpx.HTTPError:
                continue

    return items
